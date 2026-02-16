"""Tab Heatmap — comprehensive heatmap visualizations."""

import streamlit as st
import pandas as pd
import plotly.express as px

V_ORDER = ["Mini", "e", "Basic", "Air", "Plus", "Pro", "Pro Max"]


def _sort_gen(index):
    return sorted(index, key=lambda x: int(x.split()[-1]))


def render(df, kondisi_options):
    st.subheader("🗺️ Heatmap Harga iPhone")
    st.caption("Visualisasi harga dalam bentuk heatmap dengan filter lengkap")

    # ── Filter controls ──
    hm_col1, hm_col2, hm_col3 = st.columns(3)
    with hm_col1:
        hm_kondisi = st.selectbox("Kondisi", kondisi_options, key="hm_kondisi")
    with hm_col2:
        bulan_options = sorted(df["Bulan"].unique())
        bulan_labels = [pd.Timestamp(b).strftime("%b %Y") for b in bulan_options]
        hm_bulan_label = st.selectbox("Bulan", bulan_labels, index=len(bulan_labels) - 1, key="hm_bulan")
        hm_bulan = bulan_options[bulan_labels.index(hm_bulan_label)]
    with hm_col3:
        hm_storage_options = ["Semua"] + [str(s) for s in sorted(df["Storage"].unique())]
        hm_storage = st.selectbox("Storage (GB)", hm_storage_options, key="hm_storage")

    # Filter data
    hm_df = df[(df["Kondisi"] == hm_kondisi) & (df["Bulan"] == hm_bulan)].copy()
    if hm_storage != "Semua":
        hm_df = hm_df[hm_df["Storage"] == int(hm_storage)]

    if hm_df.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
        return

    # ── Heatmap 1: Generasi × Variant ──
    st.subheader("Generasi × Variant")
    pivot1 = hm_df.pivot_table(values="Harga", index="Generasi", columns="Variant_Normalized", aggfunc="mean")
    pivot1 = pivot1[[c for c in V_ORDER if c in pivot1.columns]]
    pivot1 = pivot1.reindex(_sort_gen(pivot1.index))
    fig1 = px.imshow(
        pivot1 / 1e6, text_auto=".1f",
        labels=dict(x="Variant", y="Generasi", color="Harga (Juta Rp)"),
        title=f"Harga {hm_kondisi} — {hm_bulan_label}"
              + (f" — {hm_storage}GB" if hm_storage != "Semua" else " — Rata-rata Semua Storage"),
        color_continuous_scale="YlOrRd", aspect="auto",
    )
    fig1.update_layout(height=450)
    st.plotly_chart(fig1, use_container_width=True)

    # ── Heatmap 2: Generasi × Storage ──
    st.subheader("Generasi × Storage")
    pivot2 = hm_df.pivot_table(values="Harga", index="Generasi", columns="Storage", aggfunc="mean")
    pivot2 = pivot2[sorted(pivot2.columns)]
    pivot2.columns = [f"{int(c)} GB" for c in pivot2.columns]
    pivot2 = pivot2.reindex(_sort_gen(pivot2.index))
    fig2 = px.imshow(
        pivot2 / 1e6, text_auto=".1f",
        labels=dict(x="Storage", y="Generasi", color="Harga (Juta Rp)"),
        title=f"Harga {hm_kondisi} per Storage — {hm_bulan_label}",
        color_continuous_scale="Blues", aspect="auto",
    )
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, use_container_width=True)

    # ── Heatmap 3: Variant × Storage ──
    st.subheader("Variant × Storage")
    hm_gen_options = _sort_gen(hm_df["Generasi"].unique())
    hm_gen_sel = st.selectbox("Filter Generasi", ["Semua"] + hm_gen_options, key="hm_gen_sel")
    hm_df3 = hm_df if hm_gen_sel == "Semua" else hm_df[hm_df["Generasi"] == hm_gen_sel]

    if not hm_df3.empty:
        pivot3 = hm_df3.pivot_table(values="Harga", index="Variant_Normalized", columns="Storage", aggfunc="mean")
        pivot3 = pivot3[sorted(pivot3.columns)]
        pivot3.columns = [f"{int(c)} GB" for c in pivot3.columns]
        pivot3 = pivot3.reindex([v for v in V_ORDER if v in pivot3.index])
        title3 = f"Harga {hm_kondisi} per Variant × Storage — {hm_bulan_label}"
        if hm_gen_sel != "Semua":
            title3 += f" — {hm_gen_sel}"
        fig3 = px.imshow(
            pivot3 / 1e6, text_auto=".1f",
            labels=dict(x="Storage", y="Variant", color="Harga (Juta Rp)"),
            title=title3, color_continuous_scale="Viridis", aspect="auto",
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    # ── Heatmap 4: Perbandingan antar Kondisi ──
    st.subheader("Perbandingan Harga antar Kondisi")
    st.caption("Heatmap rata-rata harga per Kondisi × Generasi (semua variant & storage)")
    hm_df4 = df[df["Bulan"] == hm_bulan].copy()
    if hm_storage != "Semua":
        hm_df4 = hm_df4[hm_df4["Storage"] == int(hm_storage)]
    if not hm_df4.empty:
        pivot4 = hm_df4.pivot_table(values="Harga", index="Generasi", columns="Kondisi", aggfunc="mean")
        kondisi_order = ["BC", "Second", "New"]
        pivot4 = pivot4[[c for c in kondisi_order if c in pivot4.columns]]
        pivot4 = pivot4.reindex(_sort_gen(pivot4.index))
        fig4 = px.imshow(
            pivot4 / 1e6, text_auto=".1f",
            labels=dict(x="Kondisi", y="Generasi", color="Harga (Juta Rp)"),
            title=f"Perbandingan Harga antar Kondisi — {hm_bulan_label}"
                  + (f" — {hm_storage}GB" if hm_storage != "Semua" else ""),
            color_continuous_scale="RdYlGn", aspect="auto",
        )
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Heatmap 5: Perubahan Harga antar Bulan ──
    st.subheader("Perubahan Harga antar Bulan (Δ)")
    st.caption("Selisih harga bulan terpilih vs bulan sebelumnya")
    bulan_idx = bulan_labels.index(hm_bulan_label)
    if bulan_idx == 0:
        st.info("Bulan pertama dipilih — tidak ada bulan sebelumnya untuk perbandingan.")
        return

    prev_bulan = bulan_options[bulan_idx - 1]
    prev_label = bulan_labels[bulan_idx - 1]
    cur = df[(df["Kondisi"] == hm_kondisi) & (df["Bulan"] == hm_bulan)].copy()
    prev = df[(df["Kondisi"] == hm_kondisi) & (df["Bulan"] == prev_bulan)].copy()
    if hm_storage != "Semua":
        cur = cur[cur["Storage"] == int(hm_storage)]
        prev = prev[prev["Storage"] == int(hm_storage)]

    merge_cols = ["Generasi", "Variant_Normalized", "Storage"]
    merged = cur.merge(prev, on=merge_cols, suffixes=("_cur", "_prev"))
    if merged.empty:
        st.info("Tidak ada data perbandingan untuk filter ini.")
        return

    merged["Delta"] = merged["Harga_cur"] - merged["Harga_prev"]
    pivot5 = merged.pivot_table(values="Delta", index="Generasi", columns="Variant_Normalized", aggfunc="mean")
    pivot5 = pivot5[[c for c in V_ORDER if c in pivot5.columns]]
    pivot5 = pivot5.reindex(_sort_gen(pivot5.index))
    fig5 = px.imshow(
        pivot5 / 1e6, text_auto=".2f",
        labels=dict(x="Variant", y="Generasi", color="Δ Harga (Juta Rp)"),
        title=f"Perubahan Harga {hm_kondisi}: {prev_label} → {hm_bulan_label}",
        color_continuous_scale="RdBu_r", aspect="auto", color_continuous_midpoint=0,
    )
    fig5.update_layout(height=450)
    st.plotly_chart(fig5, use_container_width=True)
