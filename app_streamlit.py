import streamlit as st

from utils.data import load_data
from utils.metrics import professionals_by_departement
from utils.charts import bar_professionals_by_departement

st.set_page_config(page_title="HealthMap", layout="wide")

st.title("🏥 HealthMap — Répartition des professionnels de santé")

df = load_data()

st.metric("Nombre total de professionnels", len(df))

df_dept = professionals_by_departement(df)

st.plotly_chart(
    bar_professionals_by_departement(df_dept),
    use_container_width=True
)
