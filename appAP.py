import streamlit as st
import requests
import json
import time

# ==================================================
# CONFIGURACIÓN FIREBASE
# ==================================================

FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# FUNCIONES MEJORADAS CON REGLAS TEMPORALES
# ==================================================

def signup_user(email, password, nombre):
    """Registrar usuario con Firebase REST API"""
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_CONFIG['API_KEY']}"
        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, data=payload, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            st.success("✅ Usuario registrado en Authentication")
            # Intentar guardar perfil (puede fallar por reglas)
            time.sleep(1)  # Pequeña pausa
            save_profile_via_rest(result['localId'], nombre, email)
            return result
        else:
            error_msg = result.get('error', {}).get('message', 'Error desconocido')
            raise Exception(f"Registro falló: {error_msg}")
            
    except Exception as e:
        raise Exception(f"Error en registro: {str(e)}")

def login_user(email, password):
    """Login con Firebase REST API"""
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['API_KEY']}"
        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, data=payload, headers=headers)
        result = response.json()
        
        if response.status_code == 200:
            return result
        else:
            error_msg = result.get('error', {}).get('message', 'Error desconocido')
            raise Exception(f"Login falló: {error_msg}")
            
    except Exception as e:
        raise Exception(f"Error en login: {str(e)}")

def save_profile_via_rest(uid, nombre, email):
    """Guardar perfil - con manejo de errores de reglas"""
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        
        document_data = {
            "fields": {
                "nombre": {"stringValue": nombre},
                "email": {"stringValue": email},
                "puntos": {"integerValue": 0},
                "timestamp": {"timestampValue": "2024-01-01T00:00:00Z"}
            }
        }
        
        response = requests.patch(url, json=document_data)
        
        if response.status_code == 200:
            st.success("✅ Perfil guardado en Firestore")
            return True
        else:
            # Si falla por reglas, mostrar ayuda
            error_msg = response.json().get('error', {}).get('message', '')
            if "permission" in error_msg.lower():
                st.warning("""
                ⚠️ **Problema de permisos en Firestore**
                
                **Solución temporal:**
                1. Ve a Firestore Database → Reglas
                2. Reemplaza las reglas actuales por:
                ```
                rules_version = '2';
                service cloud.firestore {
                  match /databases/{database}/documents {
                    match /{document=**} {
                      allow read, write: if true;
                    }
                  }
                }
                ```
                3. Haz clic en **Publicar**
                """)
            return False
            
    except Exception as e:
        st.warning(f"⚠️ No se pudo guardar perfil: {e}")
        return False

def get_profile_via_rest(uid):
    """Obtener perfil con manejo de errores"""
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'fields' in data:
                return {
                    'nombre': data['fields'].get('nombre', {}).get('stringValue', ''),
                    'email': data['fields'].get('email', {}).get('stringValue', ''),
                    'puntos': data['fields'].get('puntos', {}).get('integerValue', 0)
                }
        elif response.status_code == 404:
            return None  # Documento no existe
        else:
            return None
            
    except:
        return None

def update_points_via_rest(uid, delta):
    """Actualizar puntos con manejo robusto"""
    try:
        perfil = get_profile_via_rest(uid)
        if perfil:
            current_points = perfil.get('puntos', 0)
            new_points = max(0, current_points + delta)
            
            url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
            update_data = {
                "fields": {
                    "puntos": {"integerValue": new_points}
                }
            }
            
            response = requests.patch(url, json=update_data)
            return new_points if response.status_code == 200 else current_points
        return 0
    except:
        return 0

# ==================================================
# INTERFAZ PRINCIPAL
# ==================================================

st.set_page_config(page_title="Arte París", page_icon="🎨", layout="centered")

st.title("🎨 Arte París")
st.markdown("---")

# Verificación inicial
if not FIREBASE_CONFIG["API_KEY"] or FIREBASE_CONFIG["API_KEY"] == "tu_api_key_aqui":
    st.error("❌ Configura la API_KEY de Firebase en el código")
    st.stop()

# Estado de la sesión
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    # === USUARIO LOGUEADO ===
    user_info = st.session_state.user
    uid = user_info["localId"]
    
    st.success(f"✨ ¡Bienvenido {user_info['email']}!")
    
    # Obtener perfil
    perfil = get_profile_via_rest(uid)
    
    if perfil:
        st.subheader("📊 Tu Perfil")
        st.write(f"**Nombre:** {perfil['nombre']}")
        st.write(f"**Email:** {perfil['email']}")
        st.write(f"**Puntos:** {perfil['puntos']} ⭐")
        
        st.subheader("🎯 Gestión de Puntos")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎁 +10 Puntos", use_container_width=True):
                new_points = update_points_via_rest(uid, 10)
                st.success(f"¡Ahora tienes {new_points} puntos!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Canjear 50 Puntos", use_container_width=True):
                if perfil['puntos'] >= 50:
                    new_points = update_points_via_rest(uid, -50)
                    st.success(f"✅ Canjeado! Puntos restantes: {new_points}")
                    st.rerun()
                else:
                    st.error("❌ Puntos insuficientes")
    
    else:
        st.warning("⚠️ Perfil no encontrado en Firestore")
        st.info("""
        **Posibles soluciones:**
        1. **Las reglas de Firestore están bloqueando el acceso**
        2. **El perfil no se creó correctamente**
        
        **Solución rápida:** Ve a Firestore → Reglas y usa reglas temporales abiertas.
        """)
        
        if st.button("🔄 Reintentar carga de perfil"):
            st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()

else:
    # === USUARIO NO LOGUEADO ===
    st.subheader("🔐 Acceso al Sistema")
    
    tab1, tab2 = st.tabs(["🚀 Login", "📝 Registro"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Ingresar"):
                if email and password:
                    try:
                        user_info = login_user(email, password)
                        st.session_state.user = user_info
                        st.success("✅ Login exitoso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                else:
                    st.warning("⚠️ Completa todos los campos")
    
    with tab2:
        with st.form("registro_form"):
            nombre = st.text_input("Nombre completo")
            email = st.text_input("Email")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Crear Cuenta"):
                if nombre and email and password:
                    try:
                        user_info = signup_user(email, password, nombre)
                        st.session_state.user = user_info
                        st.success("✅ ¡Cuenta creada!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                else:
                    st.warning("⚠️ Completa todos los campos")

# ==================================================
# PANEL DE CONFIGURACIÓN Y AYUDA
# ==================================================

with st.sidebar:
    st.header("🔧 Configuración")
    
    if st.button("🔄 Verificar Conexión Firebase"):
        try:
            # Test simple de Authentication
            test_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_CONFIG['API_KEY']}"
            response = requests.post(test_url, json={"returnSecureToken": True})
            if response.status_code != 400:  # 400 es normal sin datos
                st.success("✅ Firebase Authentication: CONECTADO")
            else:
                st.error("❌ Firebase Authentication: ERROR")
        except:
            st.error("❌ No se pudo conectar a Firebase")
    
    st.markdown("---")
    st.header("📋 Reglas Firestore (CRÍTICO)")
    
    st.code("""
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /clientes/{userId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == userId;
    }
    // Temporal para desarrollo:
    // allow read, write: if true;
  }
}
""", language="javascript")
    
    st.info("**Para desarrollo, usa reglas abiertas temporalmente**")

st.markdown("---")
st.caption("💎 Arte París - Sistema de fidelización")
