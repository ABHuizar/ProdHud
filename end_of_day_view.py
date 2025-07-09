# ================================================
# File: end_of_day_view.py
# ================================================
import streamlit as st
import requests
from utils.config import SERVICE_URL

@st.cache_data
def commit_end_of_day():
    resp = requests.post(f"{SERVICE_URL}/commit")
    resp.raise_for_status()
    return resp.json().get('migrated', 0)

def end_of_day_view():
    st.title("🔄 End of Day")
    if st.button("Procesar registros diarios"):
        migrated = commit_end_of_day()
        st.success(f"Migrados {migrated} registros a la base.")