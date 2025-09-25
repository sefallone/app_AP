import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import json

# ==================================================
# CONFIGURACIÓN MANUAL DE FIREBASE (ELIMINA ESTO CUANDO FUNCIONEN LOS SECRETS)
# ==================================================

# 🔥 PEGA TU CONFIGURACIÓN AQUÍ DIRECTAMENTE
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "SERVICE_ACCOUNT": {
        "type": "service_account",
        "project_id": "webap-6e49a",
        "private_key_id": "c0e8fd963a84b382decbb8c06785f2786aa58923",
        "private_key": """-----BEGIN PRIVATE KEY-----
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
-----END PRIVATE KEY-----""",
        "client_email": "firebase-adminsdk-fbsvc@webap-6e49a.iam.gserviceaccount.com",
        "client_id": "100204266031113174768",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40webap-6e49a.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
}

# ==================================================
# INICIALIZACIÓN DE FIREBASE
# ==================================================

# Usar configuración directa en lugar de secrets
API_KEY = FIREBASE_CONFIG["API_KEY"]

try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CONFIG["SERVICE_ACCOUNT"])
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    st.success("✅ Firebase conectado correctamente!")
    
except Exception as e:
    st.error(f"❌ Error conectando con Firebase: {e}")
    st.stop()

# ==================================================
# FUNCIONES DE LA APLICACIÓN
# ==================================================

def login_user(email, password):
    """Login con Firebase REST API"""
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
    """Guarda perfil inicial del cliente"""
    db.collection("clientes").document(uid).set({
        "nombre": nombre,
        "email": email,
        "puntos": 0
    })

def get_profile(uid):
    """Obtiene el perfil del cliente"""
    doc = db.collection("clientes").document(uid).get()
    if doc.exists:
        return doc.to_dict()
    return None

def update_points(uid, delta):
    """Suma o resta puntos"""
    doc_ref = db.collection("clientes").document(uid)
    doc = doc_ref.get()
    if doc.exists:
        current = doc.to_dict().get("puntos", 0)
        new_value = max(0, current + delta)
        doc_ref.update({"puntos": new_value})
        return new_value
    return 0

# ==================================================
# INTERFAZ DE USUARIO
# ==================================================

st.title("🎨 App de Clientes - Arte París")
st.markdown("---")

# Manejo de sesión
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"]:
    # Usuario logueado
    user_info = st.session_state["user"]
    uid = user_info["localId"]

    st.success(f"✨ Bienvenido {user_info['email']}")

    perfil = get_profile(uid)
    if perfil:
        st.subheader("📊 Tu Perfil")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Nombre:** {perfil['nombre']}")
            st.info(f"**Email:** {perfil['email']}")
        with col2:
            st.success(f"**Puntos:** {perfil['puntos']} ⭐")
        
        st.subheader("🎯 Gestión de Puntos")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎁 +10 Puntos", use_container_width=True):
                new_points = update_points(uid, 10)
                st.success(f"¡Ahora tienes {new_points} puntos!")
                st.rerun()
        with col2:
            if st.button("🔄 Canjear 50 Puntos", use_container_width=True):
                if perfil["puntos"] >= 50:
                    new_points = update_points(uid, -50)
                    st.success(f"✅ Canjeado! Te quedan {new_points} puntos")
                    st.rerun()
                else:
                    st.warning("❌ No tienes puntos suficientes")
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["user"] = None
        st.rerun()

else:
    # Usuario no logueado
    st.subheader("🔐 Inicio de Sesión")
    
    tab1, tab2 = st.tabs(["📝 Registro", "🚀 Login"])
    
    with tab1:
        with st.form("registro_form"):
            st.write("**Crear nueva cuenta**")
            nombre = st.text_input("Nombre completo")
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Crear Cuenta"):
                if nombre and email and password:
                    try:
                        user = auth.create_user(email=email, password=password)
                        save_profile(user.uid, nombre, email)
                        st.success("✅ Cuenta creada! Ya puedes iniciar sesión.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Completa todos los campos")
    
    with tab2:
        with st.form("login_form"):
            st.write("**Acceder a tu cuenta**")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Contraseña", type="password", key="login_password")
            
            if st.form_submit_button("Iniciar Sesión"):
                if email and password:
                    try:
                        user_info = login_user(email, password)
                        st.session_state["user"] = user_info
                        st.success("✅ ¡Bienvenido!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Ingresa email y contraseña")

st.markdown("---")
st.markdown("💎 *Sistema de fidelización - Arte París*")
