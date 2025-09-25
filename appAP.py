# app.py
import streamlit as st
from datetime import datetime
import json

# Pyrebase (cliente para Auth)
import pyrebase

# Admin SDK para Firestore / operaciones seguras
import firebase_admin
from firebase_admin import credentials, firestore

# --------------------------
# CONFIG - se recomienda usar st.secrets en producción
# --------------------------
# Ejemplo de cómo esperar que pongas los secrets:
# st.secrets["firebase"] = {
#   "apiKey": "...",
#   "authDomain": "...",
#   "projectId": "...",
#   "storageBucket": "...",
#   "messagingSenderId": "...",
#   "appId": "..."
# }
# st.secrets["service_account"] = { ... }  # JSON de la service account

firebase_config = st.secrets["firebase"]

# Inicializar pyrebase (cliente)
pb = pyrebase.initialize_app(firebase_config)
pb_auth = pb.auth()

# Inicializar firebase_admin (server-side) usando service account JSON desde secrets
if not firebase_admin._apps:
    service_account_info = st.secrets["service_account"]
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --------------------------
# Helpers
# --------------------------
def create_user_profile_in_firestore(uid, email, name=""):
    """Crea el documento del usuario con saldo de puntos inicial."""
    doc_ref = db.collection("users").document(uid)
    doc_ref.set({
        "email": email,
        "name": name,
        "points_balance": 0,
        "tier": "bronze",
        "created_at": datetime.utcnow(),
        "last_update": datetime.utcnow(),
    })

def get_user_profile(uid):
    doc = db.collection("users").document(uid).get()
    return doc.to_dict() if doc.exists else None

def add_points_transaction(uid, delta, reason="manual"):
    """Ejemplo de transacción segura para sumar/restar puntos."""
    user_ref = db.collection("users").document(uid)

    def transaction_update(transaction, ref):
        snapshot = ref.get(transaction=transaction)
        if not snapshot.exists:
            raise RuntimeError("Usuario no existe")
        current = snapshot.get("points_balance") or 0
        new_balance = current + delta
        if new_balance < 0:
            raise RuntimeError("Saldo insuficiente")
        transaction.update(ref, {
            "points_balance": new_balance,
            "last_update": datetime.utcnow()
        })
        # Crear registro de transacción
        tx_ref = ref.collection("points_tx").document()
        transaction.set(tx_ref, {
            "delta": delta,
            "reason": reason,
            "created_at": datetime.utcnow()
        })

    db.run_transaction(lambda tx: transaction_update(tx, user_ref))

# --------------------------
# UI
# --------------------------
st.title("Club de Fidelidad - Demo con Firebase")

menu = st.sidebar.selectbox("Menú", ["Registro", "Login", "Perfil (autenticado)"])

if menu == "Registro":
    st.header("Crear cuenta")
    name = st.text_input("Nombre")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    if st.button("Registrarme"):
        try:
            # create user (cliente)
            user = pb_auth.create_user_with_email_and_password(email, password)
            id_token = user['idToken']
            # enviar email de verificación
            pb_auth.send_email_verification(id_token)

            # obtener uid (localId)
            info = pb_auth.get_account_info(id_token)
            uid = info['users'][0]['localId']

            # crear perfil en Firestore mediante admin SDK
            create_user_profile_in_firestore(uid, email, name)

            st.success("Cuenta creada. Revisa tu email y confirma la verificación antes de iniciar sesión.")
        except Exception as e:
            st.error(f"Error: {e}")

elif menu == "Login":
    st.header("Iniciar sesión")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        try:
            user = pb_auth.sign_in_with_email_and_password(email, password)
            id_token = user['idToken']
            info = pb_auth.get_account_info(id_token)
            user_rec = info['users'][0]
            uid = user_rec['localId']
            verified = user_rec.get('emailVerified', False)

            if not verified:
                st.warning("Tu email no está verificado. Revisa tu bandeja y confirma el enlace.")
                if st.button("Reenviar email de verificación"):
                    pb_auth.send_email_verification(id_token)
                    st.info("Email de verificación reenviado.")
            else:
                st.success("Login correcto y email verificado.")
                # Guardar sesión en st.session_state de forma básica
                st.session_state["uid"] = uid
                st.session_state["id_token"] = id_token
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error de autenticación: {e}")

elif menu == "Perfil (autenticado)":
    if "uid" not in st.session_state:
        st.info("Inicia sesión primero en la pestaña Login.")
    else:
        uid = st.session_state["uid"]
        profile = get_user_profile(uid)
        if not profile:
            st.error("Perfil no encontrado en Firestore.")
        else:
            st.subheader(f"Hola, {profile.get('name') or profile.get('email')}")
            st.write("Puntos:", profile.get("points_balance", 0))
            st.write("Tier:", profile.get("tier"))
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Sumar 10 puntos (ejemplo)"):
                    try:
                        add_points_transaction(uid, 10, reason="promo_demo")
                        st.success("Sumados 10 puntos.")
                    except Exception as e:
                        st.error(str(e))
            with col2:
                if st.button("Canjear 5 puntos (ejemplo)"):
                    try:
                        add_points_transaction(uid, -5, reason="redeem_demo")
                        st.success("Canje realizado.")
                    except Exception as e:
                        st.error(str(e))
            # Mostrar últimas tx
            tx_docs = db.collection("users").document(uid).collection("points_tx").order_by("created_at", direction=firestore.Query.DESCENDING).limit(10).stream()
            st.write("Últimas transacciones:")
            for t in tx_docs:
                st.write(t.to_dict())
