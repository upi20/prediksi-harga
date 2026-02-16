"""Tab Data Lengkap — full dataset browser with filters."""

import streamlit as st


def render(df):
    st.subheader("Dataset Lengkap")

    fcol1, fcol2, fcol3, fcol4 = st.columns(4)
    with fcol1:
        f_kondisi = st.multiselect("Kondisi", df["Kondisi"].unique(), key="f_kond")
    with fcol2:
        f_gen = st.multiselect("Generasi", sorted(df["Generasi"].unique()), key="f_gen")
    with fcol3:
        f_var = st.multiselect("Variant", sorted(df["Variant_Normalized"].unique()), key="f_var")
    with fcol4:
        f_stor = st.multiselect("Storage", sorted(df["Storage"].unique()), key="f_stor")

    display_df = df.copy()
    if f_kondisi:
        display_df = display_df[display_df["Kondisi"].isin(f_kondisi)]
    if f_gen:
        display_df = display_df[display_df["Generasi"].isin(f_gen)]
    if f_var:
        display_df = display_df[display_df["Variant_Normalized"].isin(f_var)]
    if f_stor:
        display_df = display_df[display_df["Storage"].isin(f_stor)]

    display_cols = ["Bulan", "Kondisi", "Generasi", "Variant_Normalized", "Storage", "Harga"]
    display_df = display_df[display_cols].sort_values(
        ["Bulan", "Kondisi", "Generasi", "Variant_Normalized", "Storage"],
        ascending=[False, True, True, True, True],
    )
    display_df["Harga (Rp)"] = display_df["Harga"].apply(lambda x: f"Rp {x:,.0f}")
    st.dataframe(
        display_df.rename(columns={"Variant_Normalized": "Variant"}),
        use_container_width=True, hide_index=True, height=500,
    )
    st.caption(f"Menampilkan {len(display_df)} dari {len(df)} data")
