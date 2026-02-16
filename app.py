"""📱 Prediksi Harga iPhone — Main App Entry Point."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import warnings

from data_loader import load_data
from models import build_product_models, train_global_models, evaluate_per_product
from tabs import tab_evaluasi, tab_tren, tab_heatmap, tab_versus, tab_analisis, tab_data

warnings.filterwarnings("ignore")

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Prediksi Harga iPhone", page_icon="📱", layout="wide")
st.title("📱 Prediksi Harga iPhone")
st.caption("Prediksi harga per produk spesifik (Kondisi + Generasi + Variant + Storage)")

# ── Load Data & Build Models ─────────────────────────────────────────────────
df = load_data()
min_date = df["Bulan"].min()
max_bulan_index = df["Bulan_Index"].max()

product_models = build_product_models(df)
global_results, best_global_model, global_features = train_global_models(df)
eval_df = evaluate_per_product(df)

# ── Sidebar: Filter untuk Prediksi ──────────────────────────────────────────
st.sidebar.header("🔍 Filter Prediksi Harga")

kondisi_options = sorted(df["Kondisi"].unique())
kondisi = st.sidebar.selectbox("Kondisi", kondisi_options, index=kondisi_options.index("New"))

gen_for_kondisi = sorted(
    df[df["Kondisi"] == kondisi]["Generasi"].unique(),
    key=lambda x: int(x.split()[-1]),
)
generasi = st.sidebar.selectbox("Generasi", gen_for_kondisi, index=len(gen_for_kondisi) - 1)

available_variants = sorted(
    df[(df["Generasi"] == generasi) & (df["Kondisi"] == kondisi)]["Variant_Normalized"].unique()
)
if not available_variants:
    available_variants = sorted(df[df["Generasi"] == generasi]["Variant_Normalized"].unique())
variant = st.sidebar.selectbox("Variant", available_variants)

available_storage = sorted(
    df[(df["Generasi"] == generasi) & (df["Variant_Normalized"] == variant) & (df["Kondisi"] == kondisi)]["Storage"].unique()
)
if not available_storage:
    available_storage = sorted(
        df[(df["Generasi"] == generasi) & (df["Variant_Normalized"] == variant)]["Storage"].unique()
    )
if not available_storage:
    available_storage = [128, 256, 512]
storage = st.sidebar.selectbox("Storage (GB)", available_storage)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Bulan Prediksi")
bulan_pred = st.sidebar.slider("Bulan", 1, 12, 3)
tahun_pred = st.sidebar.number_input("Tahun", min_value=2025, max_value=2030, value=2026)

# ── Prediksi Per-Produk ─────────────────────────────────────────────────────
pred_date = pd.Timestamp(year=tahun_pred, month=bulan_pred, day=1)
bulan_index = int(round((pred_date - min_date).days / 30))

product_key = f"{kondisi}|{generasi}|{variant}|{storage}"
product_history = df[df["Product_Key"] == product_key].sort_values("Bulan")

if product_key in product_models:
    pm = product_models[product_key]
    if pm["model"] is not None:
        predicted_price = pm["model"].predict([[bulan_index]])[0]
        pred_method = "Per-Produk (Linear Trend)"
        slope_per_month = pm["slope"]
    else:
        predicted_price = pm["last_price"]
        pred_method = "Per-Produk (1 data point)"
        slope_per_month = 0
    predicted_price = max(predicted_price, 0)
    has_product_data = True
else:
    has_product_data = False
    pred_method = "Global Model (produk tidak ditemukan)"
    vt_map = {"Mini": 1, "e": 2, "Basic": 3, "Air": 4, "Plus": 5, "Pro": 6, "Pro Max": 7}
    kt_map = {"BC": 1, "Second": 2, "New": 3}
    depr_map = {"New": 0, "Second": -1, "BC": -2}
    gen_num = int(generasi.split()[-1])
    max_gen = df["Gen_Num"].max()
    gen_age = max_gen - gen_num
    inp = np.array([[
        kt_map[kondisi], gen_num, vt_map.get(variant, 3), np.log2(storage),
        bulan_index, kt_map[kondisi] * bulan_index, depr_map[kondisi] * bulan_index,
        gen_age, gen_age * bulan_index,
    ]])
    predicted_price = max(global_results[best_global_model]["model"].predict(inp)[0], 0)
    slope_per_month = 0

# ── Main Content ─────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("💰 Hasil Prediksi")
    st.markdown(f"""
    | Parameter | Nilai |
    |-----------|-------|
    | **Kondisi** | {kondisi} |
    | **Generasi** | {generasi} |
    | **Variant** | {variant} |
    | **Storage** | {storage} GB |
    | **Bulan Prediksi** | {bulan_pred}/{tahun_pred} |
    | **Metode** | {pred_method} |
    """)
    if has_product_data:
        if slope_per_month < -50000:
            st.info(f"📉 Tren: harga turun ~Rp {abs(slope_per_month):,.0f}/bulan")
        elif slope_per_month > 50000:
            st.info(f"📈 Tren: harga naik ~Rp {slope_per_month:,.0f}/bulan")
        else:
            st.info("➡️ Harga relatif stabil")
        if bulan_index > max_bulan_index:
            months_beyond = bulan_index - max_bulan_index
            st.warning(f"⚠️ Prediksi {months_beyond} bulan di luar data terakhir")
    else:
        st.warning("⚠️ Kombinasi produk ini tidak ada di dataset — menggunakan model global")

with col2:
    st.metric(label="Harga Prediksi", value=f"Rp {predicted_price:,.0f}")
    actual_row = df[(df["Product_Key"] == product_key) & (df["Bulan"] == pred_date)]
    if not actual_row.empty:
        actual_price = actual_row["Harga"].mean()
        diff = predicted_price - actual_price
        st.metric(
            label="Harga Aktual", value=f"Rp {actual_price:,.0f}",
            delta=f"Rp {diff:,.0f} ({diff / actual_price * 100:.1f}%)",
        )

with col3:
    if not eval_df.empty:
        st.metric("MAPE Per-Produk", f"{eval_df['APE'].mean():.2f}%")
        st.metric("MAE Per-Produk", f"Rp {eval_df['Error'].abs().mean():,.0f}")
    if has_product_data and len(product_history) > 0:
        st.metric("Data Points", f"{len(product_history)} bulan")

# ── Product Price History Chart ──────────────────────────────────────────────
if has_product_data and len(product_history) >= 2:
    st.subheader(f"📈 Riwayat & Prediksi: {kondisi} {generasi} {variant} {storage}GB")
    pm_info = product_models[product_key]
    hist_dates = product_history["Bulan"].tolist()
    hist_prices = product_history["Harga"].tolist()

    all_indices = list(pm_info["indices"])
    last_idx = int(pm_info["indices"][-1])
    for i in range(1, 7):
        all_indices.append(last_idx + i)

    pred_dates = [min_date + pd.DateOffset(months=int(idx)) for idx in all_indices]
    if pm_info["model"] is not None:
        pred_prices = pm_info["model"].predict(np.array(all_indices).reshape(-1, 1)).tolist()
        pred_prices = [max(p, 0) for p in pred_prices]
    else:
        pred_prices = [pm_info["last_price"]] * len(all_indices)

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(
        x=hist_dates, y=hist_prices, mode="lines+markers", name="Harga Aktual",
        line=dict(color="#00CC96", width=3), marker=dict(size=10),
    ))
    fig_hist.add_trace(go.Scatter(
        x=pred_dates, y=pred_prices, mode="lines", name="Tren Prediksi",
        line=dict(color="#EF553B", width=2, dash="dash"),
    ))
    fig_hist.add_trace(go.Scatter(
        x=[pred_date], y=[predicted_price], mode="markers",
        name=f"Prediksi {bulan_pred}/{tahun_pred}",
        marker=dict(size=15, color="#AB63FA", symbol="star"),
    ))
    fig_hist.update_layout(
        title=f"Tren Harga: {kondisi} {generasi} {variant} {storage}GB",
        xaxis_title="Bulan", yaxis_title="Harga (Rp)", hovermode="x unified", height=400,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Evaluasi Model", "📈 Tren Harga", "⚔️ Versus",
    "🗺️ Heatmap", "🔍 Analisis Data", "📋 Data Lengkap",
])

with tab1:
    tab_evaluasi.render(eval_df, global_results)

with tab2:
    tab_tren.render(df, kondisi, generasi, variant, kondisi_options, product_models)

with tab3:
    tab_versus.render(df)

with tab4:
    tab_heatmap.render(df, kondisi_options)

with tab5:
    tab_analisis.render(df)

with tab6:
    tab_data.render(df)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
if not eval_df.empty:
    st.markdown(
        f"📊 **Model Per-Produk** — MAPE: {eval_df['APE'].mean():.2f}% | "
        f"MAE: Rp {eval_df['Error'].abs().mean():,.0f} | "
        f"Total Produk: {len(product_models)} | "
        f"Global Fallback: {best_global_model} (R²: {global_results[best_global_model]['r2']:.4f})"
    )
