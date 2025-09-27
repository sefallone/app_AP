import streamlit as st
import requests
import json
import time
from datetime import datetime

# ==================================================
# CONFIGURACIÓN FIREBASE
# ==================================================

FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# FUNCIONES MEJORADAS
# ==================================================

def signup_user(email, password, nombre):
    """Registrar usuario con bono de 10 puntos"""
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
            # Guardar perfil con bono de 10 puntos
            time.sleep(1)
            save_profile_via_rest(result['localId'], nombre, email, bonus_points=10)
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

def save_profile_via_rest(uid, nombre, email, bonus_points=0):
    """Guardar perfil con puntos de bono"""
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        
        document_data = {
            "fields": {
                "nombre": {"stringValue": nombre},
                "email": {"stringValue": email},
                "puntos": {"integerValue": bonus_points},
                "timestamp": {"timestampValue": datetime.utcnow().isoformat() + "Z"},
                "total_compras": {"doubleValue": 0.0},
                "tickets_registrados": {"integerValue": 0}
            }
        }
        
        response = requests.patch(url, json=document_data)
        
        if response.status_code == 200:
            st.success(f"✅ Perfil guardado con {bonus_points} puntos de bono!")
            return True
        else:
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
    """Obtener perfil con información extendida"""
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'fields' in data:
                return {
                    'nombre': data['fields'].get('nombre', {}).get('stringValue', ''),
                    'email': data['fields'].get('email', {}).get('stringValue', ''),
                    'puntos': data['fields'].get('puntos', {}).get('integerValue', 0),
                    'total_compras': data['fields'].get('total_compras', {}).get('doubleValue', 0.0),
                    'tickets_registrados': data['fields'].get('tickets_registrados', {}).get('integerValue', 0),
                    'timestamp': data['fields'].get('timestamp', {}).get('timestampValue', '')
                }
        elif response.status_code == 404:
            return None
        else:
            return None
            
    except:
        return None

def update_points_via_rest(uid, delta):
    """Actualizar puntos"""
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

def registrar_ticket_compra(uid, monto_compra, numero_ticket):
    """Registrar ticket de compra y calcular puntos (5 puntos por cada 5$)"""
    try:
        perfil = get_profile_via_rest(uid)
        if perfil:
            # Calcular puntos ganados (5 puntos por cada 5$)
            puntos_ganados = (monto_compra // 5) * 5
            nuevo_total_compras = perfil.get('total_compras', 0) + monto_compra
            nuevos_tickets = perfil.get('tickets_registrados', 0) + 1
            nuevos_puntos = perfil.get('puntos', 0) + puntos_ganados
            
            url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
            update_data = {
                "fields": {
                    "puntos": {"integerValue": nuevos_puntos},
                    "total_compras": {"doubleValue": nuevo_total_compras},
                    "tickets_registrados": {"integerValue": nuevos_tickets}
                }
            }
            
            response = requests.patch(url, json=update_data)
            
            if response.status_code == 200:
                # Guardar histórico del ticket
                ticket_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}/tickets/{numero_ticket}"
                ticket_data = {
                    "fields": {
                        "monto": {"doubleValue": monto_compra},
                        "puntos_ganados": {"integerValue": puntos_ganados},
                        "fecha": {"timestampValue": datetime.utcnow().isoformat() + "Z"},
                        "numero_ticket": {"stringValue": numero_ticket}
                    }
                }
                requests.patch(ticket_url, json=ticket_data)
                
            return puntos_ganados if response.status_code == 200 else 0
        return 0
    except:
        return 0

# ==================================================
# INTERFAZ MEJORADA - DISEÑO ELEGANTE
# ==================================================

st.set_page_config(
    page_title="Arte París - Dulces Franceses", 
    page_icon="🎨", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para mejor diseño
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Arial', sans-serif;
    }
    .welcome-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    .point-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        margin: 1rem 0;
    }
    .ticket-card {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# Header principal con logo y bienvenida
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown('<div class="welcome-section">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; color: white;">🎨 Arte París</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: white;">Dulces Franceses Artesanales</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Mostrar imágenes de dulces franceses
st.subheader("🍬 Nuestra Exquisitez Francesa")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.image("https://images.unsplash.com/photo-1558326560-355b61cf86f7?w=200", caption="Macarons Artesanales")
with col2:
    st.image("https://images.unsplash.com/photo-1571115764595-644a1f56a55c?w=200", caption="Éclairs de Chocolate")
with col3:
    st.image("https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=200", caption="Croissants Mantecosos")
with col4:
    st.image("https://images.unsplash.com/photo-1511512571111-0d6c50f5acab?w=200", caption="Profiteroles Clásicos")

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
    
    st.success(f"✨ ¡Bienvenido a Arte París, {user_info['email']}!")
    
    # Obtener perfil
    perfil = get_profile_via_rest(uid)
    
    if perfil:
        # Tarjeta de puntos y estadísticas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="point-card">
                <h3>⭐ Puntos Acumulados</h3>
                <h2 style="color: #FF6B6B;">{perfil['puntos']} Puntos</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="point-card">
                <h3>💰 Total en Compras</h3>
                <h2 style="color: #4ECDC4;">${perfil['total_compras']:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="point-card">
                <h3>🎫 Tickets Registrados</h3>
                <h2 style="color: #45B7D1;">{perfil['tickets_registrados']}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Sección de gestión de puntos
        st.subheader("🎯 Gestión de Puntos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎁 +10 Puntos Extra", use_container_width=True, help="Gana puntos adicionales"):
                new_points = update_points_via_rest(uid, 10)
                st.success(f"¡+10 puntos! Ahora tienes {new_points} puntos!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Canjear 50 Puntos", use_container_width=True, help="Canjea por productos especiales"):
                if perfil['puntos'] >= 50:
                    new_points = update_points_via_rest(uid, -50)
                    st.success(f"✅ ¡Canje exitoso! Puntos restantes: {new_points}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Puntos insuficientes. Necesitas 50 puntos para canjear.")
        
        # NUEVA SECCIÓN: Registro de tickets de compra
        st.subheader("🛍️ Registrar Ticket de Compra")
        
        with st.form("ticket_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                numero_ticket = st.text_input("Número de Ticket", placeholder="Ej: TKT-001")
                monto_compra = st.number_input("Monto de la Compra ($)", min_value=0.0, step=0.5)
            
            with col2:
                st.info("""
                **💡 Sistema de Puntos:**
                - Por cada $5 de compra: **+5 puntos**
                - Ejemplo: $15 = 15 puntos
                - $22 = 20 puntos
                """)
            
            if st.form_submit_button("📥 Registrar Compra"):
                if numero_ticket and monto_compra > 0:
                    puntos_ganados = registrar_ticket_compra(uid, monto_compra, numero_ticket)
                    if puntos_ganados > 0:
                        st.success(f"""
                        ✅ **¡Ticket registrado exitosamente!**
                        
                        - **Monto:** ${monto_compra:.2f}
                        - **Puntos ganados:** +{puntos_ganados} puntos
                        - **Total acumulado:** {perfil['puntos'] + puntos_ganados} puntos
                        """)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error al registrar el ticket")
                else:
                    st.warning("⚠️ Completa todos los campos correctamente")
        
        # Información del perfil
        with st.expander("👤 Ver Información de Perfil"):
            st.write(f"**Nombre:** {perfil['nombre']}")
            st.write(f"**Email:** {perfil['email']}")
            st.write(f"**Miembro desde:** {perfil['timestamp'][:10] if perfil['timestamp'] else 'N/A'}")
    
    else:
        st.warning("⚠️ Perfil no encontrado en Firestore")
        
        if st.button("🔄 Reintentar carga de perfil"):
            st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()

else:
    # === USUARIO NO LOGUEADO ===
    st.subheader("🔐 Acceso al Sistema de Fidelidad")
    
    tab1, tab2 = st.tabs(["🚀 Iniciar Sesión", "📝 Crear Cuenta"])
    
    with tab1:
        st.info("¿Ya eres miembro? Inicia sesión para acumular puntos")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="tu@email.com")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("🎯 Ingresar a Mi Cuenta"):
                if email and password:
                    try:
                        user_info = login_user(email, password)
                        st.session_state.user = user_info
                        st.success("✅ ¡Bienvenido de nuevo!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                else:
                    st.warning("⚠️ Completa todos los campos")
    
    with tab2:
        st.success("✨ **¡Nuevo miembro! Recibe 10 puntos de regalo al registrarte**")
        with st.form("registro_form"):
            nombre = st.text_input("Nombre completo", placeholder="Juan Pérez")
            email = st.text_input("Email", placeholder="juan@email.com")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("🎁 Crear Cuenta con 10 Puntos de Regalo"):
                if nombre and email and password:
                    try:
                        user_info = signup_user(email, password, nombre)
                        st.session_state.user = user_info
                        st.balloons()
                        st.success("""
                        ✅ ¡Cuenta creada exitosamente!
                        
                        **🎁 ¡Recibiste 10 puntos de bienvenida!**
                        
                        Ahora puedes:
                        - Registrar tus compras para ganar más puntos
                        - Canjear puntos por deliciosos productos
                        - Acceder a ofertas exclusivas
                        """)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                else:
                    st.warning("⚠️ Completa todos los campos")

# ==================================================
# PANEL DE CONFIGURACIÓN MEJORADO
# ==================================================

with st.sidebar:
    st.header("🎨 Arte París")
    st.image("https://images.unsplash.com/photo-1558326560-355b61cf86f7?w=150", caption="Dulces con Amor Francés")
    
    st.markdown("---")
    st.header("🔧 Configuración Técnica")
    
    if st.button("🔄 Verificar Conexión Firebase"):
        try:
            test_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_CONFIG['API_KEY']}"
            response = requests.post(test_url, json={"returnSecureToken": True})
            if response.status_code != 400:
                st.success("✅ Firebase: CONECTADO")
            else:
                st.error("❌ Firebase: ERROR")
        except:
            st.error("❌ No se pudo conectar a Firebase")
    
    st.markdown("---")
    st.header("📋 Sistema de Puntos")
    
    st.info("""
    **⭐ Cómo ganar puntos:**
    - **Registro:** 10 puntos de bienvenida
    - **Compras:** 5 puntos por cada $5 gastados
    - **Promociones:** Puntos extra periódicos
    
    **🎁 Cómo canjear:**
    - 50 puntos: Producto pequeño
    - 100 puntos: Producto mediano  
    - 200 puntos: Producto premium
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>💎 <strong>Arte París</strong> - Dulces Franceses Artesanales | Sistema de Fidelización</p>
    <p>📍 Donde cada bocado es una experiencia francesa</p>
</div>
""", unsafe_allow_html=True)
