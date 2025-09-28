# ==================================================
# IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ==================================================
import streamlit as st
import requests
import json
import time
from datetime import datetime, date
from streamlit_option_menu import option_menu
from PIL import Image
import base64

# ==================================================
# CONFIGURACIÓN FIREBASE - REEMPLAZAR CON TUS DATOS
# ==================================================
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# DATOS DE PRODUCTOS - MODIFICAR SEGÚN TUS PRODUCTOS
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
    },
    {
        "nombre": "Café Especial Arte París",
        "puntos": 15,
        "precio_original": 5.00,
        "imagen": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300",
        "categoria": "bebida"
    },
    {
        "nombre": "Tarta de Frambuesa",
        "puntos": 80,
        "precio_original": 35.00,
        "imagen": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=300",
        "categoria": "especial"
    }
]

# ==================================================
# OFERTAS ESPECIALES - MODIFICAR SEGÚN TUS OFERTAS
# ==================================================
OFERTAS_ESPECIALES = [
    {
        "titulo": "🎁 Regalo de Cumpleaños",
        "descripcion": "Café especial + Dulce sorpresa para tu día",
        "puntos": 0,
        "imagen": "https://images.unsplash.com/photo-1535254973040-607b474cb50d?w=300",
        "exclusivo": True,
        "cumpleanos": True
    },
    {
        "titulo": "☕ Combo Mañana Francesa",
        "descripcion": "Café + Croissant + Macaron",
        "puntos": 65,
        "imagen": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=300",
        "exclusivo": True
    }
]

# ==================================================
# FUNCIÓN: REGISTRAR USUARIO - CON CAMPO DE CUMPLEAÑOS
# ==================================================
def signup_user(email, password, nombre, fecha_cumpleanos=None):
    """Registrar usuario con bono de 10 puntos y fecha de cumpleaños"""
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
            # Guardar perfil con bono de 10 puntos y fecha de cumpleaños
            time.sleep(1)
            save_profile_via_rest(result['localId'], nombre, email, fecha_cumpleanos, bonus_points=10)
            return result
        else:
            error_msg = result.get('error', {}).get('message', 'Error desconocido')
            raise Exception(f"Registro falló: {error_msg}")
            
    except Exception as e:
        raise Exception(f"Error en registro: {str(e)}")

# ==================================================
# FUNCIÓN: LOGIN USUARIO
# ==================================================
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

# ==================================================
# FUNCIÓN: GUARDAR PERFIL - CON CAMPO DE CUMPLEAÑOS
# ==================================================
def save_profile_via_rest(uid, nombre, email, fecha_cumpleanos=None, bonus_points=0):
    """Guardar perfil con puntos de bono y fecha de cumpleaños"""
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        
        # Preparar datos del documento
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
        
        # Agregar fecha de cumpleaños si está presente
        if fecha_cumpleanos:
            document_data["fields"]["fecha_cumpleanos"] = {
                "timestampValue": fecha_cumpleanos.isoformat() + "T00:00:00Z"
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

# ==================================================
# FUNCIÓN: OBTENER PERFIL - CON CAMPO DE CUMPLEAÑOS
# ==================================================
def get_profile_via_rest(uid):
    """Obtener perfil con información extendida incluyendo cumpleaños"""
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'fields' in data:
                profile_data = {
                    'nombre': data['fields'].get('nombre', {}).get('stringValue', ''),
                    'email': data['fields'].get('email', {}).get('stringValue', ''),
                    'puntos': data['fields'].get('puntos', {}).get('integerValue', 0),
                    'total_compras': data['fields'].get('total_compras', {}).get('doubleValue', 0.0),
                    'tickets_registrados': data['fields'].get('tickets_registrados', {}).get('integerValue', 0),
                    'timestamp': data['fields'].get('timestamp', {}).get('timestampValue', '')
                }
                
                # Agregar fecha de cumpleaños si existe
                if 'fecha_cumpleanos' in data['fields']:
                    fecha_str = data['fields']['fecha_cumpleanos'].get('timestampValue', '')
                    if fecha_str:
                        try:
                            # Convertir de timestamp a date
                            fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                            profile_data['fecha_cumpleanos'] = fecha_dt.date()
                        except:
                            profile_data['fecha_cumpleanos'] = None
                
                return profile_data
        elif response.status_code == 404:
            return None
        else:
            return None
            
    except:
        return None

# ==================================================
# FUNCIÓN: VERIFICAR CUMPLEAÑOS
# ==================================================
def es_cumpleanos_hoy(fecha_cumpleanos):
    """Verificar si hoy es el cumpleaños del usuario"""
    if not fecha_cumpleanos:
        return False
    
    hoy = date.today()
    return fecha_cumpleanos.month == hoy.month and fecha_cumpleanos.day == hoy.day

# ==================================================
# FUNCIÓN: ACTUALIZAR PUNTOS
# ==================================================
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

# ==================================================
# FUNCIÓN: REGISTRAR TICKET COMPRA
# ==================================================
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
# CONFIGURACIÓN PARA MÓVIL
# ==================================================
st.set_page_config(
    page_title="Arte París Delicafé",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================================================
# CSS PARA MÓVIL MEJORADO
# ==================================================
st.markdown("""
<style>
    /* Estilos móviles mejorados */
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
        box-shadow: 0 10px 30px rgba(139, 69, 19, 0.3);
    }
    
    .logo-container {
        background: white;
        border-radius: 20px;
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
        box-shadow: 0 5px 15px rgba(139, 69, 19, 0.3);
    }
    
    .birthday-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
        border: 2px solid #FF6B6B;
    }
    
    .coffee-card {
        background: linear-gradient(135deg, #4A3520 0%, #8B4513 100%);
        padding: 1rem;
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
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(139, 69, 19, 0.4);
    }
    
    .benefit-item {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: #FFF8F0;
        border-radius: 10px;
        border-left: 4px solid #D2691E;
    }
    
    /* Ocultar elementos no esenciales para móvil */
    .css-1d391kg { 
        display: none; 
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# VERIFICACIÓN CONFIGURACIÓN FIREBASE
# ==================================================
if not FIREBASE_CONFIG["API_KEY"] or FIREBASE_CONFIG["API_KEY"] == "tu_api_key_aqui":
    st.error("❌ Configura la API_KEY de Firebase en el código")
    st.stop()

# ==================================================
# MANEJO DE SESIÓN USUARIO
# ==================================================
if "user" not in st.session_state:
    st.session_state.user = None

# ==================================================
# INTERFAZ PRINCIPAL PARA MÓVIL
# ==================================================
if st.session_state.user:
    user_info = st.session_state.user
    uid = user_info["localId"]
    
    # Obtener perfil
    perfil = get_profile_via_rest(uid)
    
    if perfil:
        # VALIDACIÓN SEGURA DE PUNTOS
        try:
            puntos_usuario = int(perfil.get('puntos', 0))
        except (TypeError, ValueError):
            puntos_usuario = 0
        
        # NAVEGACIÓN MÓVIL
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
            # Hero Section con logo
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
            
            # Verificar cumpleaños
            fecha_cumpleanos = perfil.get('fecha_cumpleanos')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.markdown(f"""
                <div class="birthday-card">
                    <h3>🎉 ¡Feliz Cumpleaños!</h3>
                    <p>¡Hoy es tu día especial! Disfruta de regalos exclusivos</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Imagen de café inspiradora
            st.image("https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400", 
                    caption="☕ Nuestro café especial - Una obra de arte en cada taza")
            
            # Acciones rápidas
            st.subheader("🚀 Acciones Rápidas")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Registrar Compra", use_container_width=True):
                    st.session_state.registrar_compra = True
            with col2:
                if st.button("🎁 Canjear Puntos", use_container_width=True):
                    st.session_state.canjear_puntos = True
            
            # Productos destacados
            st.subheader("🛍️ Destacados del Mes")
            for producto in PRODUCTOS[:2]:
                with st.container():
                    st.markdown(f"""
                    <div class="mobile-card">
                        <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
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
            
            # Ofertas de cumpleaños
            fecha_cumpleanos = perfil.get('fecha_cumpleanos')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.markdown(f"""
                <div class="birthday-card">
                    <h3>🎁 Regalo de Cumpleaños</h3>
                    <p>¡Café especial + Dulce sorpresa para celebrar contigo!</p>
                    <h4>¡GRATIS en tu cumpleaños!</h4>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🎁 Reclamar Regalo de Cumpleaños", use_container_width=True, key="cumpleanos"):
                    st.success("¡Regalo reclamado! Presenta esta pantalla en tienda para recibir tu sorpresa")
            
            # Todos los productos
            st.subheader("☕ Nuestra Carta")
            for producto in PRODUCTOS:
                with st.container():
                    disponible = puntos_usuario >= producto['puntos']
                    st.markdown(f"""
                    <div class="mobile-card" style="opacity: {'1' if disponible else '0.7'};">
                        <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
                        <p><small>Valor: ${producto['precio_original']}</small></p>
                        {"✅ DISPONIBLE" if disponible else f"❌ Te faltan {producto['puntos'] - puntos_usuario} puntos"}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if disponible and st.button(f"Canjear {producto['puntos']} pts", key=f"canjear_{producto['nombre']}", use_container_width=True):
                        nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                        if nuevos_puntos >= 0:
                            st.success(f"¡Canjeado exitosamente! Disfruta de: {producto['nombre']}")
                            st.balloons()
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
                <p>⭐ {puntos_usuario} puntos acumulados</p>
                <p>{"🎂 Cumpleaños: " + perfil['fecha_cumpleanos'].strftime('%d/%m/%Y') if perfil.get('fecha_cumpleanos') else "🎂 Agrega tu fecha de cumpleaños"}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Estadísticas
            st.subheader("📊 Tu Trayectoria Delicafé")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Gastado", f"${perfil.get('total_compras', 0):.2f}")
            with col2:
                st.metric("Tickets Registrados", perfil.get('tickets_registrados', 0))
            
            # Sistema de niveles
            st.subheader("🏆 Tu Nivel")
            if puntos_usuario < 50:
                nivel = "☕ Aprendiz del Café"
                progreso = puntos_usuario / 50
            elif puntos_usuario < 100:
                nivel = "⭐ Barista"
                progreso = (puntos_usuario - 50) / 50
            elif puntos_usuario < 200:
                nivel = "👑 Maestro Cafetero"
                progreso = (puntos_usuario - 100) / 100
            else:
                nivel = "💎 Leyenda Delicafé"
                progreso = 1.0
            
            st.progress(progreso)
            st.write(f"**{nivel}** - {puntos_usuario} puntos")
            
            # Registrar compra
            st.subheader("📥 Registrar Nueva Compra")
            with st.form("compra_form"):
                numero_ticket = st.text_input("Número de Ticket", placeholder="TKT-001")
                monto_compra = st.number_input("Monto de la Compra ($)", min_value=0.0, step=0.5, value=0.0)
                
                if st.form_submit_button("📥 Registrar Compra y Ganar Puntos", use_container_width=True):
                    if numero_ticket.strip() and monto_compra > 0:
                        puntos_ganados = registrar_ticket_compra(uid, monto_compra, numero_ticket)
                        if puntos_ganados > 0:
                            st.success(f"✅ ¡Compra registrada! Ganaste {puntos_ganados} puntos")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Error al registrar la compra")
                    else:
                        st.warning("⚠️ Ingresa un número de ticket y monto válidos")
            
            # Cerrar sesión
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.user = None
                st.rerun()

# ==================================================
# INTERFAZ DE LOGIN/CREAR CUENTA MEJORADA
# ==================================================
else:
    # Hero Section para login
    st.markdown("""
    <div class="hero-section">
        <div class="logo-container">
            <h2 style="color: #8B4513; margin: 0; font-family: 'Brush Script MT', cursive;">Ait Paris</h2>
            <h3 style="color: #D2691E; margin: 0; font-size: 1.2rem;">DELICAFÉ</h3>
        </div>
        <h3 style="margin: 1rem 0 0 0; font-style: italic;">Donde el café se encuentra con el arte</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Imagen atractiva de café
    st.image("https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400", 
             caption="🎨 Cada taza es una experiencia artística")
    
    tab1, tab2 = st.tabs(["🚀 Ingresar", "📝 Crear Cuenta"])
    
    with tab1:
        st.subheader("Bienvenido de vuelta")
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="tu@email.com")
            password = st.text_input("🔒 Contraseña", type="password")
            
            if st.form_submit_button("🎯 Ingresar a Mi Cuenta", use_container_width=True):
                if email and password:
                    try:
                        user_info = login_user(email, password)
                        st.session_state.user = user_info
                        st.success("¡Bienvenido de vuelta a Delicafé!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Por favor completa todos los campos")
    
    with tab2:
        st.subheader("Únete a la Familia Delicafé")
        st.info("🎁 **¡Regístrate y recibe 10 puntos de bienvenida!**")
        
        with st.form("registro_form"):
            nombre = st.text_input("👤 Nombre completo", placeholder="Claude Monet")
            email = st.text_input("📧 Email", placeholder="claude@arteparis.com")
            password = st.text_input("🔒 Contraseña", type="password")
            fecha_cumpleanos = st.date_input(
                "🎂 Fecha de Cumpleaños (opcional)",
                value=None,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="¡Recibe regalos especiales en tu cumpleaños!"
            )
            
            if st.form_submit_button("🎨 Unirme a Delicafé", use_container_width=True):
                if nombre and email and password:
                    try:
                        user_info = signup_user(email, password, nombre, fecha_cumpleanos)
                        st.session_state.user = user_info
                        st.balloons()
                        st.success("""
                        🎉 ¡Bienvenido a nuestra familia Delicafé!
                        
                        **🎁 Recibiste 10 puntos de bienvenida**
                        
                        Ahora puedes:
                        - Canjear puntos por experiencias únicas
                        - Acceder a ofertas exclusivas
                        - Recibir regalos en tu cumpleaños
                        """)
                        time.sleep(3)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Por favor completa los campos obligatorios")
    
    # Beneficios section
    st.markdown("---")
    st.subheader("⭐ Beneficios Exclusivos")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="benefit-item">
            <span>☕ 5 puntos por cada $5</span>
        </div>
        <div class="benefit-item">
            <span>🎁 Regalos cumpleaños</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="benefit-item">
            <span>⭐ Ofertas exclusivas</span>
        </div>
        <div class="benefit-item">
            <span>👑 Trato preferencial</span>
        </div>
        """, unsafe_allow_html=True)

# ==================================================
# FOOTER MÓVIL MEJORADO
# ==================================================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">'
    '☕ <strong>Ait Paris Delicafé</strong> - Donde cada taza cuenta una historia 🎨'
    '</div>',
    unsafe_allow_html=True
)
