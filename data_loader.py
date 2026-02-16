"""Data loading and preprocessing module."""

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    """Load and preprocess the iPhone price dataset."""
    df = pd.read_csv("DatasetHargaIphone.csv")

    # Fix Storage 1000 → 1024
    df["Storage"] = df["Storage"].replace(1000, 1024)

    # Normalize variant: color variants → base variant
    variant_map = {
        "Midnight": "Basic",
        "Starlight": "Basic",
        "Sage": "Basic",
        "Pro Silver": "Pro",
        "Pro Max Silver": "Pro Max",
    }
    df["Variant_Original"] = df["Variant"]
    df["Variant_Normalized"] = df["Variant"].replace(variant_map)

    # Parse date
    df["Bulan"] = pd.to_datetime(df["Bulan"])
    df["Tahun"] = df["Bulan"].dt.year
    df["Bulan_Num"] = df["Bulan"].dt.month

    # Generasi number
    df["Gen_Num"] = df["Generasi"].str.extract(r"(\d+)").astype(int)

    # Variant tier
    vt = {"Mini": 1, "e": 2, "Basic": 3, "Air": 4, "Plus": 5, "Pro": 6, "Pro Max": 7}
    df["Variant_Tier"] = df["Variant_Normalized"].map(vt).fillna(3)

    # Kondisi tier
    kt = {"BC": 1, "Second": 2, "New": 3}
    df["Kondisi_Tier"] = df["Kondisi"].map(kt)

    # Time index (months since first date)
    min_date = df["Bulan"].min()
    df["Bulan_Index"] = ((df["Bulan"] - min_date).dt.days / 30).round().astype(int)

    # Product key
    df["Product_Key"] = (
        df["Kondisi"] + "|" + df["Generasi"] + "|" +
        df["Variant_Normalized"] + "|" + df["Storage"].astype(str)
    )

    return df
