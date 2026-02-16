"""ML models: per-product linear and global ensemble models."""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor


@st.cache_resource
def build_product_models(_df):
    """Build a linear trend model for each unique product (Kondisi+Generasi+Variant+Storage)."""
    product_models = {}

    for pk, grp in _df.groupby("Product_Key"):
        grp = grp.sort_values("Bulan")
        X_t = grp["Bulan_Index"].values.reshape(-1, 1)
        y_t = grp["Harga"].values

        if len(grp) >= 2:
            lr = LinearRegression()
            lr.fit(X_t, y_t)
            product_models[pk] = {
                "model": lr,
                "slope": lr.coef_[0],
                "intercept": lr.intercept_,
                "n_points": len(grp),
                "last_price": y_t[-1],
                "first_price": y_t[0],
                "last_index": X_t[-1, 0],
                "prices": y_t,
                "indices": X_t.ravel(),
                "r2": r2_score(y_t, lr.predict(X_t)) if len(grp) > 2 else 1.0,
            }
        else:
            product_models[pk] = {
                "model": None,
                "slope": 0,
                "intercept": y_t[0],
                "n_points": 1,
                "last_price": y_t[0],
                "first_price": y_t[0],
                "last_index": X_t[0, 0],
                "prices": y_t,
                "indices": X_t.ravel(),
                "r2": 1.0,
            }

    return product_models


@st.cache_resource
def train_global_models(_df):
    """Train global ML models (XGBoost, RF, GB) as fallback."""
    df2 = _df.copy()
    df2["Storage_Log"] = np.log2(df2["Storage"])
    df2["Kondisi_x_Bulan"] = df2["Kondisi_Tier"] * df2["Bulan_Index"]
    depr = {"New": 0, "Second": -1, "BC": -2}
    df2["Depr_Factor"] = df2["Kondisi"].map(depr)
    df2["Depr_x_Bulan"] = df2["Depr_Factor"] * df2["Bulan_Index"]
    max_gen = df2["Gen_Num"].max()
    df2["Gen_Age"] = max_gen - df2["Gen_Num"]
    df2["Age_x_Bulan"] = df2["Gen_Age"] * df2["Bulan_Index"]

    features = [
        "Kondisi_Tier", "Gen_Num", "Variant_Tier", "Storage_Log",
        "Bulan_Index", "Kondisi_x_Bulan", "Depr_x_Bulan", "Gen_Age", "Age_x_Bulan",
    ]
    X = df2[features].values
    y = df2["Harga"].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "XGBoost": XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42
        ),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred) * 100
        r2 = r2_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X, y, cv=3, scoring="r2")
        results[name] = {
            "model": model, "mae": mae, "mape": mape, "r2": r2,
            "cv_r2_mean": cv_scores.mean(), "cv_r2_std": cv_scores.std(),
            "y_test": y_test, "y_pred": y_pred,
        }

    best_name = min(results, key=lambda k: results[k]["mape"])
    return results, best_name, features


@st.cache_data
def evaluate_per_product(_df):
    """Leave-last-out evaluation per product."""
    errors = []
    for pk, grp in _df.groupby("Product_Key"):
        grp = grp.sort_values("Bulan")
        if len(grp) < 3:
            continue
        X_t = grp["Bulan_Index"].values
        y_t = grp["Harga"].values
        lr = LinearRegression()
        lr.fit(X_t[:-1].reshape(-1, 1), y_t[:-1])
        pred = lr.predict([[X_t[-1]]])[0]
        actual = y_t[-1]
        errors.append({
            "Product": pk, "Actual": actual, "Predicted": pred,
            "Error": pred - actual, "APE": abs(pred - actual) / actual * 100,
        })
    return pd.DataFrame(errors)
