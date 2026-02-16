"""Tab Analisis Data — box plots and scatter charts."""

import streamlit as st
import plotly.express as px


def render(df):
    st.subheader("Analisis Data")

    col_x, col_y = st.columns(2)
    with col_x:
        fig_box1 = px.box(df, x="Kondisi", y="Harga", color="Kondisi",
                          title="Distribusi Harga per Kondisi",
                          labels={"Harga": "Harga (Rp)"})
        st.plotly_chart(fig_box1, use_container_width=True)
    with col_y:
        fig_box2 = px.box(df, x="Generasi", y="Harga", color="Generasi",
                          title="Distribusi Harga per Generasi",
                          labels={"Harga": "Harga (Rp)"})
        st.plotly_chart(fig_box2, use_container_width=True)

    col_p, col_q = st.columns(2)
    with col_p:
        fig_box3 = px.box(df, x="Variant_Normalized", y="Harga", color="Variant_Normalized",
                          title="Distribusi Harga per Variant",
                          labels={"Harga": "Harga (Rp)", "Variant_Normalized": "Variant"})
        st.plotly_chart(fig_box3, use_container_width=True)
    with col_q:
        fig_stor = px.scatter(df, x="Storage", y="Harga", color="Generasi",
                              title="Harga vs Storage", log_x=True,
                              labels={"Harga": "Harga (Rp)", "Storage": "Storage (GB)"})
        st.plotly_chart(fig_stor, use_container_width=True)
