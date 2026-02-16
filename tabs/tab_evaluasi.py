"""Tab Evaluasi Model — per-product scatter + global model comparison."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render(eval_df, global_results):
    st.subheader("Evaluasi Model Per-Produk vs Global")
    st.markdown("""
    **Per-Produk (Linear Trend):** Setiap kombinasi Kondisi+Generasi+Variant+Storage punya model sendiri.
    Menangkap tren spesifik: Second/BC turun, New stabil.
    
    **Global (ML):** Satu model untuk semua data. Fallback jika produk tidak ada di dataset.
    """)

    st.subheader("Akurasi Per-Produk (Leave-Last-Out)")
    if not eval_df.empty:
        col_ev1, col_ev2, col_ev3 = st.columns(3)
        with col_ev1:
            st.metric("MAPE", f"{eval_df['APE'].mean():.2f}%")
        with col_ev2:
            st.metric("MAE", f"Rp {eval_df['Error'].abs().mean():,.0f}")
        with col_ev3:
            st.metric("Produk Dievaluasi", f"{len(eval_df)}")

        fig_pp = px.scatter(
            eval_df, x="Actual", y="Predicted",
            title="Per-Produk: Aktual vs Prediksi (bulan terakhir)",
            labels={"Actual": "Harga Aktual (Rp)", "Predicted": "Harga Prediksi (Rp)"},
            hover_data=["Product", "APE"],
        )
        max_val = max(eval_df["Actual"].max(), eval_df["Predicted"].max())
        fig_pp.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode="lines", name="Perfect", line=dict(dash="dash", color="red"),
        ))
        st.plotly_chart(fig_pp, use_container_width=True)

    st.subheader("Perbandingan Model Global (Fallback)")
    comparison_data = []
    for name, res in global_results.items():
        comparison_data.append({
            "Model": name,
            "R² Score": f"{res['r2']:.4f}",
            "MAE (Rp)": f"{res['mae']:,.0f}",
            "MAPE (%)": f"{res['mape']:.2f}",
            "CV R² Mean": f"{res['cv_r2_mean']:.4f}",
        })
    comp_df = pd.DataFrame(comparison_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_r2 = px.bar(comp_df, x="Model", y="R² Score",
                        title="R² Score (makin tinggi makin baik)",
                        color="Model", text="R² Score")
        fig_r2.update_traces(textposition="outside")
        st.plotly_chart(fig_r2, use_container_width=True)
    with col_b:
        fig_mape = px.bar(comp_df, x="Model", y="MAPE (%)",
                          title="MAPE (makin rendah makin baik)",
                          color="Model", text="MAPE (%)")
        fig_mape.update_traces(textposition="outside")
        st.plotly_chart(fig_mape, use_container_width=True)
