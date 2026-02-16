"""Tab Tren Harga — trend lines + summary table."""

import streamlit as st
import pandas as pd
import plotly.express as px


def render(df, kondisi, generasi, variant, kondisi_options, product_models):
    st.subheader("Tren Harga per Bulan")

    tcol1, tcol2, tcol3 = st.columns(3)
    with tcol1:
        trend_kondisi = st.multiselect("Filter Kondisi", df["Kondisi"].unique(), default=[kondisi])
    with tcol2:
        trend_gen = st.multiselect("Filter Generasi", sorted(df["Generasi"].unique()), default=[generasi])
    with tcol3:
        trend_variant = st.multiselect("Filter Variant", sorted(df["Variant_Normalized"].unique()), default=[variant])

    trend_df = df.copy()
    if trend_kondisi:
        trend_df = trend_df[trend_df["Kondisi"].isin(trend_kondisi)]
    if trend_gen:
        trend_df = trend_df[trend_df["Generasi"].isin(trend_gen)]
    if trend_variant:
        trend_df = trend_df[trend_df["Variant_Normalized"].isin(trend_variant)]

    if not trend_df.empty:
        trend_df["Label"] = (
            trend_df["Kondisi"] + " | " + trend_df["Generasi"] + " " +
            trend_df["Variant_Normalized"] + " " + trend_df["Storage"].astype(str) + "GB"
        )
        trend_agg = trend_df.groupby(["Bulan", "Label"])["Harga"].mean().reset_index()
        fig_trend = px.line(
            trend_agg, x="Bulan", y="Harga", color="Label",
            title="Tren Harga per Produk Spesifik",
            labels={"Harga": "Harga (Rp)", "Bulan": "Periode"}, markers=True,
        )
        fig_trend.update_layout(hovermode="x unified")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("Tidak ada data dengan filter yang dipilih.")

    st.subheader("Rangkuman Tren per Produk")
    trend_summary = []
    for pk, pm_data in product_models.items():
        if pm_data["n_points"] >= 2:
            parts = pk.split("|")
            trend_summary.append({
                "Kondisi": parts[0], "Generasi": parts[1], "Variant": parts[2],
                "Storage": int(parts[3]), "Data": pm_data["n_points"],
                "Harga Awal": f"Rp {pm_data['first_price']:,.0f}",
                "Harga Akhir": f"Rp {pm_data['last_price']:,.0f}",
                "Δ/Bulan": f"Rp {pm_data['slope']:,.0f}",
                "Tren": "📉 Turun" if pm_data["slope"] < -50000 else (
                    "📈 Naik" if pm_data["slope"] > 50000 else "➡️ Stabil"
                ),
            })

    if trend_summary:
        summary_df = pd.DataFrame(trend_summary).sort_values(
            ["Kondisi", "Generasi", "Variant", "Storage"]
        )
        sum_kondisi = st.selectbox("Filter Kondisi:", ["Semua"] + kondisi_options, key="sum_k")
        if sum_kondisi != "Semua":
            summary_df = summary_df[summary_df["Kondisi"] == sum_kondisi]
        st.dataframe(summary_df, use_container_width=True, hide_index=True, height=400)
