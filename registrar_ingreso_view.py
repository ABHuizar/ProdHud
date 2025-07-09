# registrar_ingreso_view.py

import streamlit as st
import requests
from datetime import datetime
from utils.config import SERVICE_URL

def fetch_projects():
    resp = requests.get(f"{SERVICE_URL}/projects")
    resp.raise_for_status()
    return resp.json()

def registrar_ingreso_view():
    st.title("💰 Registrar Ingreso Manual")

    proyectos = fetch_projects()

    with st.form("form_revenue"):
        proyecto_sel = st.selectbox("Proyecto", proyectos, format_func=lambda p: p["name"])
        fecha = st.date_input("Fecha", value=datetime.now().date())
        monto = st.number_input("Monto generado (MXN)", min_value=0.0, format="%.2f")
        comentario = st.text_input("Comentario (opcional)")
        enviar = st.form_submit_button("Registrar ingreso")

        if enviar:
            record = {
                'project_id': proyecto_sel['id'],
                'date': fecha.isoformat(),
                'hours': 0.0,
                'minutes': 0,
                'seconds': 0,
                'decimal_hours': 0.0,
                'revenue': monto,
                'comentario': comentario
            }
            requests.post(f"{SERVICE_URL}/records", json=record)
            st.success(f"✅ Ingreso registrado para {proyecto_sel['name']} por ${monto:,.2f}")
