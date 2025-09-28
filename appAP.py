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
import os

# ==================================================
# CONFIGURACIÓN FIREBASE
# ==================================================
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# CONFIGURACIÓN DE IMÁGENES LOCALES
# ==================================================
# NOTA: Coloca estos archivos en la misma carpeta que tu script
CONFIG_IMAGENES = {
    "logo": "LogoAP.jpg",           # Tu logo principal
    "hero": "Cafe1.jpg",       # Imagen hero principal
    "productos": {
        "macarons": "Milhojas.jpg",
        "eclair": "Brazo.jpg",
        "croissant": "Croissant.jpg",
        "cafe_especial": "Cafe.jpg",
        "tarta_frambuesa": "Profiterol.jpg"
    },
    "ofertas": {
        "cumpleanos": "Brazo.jpg",
        "combo": "Tartaletafresa1.jpg"
    }
}

# ==================================================
# DATOS DE PRODUCTOS CON IMÁGENES LOCALES
# ==================================================
PRODUCTOS = [
    {
        "nombre": "Caja de Macarons Surpresa",
        "puntos": 50,
        "precio_original": 25.00,
        "imagen": CONFIG_IMAGENES["productos"]["macarons"],
        "categoria": "clasico"
    },
    {
        "nombre": "Éclair de Temporada",
        "puntos": 30,
        "precio_original": 12.00,
        "imagen": CONFIG_IMAGENES["productos"]["eclair"],
        "categoria": "clasico"
    },
    {
        "nombre": "Croissant Artístico",
        "puntos": 25,
        "precio_original": 8.00,
        "imagen": CONFIG_IMAGENES["productos"]["croissant"],
        "categoria": "panaderia"
    },
    {
        "nombre": "Café Especial Arte París",
        "puntos": 15,
        "precio_original": 5.00,
        "imagen": CONFIG_IMAGENES["productos"]["cafe_especial"],
        "categoria": "bebida"
    },
    {
        "nombre": "Tarta de Frambuesa",
        "puntos": 80,
        "precio_original": 35.00,
        "imagen": CONFIG_IMAGENES["productos"]["tarta_frambuesa"],
        "categoria": "especial"
    }
]

# ==================================================
# OFERTAS ESPECIALES CON IMÁGENES LOCALES
# ==================================================
OFERTAS_ESPECIALES = [
    {
        "titulo": "🎁 Regalo de Cumpleaños",
        "descripcion": "Café especial + Dulce sorpresa para tu día",
        "puntos": 0,
        "imagen": CONFIG_IMAGENES["ofertas"]["cumpleanos"],
        "exclusivo": True,
        "cumpleanos": True
    },
    {
        "titulo": "☕ Combo Mañana Francesa",
        "descripcion": "Café + Croissant + Macaron",
        "puntos": 65,
        "imagen": CONFIG_IMAGENES["ofertas"]["combo"],
        "exclusivo": True
    }
]

# ==================================================
# FUNCIONES PARA MANEJO DE IMÁGENES LOCALES
# ==================================================
def cargar_imagen_local(ruta_imagen, ancho_maximo=400):
    """
    Carga una imagen local y la muestra en Streamlit
    Si no encuentra la imagen, muestra un placeholder
    """
    try:
        if os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            st.image(imagen, use_container_width =True)
            return True
        else:
            st.error(f"❌ No se encontró: {ruta_imagen}")
            # Placeholder genérico
            st.image("https://via.placeholder.com/300x200/8B4513/FFFFFF?text=Imagen+No+Encontrada", 
                    use_container_width =True)
            return False
    except Exception as e:
        st.error(f"❌ Error cargando imagen: {e}")
        return False

def mostrar_logo():
    """
    Muestra el logo de la empresa
    """
    st.markdown("""
    <div style="text-align: center; background: white; padding: 1rem; border-radius: 15px; margin: 1rem 0;">
    """, unsafe_allow_html=True)
    
    if os.path.exists(CONFIG_IMAGENES["logo"]):
        logo = Image.open(CONFIG_IMAGENES["logo"])
        st.image(logo, use_container_width=True)
    else:
        st.markdown("""
        <h2 style="color: #8B4513; margin: 0; font-family: 'Brush Script MT', cursive;">Ait Paris</h2>
        <h3 style="color: #D2691E; margin: 0; font-size: 1.2rem;">ARTE PARÍS</h3>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# FUNCIONES FIREBASE
# ==================================================
def login_user(email, password):
    """Login con Firebase"""
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
    """Registro de usuario"""
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
            st.success("✅ Usuario registrado")
            time.sleep(1)
            save_profile_via_rest(result['localId'], nombre, email, fecha_cumpleanos, 10)
            return result
        else:
            error_msg = result.get('error', {}).get('message', 'Error desconocido')
            raise Exception(f"Registro falló: {error_msg}")
    except Exception as e:
        raise Exception(f"Error en registro: {str(e)}")

def save_profile_via_rest(uid, nombre, email, fecha_cumpleanos=None, bonus_points=0):
    """Guardar perfil en Firestore"""
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
    """Obtener perfil del usuario"""
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
    """Actualizar puntos del usuario"""
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
    """Registrar ticket de compra"""
    try:
        perfil = get_profile_via_rest(uid)
        if perfil:
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
            return puntos_ganados if response.status_code == 200 else 0
        return 0
    except:
        return 0

def es_cumpleanos_hoy(fecha_cumpleanos):
    """Verificar si hoy es cumpleaños"""
    if not fecha_cumpleanos:
        return False
    hoy = date.today()
    return fecha_cumpleanos.month == hoy.month and fecha_cumpleanos.day == hoy.day

# ==================================================
# CONFIGURACIÓN STREAMLIT
# ==================================================
st.set_page_config(
    page_title="Arte Paris Deli café",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================================================
# CSS PERSONALIZADO
# ==================================================
st.markdown("""
<style>
    .main > div {
        padding: 0.5rem;
    }
    .hero-section {
        background: linear-gradient(135deg, #46E0E0 0%, #38C7C7 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .mobile-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border: 2px solid #061B30;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
    }
    .point-card-mobile {
        background: linear-gradient(135deg, #46E0E0 0%, #46E0E0 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: black;
        text-align: center;
    }
    .birthday-card {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: black;
        text-align: center;
        border: 2px solid #FF6B6B;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #135454 0%, #135454 100%);
        color: black;
        border: none;
        padding: 0.75rem;
        border-radius: 25px;
        font-weight: bold;
        margin: 0.25rem 0;
    }
    .benefit-item {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        background: #46E0E0;
        border-radius: 10px;
        border-left: 4px solid #135454;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# MANEJO DE SESIÓN
# ==================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "profile" not in st.session_state:
    st.session_state.profile = None

# ==================================================
# INTERFAZ PRINCIPAL - USUARIO LOGUEADO
# ==================================================
if st.session_state.user:
    user_info = st.session_state.user
    uid = user_info["localId"]
    
    # Cargar perfil
    if st.session_state.profile is None:
        with st.spinner("Cargando tu perfil..."):
            st.session_state.profile = get_profile_via_rest(uid)
    
    perfil = st.session_state.profile
    
    if perfil:
        puntos_usuario = perfil.get('puntos', 0)
        
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
                    "icon": {"color": "#4EDED7", "font-size": "12px"}, 
                    "nav-link": {"font-size": "12px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#4EDED7"},
                }
            )
        
        # PÁGINA DE INICIO
        if selected == "Inicio":
            st.markdown("""
            <div class="hero-section">
                <h3 style="margin: 0; font-style: italic;">Lo convertimos en Arte</h3>
            </div>
            """, unsafe_allow_html=True)
            
            mostrar_logo()
            
            # Tarjeta de puntos
            st.markdown(f"""
            <div class="point-card-mobile">
                <h3>⭐ Tus Puntos ArteParís</h3>
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
            
            # Imagen principal local
            st.subheader("☕ Nuestra Esencia")
            cargar_imagen_local(CONFIG_IMAGENES["hero"], "🎨 Donde el café es arte")
            
            # Acciones rápidas
            st.subheader("🚀 Acciones Rápidas")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Registrar Compra", use_container_width=True):
                    st.info("📍 Ve a 'Perfil' para registrar tus compras")
            with col2:
                if st.button("🎁 Canjear Puntos", use_container_width=True):
                    st.info("📍 Ve a 'Productos' para canjear tus puntos")
            
            # Productos destacados
            st.subheader("🌟 Destacados")
            for producto in PRODUCTOS[:2]:
                with st.container():
                    st.markdown(f"""
                    <div class="mobile-card">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
                    </div>
                    """, unsafe_allow_html=True)
                    cargar_imagen_local(producto['imagen'])
        
        # PÁGINA DE PRODUCTOS
        elif selected == "Productos":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #3DCCC5; margin: 0;">🎁 Productos Arte París</h2>
                <p style="color: #666;">Canjea tus puntos por experiencias únicas</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Ofertas de cumpleaños
            fecha_cumpleanos = perfil.get('fecha_cumpleaños')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.markdown(f"""
                <div class="birthday-card">
                    <h3>🎁 ¡Regalo de Cumpleaños!</h3>
                    <p>Café especial + Dulce sorpresa</p>
                    <h4>¡GRATIS hoy!</h4>
                </div>
                """, unsafe_allow_html=True)
                cargar_imagen_local(OFERTAS_ESPECIALES[0]['imagen'])
                if st.button("🎁 Reclamar Mi Regalo", use_container_width=True):
                    st.success("¡Regalo reclamado! Muestra esta pantalla en tienda")
            
            # Todos los productos
            st.subheader("☕ Nuestra Carta")
            for producto in PRODUCTOS:
                with st.container():
                    disponible = puntos_usuario >= producto['puntos']
                    st.markdown(f"""
                    <div class="mobile-card" style="opacity: {'1' if disponible else '0.7'}">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
                        <p><small>Valor: ${producto['precio_original']}</small></p>
                        {"✅ DISPONIBLE" if disponible else f"❌ Te faltan {producto['puntos'] - puntos_usuario} puntos"}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    cargar_imagen_local(producto['imagen'])
                    
                    if disponible and st.button(f"Canjear {producto['puntos']} pts", 
                                              key=f"canjear_{producto['nombre']}", 
                                              use_container_width=True):
                        nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                        if nuevos_puntos >= 0:
                            st.success(f"¡Canjeado! {producto['nombre']}")
                            st.session_state.profile = None
                            time.sleep(2)
                            st.rerun()
        
        # PÁGINA DE PERFIL
        elif selected == "Perfil":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #3DCCC5; margin: 0;">👤 Tu Perfil</h2>
                <p style="color: #666;">Gestiona tu cuenta Arte París</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Información del perfil
            st.markdown(f"""
            <div class="mobile-card">
                <h4>👋 Hola, {perfil['nombre']}</h4>
                <p>📧 {perfil['email']}</p>
                <p>⭐ {puntos_usuario} puntos acumulados</p>
                <p>💰 ${perfil.get('total_compras', 0):.2f} gastados</p>
                <p>🎫 {perfil.get('tickets_registrados', 0)} tickets registrados</p>
                <p>{"🎂 " + perfil['fecha_cumpleanos'].strftime('%d/%m/%Y') if perfil.get('fecha_cumpleanos') else "🎂 Sin fecha de cumpleaños"}</p>
            </div>
            """, unsafe_allow_html=True)
            
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
                            st.session_state.profile = None
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
                st.session_state.profile = None
                st.rerun()

# ==================================================
# INTERFAZ DE LOGIN - NO LOGUEADO
# ==================================================
else:
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h3 style="margin: 0; font-style: italic;">Bienvenido a Arte Paris Deli Café</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Logo
    mostrar_logo()
    
    # Imagen principal local
    cargar_imagen_local(CONFIG_IMAGENES["hero"], "🎨 Donde el café es arte")
    
    # Tabs de login/registro
    tab1, tab2 = st.tabs(["🚀 Ingresar", "📝 Crear Cuenta"])
    
    with tab1:
        st.subheader("Bienvenido de vuelta")
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="tu@email.com")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Tu contraseña")
            
            if st.form_submit_button("🎯 Ingresar a Mi Cuenta", use_container_width=True):
                if email and password:
                    try:
                        user_info = login_user(email, password)
                        st.session_state.user = user_info
                        st.success("¡Bienvenido de vuelta!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Por favor completa todos los campos")
    
    with tab2:
        st.subheader("Únete al Club Arte París")
        st.markdown("Para conseguir puntos, que podrás canjear por comida y bebidas gratis,Podrás hacer pedidos con tu celular, recibirás una recompensa de cumpleaños y mucho más.")
        st.info("🎁 **¡Regístrate y recibe 10 puntos de bienvenida!**")
        
        with st.form("registro_form"):
            nombre = st.text_input("👤 Nombre completo", placeholder="Tu nombre completo")
            email = st.text_input("📧 Email", placeholder="tu@email.com")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Crea una contraseña")
            fecha_cumpleanos = st.date_input(
                "🎂 Fecha de Cumpleaños (opcional) Añade tu cumpleaños para que podamos felicitarte y enviarte un vale de regalo tu cumpleaños.",
                value=None,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                help="¡Recibe regalos especiales en tu cumpleaños!"
            )
            
            if st.form_submit_button("Unirme a Arte París", use_container_width=True):
                if nombre and email and password:
                    try:
                        user_info = signup_user(email, password, nombre, fecha_cumpleanos)
                        st.session_state.user = user_info
                        st.balloons()
                        st.success("""
                        🎉 ¡Bienvenido al Club Arte París!
                        
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
    
    # Beneficios
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
# FOOTER
# ==================================================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">'
    '☕ <strong>Arte Paris Deli café</strong> - Donde cada taza cuenta una historia 🎨'
    '</div>',
    unsafe_allow_html=True
)
