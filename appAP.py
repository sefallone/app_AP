# ==================================================
# IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ==================================================
import streamlit as st
import requests
import json
import time
from datetime import datetime, date
from streamlit_option_menu import option_menu

# ==================================================
# CONFIGURACIÓN FIREBASE - REEMPLAZAR CON TUS DATOS
# ==================================================
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# DATOS DE PRODUCTOS
# ==================================================
PRODUCTOS = [
    {
        "nombre": "Caja de Macarons Surpresa",
        "puntos": 50,
        "precio_original": 25.00,
        "imagen": "https://images.unsplash.com/photo-1558326560-355b61cf86f7?w=300",
        "categoria": "clasico"
    },
    {
        "nombre": "Éclair de Temporada",
        "puntos": 30,
        "precio_original": 12.00,
        "imagen": "https://images.unsplash.com/photo-1571115764595-644a1f56a55c?w=300",
        "categoria": "clasico"
    },
    {
        "nombre": "Croissant Artístico",
        "puntos": 25,
        "precio_original": 8.00,
        "imagen": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=300",
        "categoria": "panaderia"
    }
]

# ==================================================
# CONFIGURACIÓN DE PÁGINA
# ==================================================
st.set_page_config(
    page_title="Arte París Delicafé",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================================================
# CSS MEJORADO
# ==================================================
st.markdown("""
<style>
    .main > div {
        padding: 0.5rem;
    }
    
    .hero-section {
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .logo-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem auto;
        max-width: 200px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .mobile-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border: 2px solid #f8f9fa;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    
    .point-card-mobile {
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 25px;
        font-weight: bold;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# FUNCIONES FIREBASE - VERSIÓN SIMPLIFICADA Y ROBUSTA
# ==================================================
def login_user(email, password):
    """Login simplificado"""
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

def signup_user(email, password, nombre, fecha_cumpleanos=None):
    """Registro simplificado"""
    try:
        # Primero registrar en Authentication
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
            # Luego guardar perfil en Firestore
            save_profile_via_rest(result['localId'], nombre, email, fecha_cumpleanos, 10)
            return result
        else:
            error_msg = result.get('error', {}).get('message', 'Error desconocido')
            raise Exception(f"Registro falló: {error_msg}")
    except Exception as e:
        raise Exception(f"Error en registro: {str(e)}")

def save_profile_via_rest(uid, nombre, email, fecha_cumpleanos=None, bonus_points=0):
    """Guardar perfil de manera robusta"""
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
        
        if fecha_cumpleanos:
            document_data["fields"]["fecha_cumpleanos"] = {
                "timestampValue": fecha_cumpleanos.isoformat() + "T00:00:00Z"
            }
        
        response = requests.patch(url, json=document_data)
        return response.status_code == 200
    except:
        return False

def get_profile_via_rest(uid):
    """Obtener perfil con manejo de errores mejorado"""
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'fields' in data:
                profile_data = {
                    'nombre': data['fields'].get('nombre', {}).get('stringValue', 'Usuario'),
                    'email': data['fields'].get('email', {}).get('stringValue', ''),
                    'puntos': int(data['fields'].get('puntos', {}).get('integerValue', 0)),
                    'total_compras': float(data['fields'].get('total_compras', {}).get('doubleValue', 0.0)),
                    'tickets_registrados': int(data['fields'].get('tickets_registrados', {}).get('integerValue', 0))
                }
                
                # Manejar fecha de cumpleaños
                if 'fecha_cumpleanos' in data['fields']:
                    fecha_str = data['fields']['fecha_cumpleanos'].get('timestampValue', '')
                    if fecha_str:
                        try:
                            fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                            profile_data['fecha_cumpleanos'] = fecha_dt.date()
                        except:
                            profile_data['fecha_cumpleanos'] = None
                
                return profile_data
        return None
    except Exception as e:
        st.error(f"Error cargando perfil: {e}")
        return None

def update_points_via_rest(uid, delta):
    """Actualizar puntos simplificado"""
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
# MANEJO DE SESIÓN
# ==================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "profile" not in st.session_state:
    st.session_state.profile = None

# ==================================================
# INTERFAZ PRINCIPAL
# ==================================================
if st.session_state.user:
    # DEBUG: Mostrar información de sesión
    st.write("🔍 Debug - Usuario en sesión:", st.session_state.user.get('email', 'No email'))
    
    user_info = st.session_state.user
    uid = user_info["localId"]
    
    # Cargar perfil una vez por sesión
    if st.session_state.profile is None:
        with st.spinner("Cargando tu perfil..."):
            st.session_state.profile = get_profile_via_rest(uid)
    
    perfil = st.session_state.profile
    
    if perfil:
        puntos_usuario = perfil.get('puntos', 0)
        
        # NAVEGACIÓN
        with st.container():
            selected = option_menu(
                menu_title=None,
                options=["Inicio", "Productos", "Perfil"],
                icons=["house", "gift", "person"],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                    "icon": {"color": "#8B4513", "font-size": "12px"}, 
                    "nav-link": {"font-size": "12px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#8B4513"},
                }
            )
        
        # PÁGINA DE INICIO
        if selected == "Inicio":
            st.markdown("""
            <div class="hero-section">
                <div class="logo-container">
                    <h2 style="color: #8B4513; margin: 0; font-family: 'Brush Script MT', cursive;">Ait Paris</h2>
                    <h3 style="color: #D2691E; margin: 0; font-size: 1.2rem;">DELICAFÉ</h3>
                </div>
                <h3 style="margin: 1rem 0 0 0; font-style: italic;">Donde el café se encuentra con el arte</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Tarjeta de puntos
            st.markdown(f"""
            <div class="point-card-mobile">
                <h3>⭐ Tus Puntos Delicafé</h3>
                <h1 style="font-size: 3rem; margin: 0;">{puntos_usuario}</h1>
                <p>Puntos acumulados</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Bienvenida personal
            st.success(f"✨ ¡Bienvenido/a {perfil['nombre']}!")
            
            # Acciones rápidas
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Registrar Compra", use_container_width=True):
                    st.info("Ve a la pestaña 'Perfil' para registrar compras")
            with col2:
                if st.button("🎁 Ver Productos", use_container_width=True):
                    st.experimental_set_query_params(tab="Productos")
                    st.rerun()
            
            # Productos destacados
            st.subheader("🛍️ Productos Destacados")
            for producto in PRODUCTOS[:2]:
                with st.container():
                    st.markdown(f"""
                    <div class="mobile-card">
                        <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
                        <p><small>${producto['precio_original']} valor</small></p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # PÁGINA DE PRODUCTOS
        elif selected == "Productos":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #8B4513; margin: 0;">🎁 Productos Delicafé</h2>
                <p style="color: #666;">Canjea tus puntos por experiencias únicas</p>
            </div>
            """, unsafe_allow_html=True)
            
            for producto in PRODUCTOS:
                with st.container():
                    disponible = puntos_usuario >= producto['puntos']
                    st.markdown(f"""
                    <div class="mobile-card" style="opacity: {'1' if disponible else '0.7'};">
                        <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
                        {"✅ DISPONIBLE" if disponible else f"❌ Te faltan {producto['puntos'] - puntos_usuario} puntos"}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if disponible and st.button(f"Canjear {producto['puntos']} pts", key=f"canjear_{producto['nombre']}", use_container_width=True):
                        nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                        if nuevos_puntos >= 0:
                            st.success(f"¡Canjeado! {producto['nombre']}")
                            st.session_state.profile = None  # Forzar recarga
                            time.sleep(2)
                            st.rerun()
        
        # PÁGINA DE PERFIL
        elif selected == "Perfil":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #8B4513; margin: 0;">👤 Tu Perfil</h2>
                <p style="color: #666;">Gestiona tu cuenta Delicafé</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Información del perfil
            st.markdown(f"""
            <div class="mobile-card">
                <h4>👋 Hola, {perfil['nombre']}</h4>
                <p>📧 {perfil['email']}</p>
                <p>⭐ {puntos_usuario} puntos</p>
                <p>💰 ${perfil.get('total_compras', 0):.2f} gastados</p>
                <p>🎫 {perfil.get('tickets_registrados', 0)} tickets</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Registrar compra
            st.subheader("📥 Registrar Compra")
            with st.form("compra_form"):
                numero_ticket = st.text_input("Número de Ticket")
                monto_compra = st.number_input("Monto ($)", min_value=0.0, step=0.5)
                
                if st.form_submit_button("Registrar Compra", use_container_width=True):
                    if numero_ticket and monto_compra > 0:
                        # Simular registro de compra
                        nuevos_puntos = update_points_via_rest(uid, int(monto_compra))
                        if nuevos_puntos > puntos_usuario:
                            st.success(f"¡Compra registrada! +{int(monto_compra)} puntos")
                            st.session_state.profile = None  # Forzar recarga
                            time.sleep(2)
                            st.rerun()
            
            # Cerrar sesión
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.user = None
                st.session_state.profile = None
                st.rerun()
    
    else:
        st.error("❌ No se pudo cargar el perfil. Por favor, recarga la página.")
        if st.button("🔄 Recargar"):
            st.session_state.profile = None
            st.rerun()

# ==================================================
# INTERFAZ DE LOGIN (NO LOGUEADO)
# ==================================================
else:
    st.markdown("""
    <div class="hero-section">
        <div class="logo-container">
            <h2 style="color: #8B4513; margin: 0; font-family: 'Brush Script MT', cursive;">Ait Paris</h2>
            <h3 style="color: #D2691E; margin: 0; font-size: 1.2rem;">DELICAFÉ</h3>
        </div>
        <h3 style="margin: 1rem 0 0 0; font-style: italic;">Donde el café se encuentra con el arte</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400", 
             caption="🎨 Cada taza es una experiencia artística")
    
    tab1, tab2 = st.tabs(["🚀 Ingresar", "📝 Crear Cuenta"])
    
    with tab1:
        st.subheader("Bienvenido de vuelta")
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Contraseña", type="password")
            
            if st.form_submit_button("🎯 Ingresar", use_container_width=True):
                if email and password:
                    try:
                        user_info = login_user(email, password)
                        st.session_state.user = user_info
                        st.success("¡Bienvenido!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with tab2:
        st.subheader("Únete a Nosotros")
        with st.form("registro_form"):
            nombre = st.text_input("👤 Nombre completo")
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Contraseña", type="password")
            fecha_cumpleanos = st.date_input("🎂 Fecha de Cumpleaños (opcional)")
            
            if st.form_submit_button("🎨 Registrarse", use_container_width=True):
                if nombre and email and password:
                    try:
                        user_info = signup_user(email, password, nombre, fecha_cumpleanos)
                        st.session_state.user = user_info
                        st.success("¡Cuenta creada! 10 puntos de regalo")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">'
    '☕ <strong>Ait Paris Delicafé</strong> - Donde cada taza cuenta una historia 🎨'
    '</div>',
    unsafe_allow_html=True
)
