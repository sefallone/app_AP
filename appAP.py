import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import json
import os

# --- Debug completo de Secrets ---
st.sidebar.title("🔧 Debug de Configuración")

# Verificar qué secrets están disponibles
try:
    all_secrets = dict(st.secrets)  # Convertir a dict para inspeccionar
    st.sidebar.write("**Todos los secrets:**", list(all_secrets.keys()))
    
    # Verificar FIREBASE_API_KEY específicamente
    if "FIREBASE_API_KEY" in st.secrets:
        API_KEY = st.secrets["FIREBASE_API_KEY"]
        st.sidebar.success("✅ FIREBASE_API_KEY encontrada")
        st.sidebar.write("Longitud API Key:", len(API_KEY))
    else:
        st.sidebar.error("❌ FIREBASE_API_KEY NO encontrada")
        API_KEY = None
        
except Exception as e:
    st.sidebar.error(f"Error accediendo secrets: {e}")
    API_KEY = None

# --- Si no hay API_KEY, mostrar ayuda detallada ---
if not API_KEY:
    st.error("""
    # 🚨 Configuración de Secrets Requerida
    
    ### 🔍 ¿Qué está pasando?
    Streamlit Cloud no puede encontrar tus secrets de Firebase.
    
    ### 🛠️ **Solución RÁPIDA:**
    1. **Ve a [share.streamlit.io](https://share.streamlit.io)**
    2. **Selecciona tu app → Settings (⚙️) → Secrets**
    3. **Pega EXACTAMENTE esto:**
    """)
    
    st.code("""
FIREBASE_API_KEY = "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k"

[FIREBASE_SERVICE_ACCOUNT]
type = "service_account"
project_id = "webap-6e49a"
private_key_id = "c0e8fd963a84b382decbb8c06785f2786aa58923"
private_key = \"\"\"-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDIL+ComB9bMuYb
ZeiH/an6aBBLb0ZMJ8npJHEeFmXQ/cobrLzSj9YtsjOsvYHyONPI2kgeeSZCGbSc
YqHJeW3n6mR+8klB3qGkwFMDWRdCS2ni016EgXkSamq6zEZ7kO2DHonSy1eQfZiD
sdRhju4DV9icl188+Tr8pujuHde3ysfckIEC9as3CzpCIqoB65UvG5tsFGEXvvLO
r5lsshn2sR89u8esjy3dfqTChj7MMMAquKhMze34N28AOKTci6K1z/5H1JfD2RxI
+wNCiQA1sF/0YlSVratQ5kbJ6MiitzxTiN8cjm9kZuSvSXCe8Bm3HsxrSNJwRzj3
JBnAHYW7AgMBAAECggEAA2Z2Hpb64rMsymatj5saPIPGUb8G8Xs0Mu6+ByCimRf+
dgA18tj47oIaM5htG8lQUOyNkLWbwJVW29h8Xq4z1N5xLODTqA1D2fG0V0MM90DN
qx8jpK+ITWzw+XxHxDM0KD0oDSRhYosSQJu60O9lu+PNl5dQnvoCwPuFdanxxJA4
VDlai49i7Ony1zElqoYKGqAcJK4aC4ga5sfHWsC4F+HiEE01PfQCijnilKu6UEFt
HvInoys9gj8dNz/BNsIkaQ7MOPlFc1NQISUiuFL0pNLS9O2s0n8DKVULWzR2OYfK
k1fJjc5olOdFEAB67FVa5zMDPv49mckZUOqPxZOCEQKBgQDpPHkVh2Af2quUmfvt
viyi9BSoJel9V/X2HVo0cn8FbE1FBEMcCP4r/thc6nt2Q5V+X21UQ0vym0WLcpWe
MSqXsBsaIYp6O1L7+0INOeUUSGmZlFONVnBoJPwzoLfyWzGULadaPBj94fFWhVCd
HYEBCE8+URniCgFfGuqCm7ReCwKBgQDbuac+z5Q0yHPJuwMVastV4vlvWvZTt1F0
OqnhCpZjUmWNI/uhhXVfpSKC5Wy3v9JnFFMNNQoWATvB+FoOVQ6FIY/0QxN5uxiX
jhe92kKStY2oWARBvunIoX++s/IR9aXAkjEwzLCIx8EIfHwVDYoaNBmyNPp7uEBO
6e/DfuE1EQKBgFE5PRWxQll1hoFGqsRdkR/ijnsMUObUxhRCnpJbOT8DO1mIpXJS
82kQ4/pfskU6Pgp3YxSQJxfC2RI6Aj7H8oRG0PllqtrsY/baxmLiwZMxsIzKadpz
usuZ7bZxBv5AoeBvkbNL8IwhrjEqViuRBcb9RNN33OKqB1Y+gmKfpM2HAoGARE3p
XNBAvUvXGs4E/mJthWyCqAg57Ppe2uflqWyWJZgWs5KNBcAsJah7Gv/hFRoPeTXL
P57OXNrTTdA7hpsQYXh2fLNhWYU89tgYL0+rRFomCEAcSqfjmxgBUzIzPTwE4+FO
Y2IuOscGDfJMzGqiFNU/a7OmblFvxFhazYYi0lECgYEAn4WIRH7uIEBRhajPWWgg
bD1aWCrsiCJtBz4J89dNDQ1Cr2sqGRfIY9Mp2XdgE70SXo5F7ce8ybT5aZPCRHT9
xVNCYKc33+06qCOuBsIMMakI2STxRjYXBsE8/ZrXBfl2BFFh6nmdYstAJ/FFo6QN
tmYP4juK0ul0xRnlkFWGE30=
-----END PRIVATE KEY-----\"\"\"
client_email = "firebase-adminsdk-fbsvc@webap-6e49a.iam.gserviceaccount.com"
client_id = "100204266031113174768"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40webap-6e49a.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
""", language="toml")

    st.info("""
    **💡 Después de pegar los secrets:**
    - Haz clic en **Save**
    - Espera 1-2 minutos
    - **Recarga la página** de tu app Streamlit
    """)
    
    st.stop()

# --- Si llegamos aquí, tenemos API_KEY ---
st.sidebar.success("🎉 ¡Configuración correcta! Inicializando Firebase...")

try:
    # Inicializar Firebase Admin
    if not firebase_admin._apps:
        cred_dict = dict(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        st.sidebar.success("✅ Firebase Admin inicializado")
    
    db = firestore.client()
    st.sidebar.success("✅ Firestore conectado")
    
except Exception as e:
    st.error(f"❌ Error inicializando Firebase: {e}")
    st.stop()

# --- Funciones auxiliares ---
def login_user(email, password):
    """Login con Firebase REST API (correo + contraseña)"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        return res.json()
    else:
        raise Exception(res.json().get("error", {}).get("message", "Login failed"))


def save_profile(uid, nombre, email):
    """Guarda perfil inicial del cliente en Firestore"""
    db.collection("clientes").document(uid).set({
        "nombre": nombre,
        "email": email,
        "puntos": 0
    })


def get_profile(uid):
    """Obtiene el perfil del cliente desde Firestore"""
    doc = db.collection("clientes").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None


def update_points(uid, delta):
    """Suma o resta puntos en el perfil"""
    doc_ref = db.collection("clientes").document(uid)
    doc = doc_ref.get()
    if doc.exists:
        current = doc.to_dict().get("puntos", 0)
        new_value = max(0, current + delta)  # nunca menos de 0
        doc_ref.update({"puntos": new_value})
        return new_value
    return 0


# --- UI Principal ---
st.title("🎨 App de Clientes - Arte París")

# Inicializar sesión
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"]:
    # Usuario logueado
    user_info = st.session_state["user"]
    uid = user_info["localId"]

    st.success(f"✨ Bienvenido {user_info['email']} 👋")

    perfil = get_profile(uid)
    if perfil:
        st.subheader("📊 Tu perfil")
        st.write(f"**Nombre:** {perfil['nombre']}")
        st.write(f"**Correo:** {perfil['email']}")
        st.write(f"**Puntos acumulados:** {perfil['puntos']} ⭐")

        # --- Sección de puntos ---
        st.subheader("🎯 Gestión de Puntos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎁 Acumular +10 puntos", use_container_width=True):
                new_points = update_points(uid, 10)
                st.success(f"¡Perfecto! Ahora tienes {new_points} puntos 🎉")
                st.rerun()

        with col2:
            if st.button("🔄 Canjear 50 puntos", use_container_width=True):
                if perfil["puntos"] >= 50:
                    new_points = update_points(uid, -50)
                    st.success(f"✅ Canje exitoso! Te quedan {new_points} puntos.")
                    st.rerun()
                else:
                    st.warning("❌ No tienes suficientes puntos para canjear")

    else:
        st.warning("⚠️ Perfil no encontrado. Contacta con soporte.")

    st.markdown("---")
    if st.button("🚪 Cerrar sesión"):
        st.session_state["user"] = None
        st.rerun()

else:
    # Menú de no logueado
    st.sidebar.subheader("🔐 Autenticación")
    menu = st.sidebar.selectbox("Selecciona una opción:", ["Login", "Registro"])

    if menu == "Registro":
        st.subheader("📝 Crear nueva cuenta")
        
        with st.form("form_registro"):
            nombre = st.text_input("Nombre completo")
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("📨 Registrar cuenta"):
                if nombre and email and password:
                    try:
                        user = auth.create_user(email=email, password=password)
                        save_profile(user.uid, nombre, email)
                        st.success("✅ Usuario creado correctamente! Ahora puedes iniciar sesión.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Por favor, completa todos los campos")

    elif menu == "Login":
        st.subheader("🔑 Iniciar sesión")
        
        with st.form("form_login"):
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("🚀 Ingresar"):
                if email and password:
                    try:
                        user_info = login_user(email, password)
                        st.session_state["user"] = user_info
                        st.success("✅ ¡Login exitoso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Por favor, ingresa correo y contraseña")

# --- Footer ---
st.markdown("---")
st.markdown("🎨 *Arte París - Sistema de fidelización de clientes*")

