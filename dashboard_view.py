# ================================================
# File: dashboard_view.py
# ================================================
import streamlit as st
import pandas as pd
import requests
from utils.config import SERVICE_URL

@st.cache_data
def fetch_dashboard():
    resp = requests.get(f"{SERVICE_URL}/dashboard")
    resp.raise_for_status()
    return resp.json()

def dashboard_view():
    st.title("📊 Dashboard")
    data = fetch_dashboard()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.metric("Total Horas", df['hours'].sum())
        st.metric("Total Ingresos", df['revenue'].sum())
        by_proj = df.groupby('project')[['hours','revenue']].sum()
        st.bar_chart(by_proj)
    else:
        st.info("No hay datos disponibles.")