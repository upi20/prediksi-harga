"""Tab Versus — dynamic comparison of actual price trends across products."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _product_label(kondisi, generasi, variant, storage):
    return f"{kondisi} | {generasi} {variant} {storage}GB"


def render(df):
    st.subheader("⚔️ Versus — Perbandingan Harga Dinamis")
    st.caption("Bandingkan tren harga aktual antar produk (bukan prediksi). Tambahkan sebanyak mungkin produk untuk dibandingkan.")

    # ── How many products to compare ──
    n_compare = st.slider("Jumlah produk yang dibandingkan", min_value=2, max_value=10, value=3, key="vs_n")

    kondisi_opts = sorted(df["Kondisi"].unique())
    gen_opts = sorted(df["Generasi"].unique(), key=lambda x: int(x.split()[-1]))

    selections = []

    st.markdown("---")
    cols_per_row = min(n_compare, 5)

    for row_start in range(0, n_compare, cols_per_row):
        cols = st.columns(min(cols_per_row, n_compare - row_start))
        for j, col in enumerate(cols):
            i = row_start + j
            with col:
                st.markdown(f"**Produk {i + 1}**")

                k = st.selectbox("Kondisi", kondisi_opts, key=f"vs_k_{i}",
                                 index=min(i, len(kondisi_opts) - 1) % len(kondisi_opts))

                gens_avail = sorted(
                    df[df["Kondisi"] == k]["Generasi"].unique(),
                    key=lambda x: int(x.split()[-1])
                )
                default_gen_idx = min(i, len(gens_avail) - 1)
                g = st.selectbox("Generasi", gens_avail, key=f"vs_g_{i}", index=default_gen_idx)

                vars_avail = sorted(
                    df[(df["Kondisi"] == k) & (df["Generasi"] == g)]["Variant_Normalized"].unique()
                )
                v = st.selectbox("Variant", vars_avail, key=f"vs_v_{i}")

                stors_avail = sorted(
                    df[(df["Kondisi"] == k) & (df["Generasi"] == g) &
                       (df["Variant_Normalized"] == v)]["Storage"].unique()
                )
                s = st.selectbox("Storage (GB)", stors_avail, key=f"vs_s_{i}")

                selections.append({"Kondisi": k, "Generasi": g, "Variant": v, "Storage": s})

    if not selections:
        return

    st.markdown("---")

    # ── Gather data for all selections ──
    all_data = []
    labels = []
    for sel in selections:
        label = _product_label(sel["Kondisi"], sel["Generasi"], sel["Variant"], sel["Storage"])
        mask = (
            (df["Kondisi"] == sel["Kondisi"]) &
            (df["Generasi"] == sel["Generasi"]) &
            (df["Variant_Normalized"] == sel["Variant"]) &
            (df["Storage"] == sel["Storage"])
        )
        prod_df = df[mask][["Bulan", "Harga"]].copy()
        prod_df["Produk"] = label
        all_data.append(prod_df)
        labels.append(label)

    if not all_data:
        st.warning("Tidak ada data untuk produk yang dipilih.")
        return

    compare_df = pd.concat(all_data, ignore_index=True).sort_values("Bulan")

    # Check for duplicates (same product selected twice)
    unique_labels = list(dict.fromkeys(labels))

    # ── 1. Line Chart: Tren Harga ──
    st.subheader("📈 Tren Harga — Perbandingan")
    fig_line = px.line(
        compare_df, x="Bulan", y="Harga", color="Produk",
        title="Perbandingan Tren Harga Aktual",
        labels={"Harga": "Harga (Rp)", "Bulan": "Periode"},
        markers=True,
    )
    fig_line.update_layout(hovermode="x unified", height=500, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_line, use_container_width=True)

    # ── 2. Bar Chart: Harga Terbaru ──
    st.subheader("📊 Harga Terbaru (Bulan Terakhir)")
    latest_bulan = compare_df["Bulan"].max()
    latest_df = compare_df[compare_df["Bulan"] == latest_bulan].copy()

    if not latest_df.empty:
        latest_df = latest_df.sort_values("Harga", ascending=True)
        fig_bar = px.bar(
            latest_df, x="Harga", y="Produk", orientation="h",
            title=f"Harga per {pd.Timestamp(latest_bulan).strftime('%b %Y')}",
            labels={"Harga": "Harga (Rp)"}, color="Produk",
            text=latest_df["Harga"].apply(lambda x: f"Rp {x:,.0f}"),
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(height=max(300, 60 * len(latest_df)), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── 3. Perubahan Harga (Δ) per bulan ──
    st.subheader("📉 Perubahan Harga per Bulan (Δ)")
    delta_rows = []
    for label in unique_labels:
        prod = compare_df[compare_df["Produk"] == label].sort_values("Bulan")
        if len(prod) < 2:
            continue
        for idx in range(1, len(prod)):
            row_cur = prod.iloc[idx]
            row_prev = prod.iloc[idx - 1]
            delta = row_cur["Harga"] - row_prev["Harga"]
            delta_pct = delta / row_prev["Harga"] * 100
            delta_rows.append({
                "Produk": label,
                "Bulan": row_cur["Bulan"],
                "Δ Harga": delta,
                "Δ %": delta_pct,
            })

    if delta_rows:
        delta_df = pd.DataFrame(delta_rows)
        fig_delta = px.bar(
            delta_df, x="Bulan", y="Δ Harga", color="Produk",
            barmode="group", title="Perubahan Harga antar Bulan",
            labels={"Δ Harga": "Selisih Harga (Rp)", "Bulan": "Periode"},
        )
        fig_delta.update_layout(hovermode="x unified", height=450, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_delta, use_container_width=True)

        # Δ percentage chart
        fig_dpct = px.bar(
            delta_df, x="Bulan", y="Δ %", color="Produk",
            barmode="group", title="Perubahan Harga (%)",
            labels={"Δ %": "Perubahan (%)", "Bulan": "Periode"},
        )
        fig_dpct.update_layout(hovermode="x unified", height=400, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_dpct, use_container_width=True)

    # ── 4. Tabel Perbandingan Lengkap ──
    st.subheader("📋 Tabel Perbandingan Harga")

    bulan_sorted = sorted(compare_df["Bulan"].unique())
    table_data = {}
    for label in unique_labels:
        prod = compare_df[compare_df["Produk"] == label]
        prices = {}
        for _, row in prod.iterrows():
            bl = pd.Timestamp(row["Bulan"]).strftime("%b %Y")
            prices[bl] = row["Harga"]
        table_data[label] = prices

    # Build pivot table
    bulan_cols = [pd.Timestamp(b).strftime("%b %Y") for b in bulan_sorted]
    rows = []
    for label in unique_labels:
        row = {"Produk": label}
        prices_list = []
        for bc in bulan_cols:
            price = table_data[label].get(bc)
            if price is not None:
                row[bc] = f"Rp {price:,.0f}"
                prices_list.append(price)
            else:
                row[bc] = "—"

        # Summary columns
        if len(prices_list) >= 2:
            total_change = prices_list[-1] - prices_list[0]
            row["Total Δ"] = f"Rp {total_change:,.0f}"
            row["Δ %"] = f"{total_change / prices_list[0] * 100:.1f}%"
            row["Tren"] = "📉 Turun" if total_change < -50000 else (
                "📈 Naik" if total_change > 50000 else "➡️ Stabil"
            )
        else:
            row["Total Δ"] = "—"
            row["Δ %"] = "—"
            row["Tren"] = "—"

        rows.append(row)

    table_df = pd.DataFrame(rows)
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    # ── 5. Ranking ──
    st.subheader("🏆 Ranking Harga")
    rank_col1, rank_col2 = st.columns(2)

    with rank_col1:
        st.markdown("**Termurah → Termahal (bulan terakhir)**")
        if not latest_df.empty:
            ranking = latest_df.sort_values("Harga").reset_index(drop=True)
            for idx, row in ranking.iterrows():
                medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else f"#{idx + 1}"
                st.markdown(f"{medal} **{row['Produk']}** — Rp {row['Harga']:,.0f}")

    with rank_col2:
        st.markdown("**Penurunan Terbesar → Terkecil**")
        if delta_rows:
            total_deltas = []
            for label in unique_labels:
                prod = compare_df[compare_df["Produk"] == label].sort_values("Bulan")
                if len(prod) >= 2:
                    total_d = prod.iloc[-1]["Harga"] - prod.iloc[0]["Harga"]
                    total_deltas.append({"Produk": label, "Total Δ": total_d})
            if total_deltas:
                td_df = pd.DataFrame(total_deltas).sort_values("Total Δ")
                for idx, row in td_df.reset_index(drop=True).iterrows():
                    arrow = "📉" if row["Total Δ"] < 0 else ("📈" if row["Total Δ"] > 0 else "➡️")
                    st.markdown(f"{arrow} **{row['Produk']}** — Rp {row['Total Δ']:,.0f}")
