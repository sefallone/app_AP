import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import json

# --- Configuración ---
API_KEY = st.secrets["FIREBASE_API_KEY"]  # Firebase Web API Key

# Inicializar Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
    firebase_admin.initialize_app(cred)
db = firestore.client()


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


# --- UI ---
st.title("App de Clientes - Arte París")

# Inicializar sesión
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"]:
    # Usuario logueado
    user_info = st.session_state["user"]
    uid = user_info["localId"]

    st.success(f"Bienvenido {user_info['email']} 👋")

    perfil = get_profile(uid)
    if perfil:
        st.subheader("Tu perfil")
        st.write(f"**Nombre:** {perfil['nombre']}")
        st.write(f"**Correo:** {perfil['email']}")
        st.write(f"**Puntos acumulados:** {perfil['puntos']}")

        # --- Sección de puntos ---
        st.subheader("Gestión de Puntos")

        if st.button("Acumular +10 puntos"):
            new_points = update_points(uid, 10)
            st.success(f"Ahora tienes {new_points} puntos 🎉")
            st.experimental_rerun()

        if st.button("Canjear 50 puntos"):
            if perfil["puntos"] >= 50:
                new_points = update_points(uid, -50)
                st.success(f"Canje exitoso ✅. Te quedan {new_points} puntos.")
                st.experimental_rerun()
            else:
                st.warning("No tienes suficientes puntos para canjear ❌")

    if st.button("Cerrar sesión"):
        st.session_state["user"] = None
        st.experimental_rerun()

else:
    # Menú de no logueado
    menu = st.sidebar.selectbox("Menú", ["Registro", "Login"])

    if menu == "Registro":
        nombre = st.text_input("Nombre")
        email = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrar"):
            try:
                user = auth.create_user(email=email, password=password)
                save_profile(user.uid, nombre, email)
                st.success("Usuario creado correctamente ✅ Ahora puedes iniciar sesión.")
            except Exception as e:
                st.error(f"Error: {e}")

    elif menu == "Login":
        email = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            try:
                user_info = login_user(email, password)
                st.session_state["user"] = user_info
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {e}")

