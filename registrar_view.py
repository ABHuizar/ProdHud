# registrar_view.py

import streamlit as st
import requests
from datetime import datetime
from utils.config import SERVICE_URL

def fetch_projects():
    resp = requests.get(f"{SERVICE_URL}/projects")
    resp.raise_for_status()
    return resp.json()

def registrar_view():
    st.title("⏱️ Registrar Trabajo")

    proyectos = fetch_projects()

    if 'active_proj' not in st.session_state:
        st.session_state.active_proj = None
        st.session_state.start_time = None

    if st.session_state.active_proj:
        # Proyecto activo: mostrar solo botón de detener
        proyecto = next((p for p in proyectos if p['id'] == st.session_state.active_proj), None)
        if proyecto:
            st.markdown(f"### 🟢 Trabajando en: **{proyecto['name']}**")
            if st.button("🔴 Finalizar trabajo"):
                start_time = datetime.fromisoformat(st.session_state.start_time)
                elapsed = datetime.now() - start_time
                total_seconds = int(elapsed.total_seconds())

                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                decimal_hours = round(total_seconds / 3600, 6)

                record = {
                    'project_id': proyecto['id'],
                    'date': datetime.now().date().isoformat(),
                    'hours': hours,
                    'minutes': minutes,
                    'seconds': seconds,
                    'decimal_hours': decimal_hours,
                    'revenue': 0.0
                }

                requests.post(f"{SERVICE_URL}/records", json=record)
                st.session_state.active_proj = None
                st.session_state.start_time = None
                st.success(f"✅ Trabajo registrado: {hours}h {minutes}m {seconds}s")
                st.rerun()

        else:
            st.warning("⚠️ Proyecto no encontrado.")
            st.session_state.active_proj = None
            st.session_state.start_time = None
    else:
        # No hay proyecto activo: mostrar botones para iniciar
        st.subheader("Selecciona un proyecto para comenzar:")
        for proj in proyectos:
            if st.button(f"▶️ Iniciar: {proj['name']}", key=f"start_{proj['id']}"):
                st.session_state.active_proj = proj['id']
                st.session_state.start_time = datetime.now().isoformat()
                st.rerun()
