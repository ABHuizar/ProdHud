# ================================================
# File: startall.py
# ================================================
import subprocess
import os
import time

# === RUTAS ABSOLUTAS ===
BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))  # carpeta raiz del proyecto
BACKEND_PATH = os.path.join(BASE_DIR, "backend")     # donde está Service.py
FRONTEND_APP = os.path.join(BASE_DIR, "app.py")     # app de Streamlit

# === VERIFICACIONES ===
if not os.path.isfile(os.path.join(BACKEND_PATH, "Service.py")):
    raise FileNotFoundError("❌ No se encontró Service.py en el backend.")
if not os.path.isfile(FRONTEND_APP):
    raise FileNotFoundError("❌ No se encontró app.py de Streamlit.")

# === INICIAR BACKEND ===
print("🔧 Iniciando backend Flask...")
flask_proc = subprocess.Popen(["python", "Service.py"], cwd=BACKEND_PATH)

# Esperar que Flask inicie
time.sleep(2)

# === INICIAR FRONTEND (Streamlit) ===
print("🌐 Iniciando frontend Streamlit...")
streamlit_proc = subprocess.Popen(["python", "-m", "streamlit", "run", FRONTEND_APP])

# Esperar ambos procesos
try:
    flask_proc.wait()
    streamlit_proc.wait()
except KeyboardInterrupt:
    print("🛑 Deteniendo servicios...")
    flask_proc.terminate()
    streamlit_proc.terminate()