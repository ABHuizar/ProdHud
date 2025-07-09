# ================================================
# File: proyectos_view.py
# ================================================
import streamlit as st
import requests
from utils.config import SERVICE_URL

@st.cache_data(show_spinner=False)
def fetch_projects():
    resp = requests.get(f"{SERVICE_URL}/projects")
    resp.raise_for_status()
    return resp.json()

def proyectos_view():
    st.title("🗂️ Gestión de Proyectos")
    proyectos = fetch_projects()
    st.subheader("Proyectos existentes")
    for p in proyectos:
        st.write(f"- {p['name']}")
    st.markdown("---")
    new_name = st.text_input("Nombre del proyecto", key="new_proj")
    if st.button("Crear proyecto"):
        if new_name:
            resp = requests.post(f"{SERVICE_URL}/projects", json={"name": new_name})
            if resp.ok:
                st.success(f"Proyecto '{new_name}' creado.")
                from streamlit.runtime.scriptrunner import get_script_run_ctx
                ctx = get_script_run_ctx()
                if ctx:
                    ctx.rerun()
        else:
            st.error("Ingresa un nombre válido.")
    st.markdown("---")
    options = [p['name'] for p in proyectos]
    to_del = st.selectbox("Eliminar proyecto", [""] + options)
    if st.button("Eliminar proyecto") and to_del:
        pid = next((p['id'] for p in proyectos if p['name']==to_del), None)
        if pid:
            resp = requests.delete(f"{SERVICE_URL}/projects", json={"id": pid})
            if resp.ok:
                st.success(f"Proyecto '{to_del}' eliminado.")
                from streamlit.runtime.scriptrunner import get_script_run_ctx
                ctx = get_script_run_ctx()
                if ctx:
                    ctx.rerun()