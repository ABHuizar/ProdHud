import streamlit as st
from proyectos_view import proyectos_view
from registrar_view import registrar_view
from dashboard_view import dashboard_view
from end_of_day_view import end_of_day_view
from registrar_ingreso_view import registrar_ingreso_view


st.set_page_config(page_title="Productivity HUD", layout="wide")

page = st.sidebar.radio(
    "Menú",
    ["Proyectos", "Registrar", "Dashboard", "End of Day", "Registrar ingreso"]
)

if page == "Proyectos":
    proyectos_view()
elif page == "Registrar":
    registrar_view()
elif page == "Dashboard":
    dashboard_view()
elif page == "End of Day":
    end_of_day_view()
elif page == "Registrar ingreso":
    registrar_ingreso_view()
else:
    st.error("Vista no encontrada: " + page)


