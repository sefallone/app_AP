# ==================================================
# IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ==================================================
import streamlit as st
import requests
import json
import time
from datetime import datetime

# ==================================================
# CONFIGURACIÓN FIREBASE - REEMPLAZAR CON TUS DATOS
# ==================================================
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",  # REEMPLAZAR con tu API Key
    "PROJECT_ID": "webap-6e49a"  # REEMPLAZAR con tu Project ID
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
        "nombre": "Tarta de Frambuesa",
        "puntos": 80,
        "precio_original": 35.00,
        "imagen": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=300",
        "categoria": "especial"
    },
    {
        "nombre": "Profiteroles con Chocolate",
        "puntos": 60,
        "precio_original": 28.00,
        "imagen": "https://images.unsplash.com/photo-1511512571111-0d6c50f5acab?w=300",
        "categoria": "clasico"
    },
    {
        "nombre": "Mousse de Maracuyá",
        "puntos": 45,
        "precio_original": 18.00,
        "imagen": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300",
        "categoria": "especial"
    }
]

# ==================================================
# OFERTAS ESPECIALES - MODIFICAR SEGÚN TUS OFERTAS
# ==================================================
OFERTAS_ESPECIALES = [
    {
        "titulo": "🎨 Obra Maestra del Mes",
        "descripcion": "Caja sorpresa con nuestras creaciones más exclusivas",
        "puntos": 100,
        "imagen": "https://images.unsplash.com/photo-1559622214-f8a9850965bb?w=300",
        "exclusivo": True
    },
    {
        "titulo": "🎬 Edición Cine Francés",
        "descripcion": "Dulces inspirados en películas francesas clásicas",
        "puntos": 75,
        "imagen": "https://images.unsplash.com/photo-1489599809505-f2d4cac355af?w=300",
        "exclusivo": True
    }
]

# ==================================================
# FUNCIÓN: REGISTRAR USUARIO - NO MODIFICAR
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

# ==================================================
# FUNCIÓN: LOGIN USUARIO - NO MODIFICAR
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
# FUNCIÓN: GUARDAR PERFIL - NO MODIFICAR
# ==================================================
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

# ==================================================
# FUNCIÓN: OBTENER PERFIL - NO MODIFICAR
# ==================================================
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

# ==================================================
# FUNCIÓN: ACTUALIZAR PUNTOS - NO MODIFICAR
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
# FUNCIÓN: REGISTRAR TICKET COMPRA - NO MODIFICAR
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
# CONFIGURACIÓN DE PÁGINA STREAMLIT - MODIFICAR TÍTULO/ICONO
# ==================================================
st.set_page_config(
    page_title="Arte París - Dulces Franceses",  # MODIFICAR con el nombre de tu negocio
    page_icon="🎨",  # MODIFICAR con tu icono preferido
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================================================
# CSS PERSONALIZADO - MODIFICAR COLORES/ESTILOS
# ==================================================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Brush Script MT', cursive;
    }
    .welcome-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .point-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px solid #f8f9fa;
        transition: transform 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    .art-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        border: 3px solid #ff6b6b;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
    }
    .offer-badge {
        background: #ff6b6b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        position: absolute;
        top: 10px;
        right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER PRINCIPAL - MODIFICAR TÍTULO/ESLOGAN
# ==================================================
st.markdown("""
<div class="welcome-section">
    <h1 style="font-size: 4rem; margin-bottom: 0;">🎨 Arte París</h1>  <!-- MODIFICAR nombre -->
    <h3 style="font-style: italic;">Donde cada dulce es una obra maestra</h3>  <!-- MODIFICAR eslogan -->
    <p style="font-size: 1.2rem; margin-top: 1rem;">✨ <strong>¡Sé nuestro artista preferido!</strong> ✨</p>  <!-- MODIFICAR frase -->
</div>
""", unsafe_allow_html=True)

# ==================================================
# GALERÍA DE INSPIRACIÓN - MODIFICAR IMÁGENES/TEXTOS
# ==================================================
st.subheader("🎭 Inspirado en la Belleza del Arte")  

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.image("https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=200", caption="🎨 Monet - Inspiración Impresionista")  <!-- MODIFICAR imagen/texto -->
with col2:
    st.image("https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=200", caption="📚 Cultura Francesa")  <!-- MODIFICAR imagen/texto -->
with col3:
    st.image("https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=200", caption="🎬 Cine de Arte")  <!-- MODIFICAR imagen/texto -->
with col4:
    st.image("https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=200", caption="🏛️ Arte Clásico")  <!-- MODIFICAR imagen/texto -->

st.markdown("---")

# ==================================================
# VERIFICACIÓN CONFIGURACIÓN FIREBASE - NO MODIFICAR
# ==================================================
if not FIREBASE_CONFIG["API_KEY"] or FIREBASE_CONFIG["API_KEY"] == "tu_api_key_aqui":
    st.error("❌ Configura la API_KEY de Firebase en el código")
    st.stop()

# ==================================================
# MANEJO DE SESIÓN USUARIO - NO MODIFICAR
# ==================================================
if "user" not in st.session_state:
    st.session_state.user = None

# ==================================================
# INTERFAZ USUARIO LOGUEADO - MODIFICAR TEXTO/ESTILOS
# ==================================================
if st.session_state.user:
    user_info = st.session_state.user
    uid = user_info["localId"]
    
    # Obtener perfil
    perfil = get_profile_via_rest(uid)
    
    if perfil:
        # VALIDACIÓN SEGURA DE PUNTOS - NO MODIFICAR
        try:
            puntos_usuario = int(perfil.get('puntos', 0))
        except (TypeError, ValueError):
            puntos_usuario = 0
            st.warning("⚠️ Se detectó un problema con tus puntos, se han establecido en 0")
        
        # BIENVENIDA PERSONALIZADA - MODIFICAR TEXTO
        st.success(f"✨ ¡Bienvenido de nuevo, {perfil['nombre']}! Eres nuestro artista preferido 🎨")
        
        # TARJETA DE PUNTOS PRINCIPAL - MODIFICAR ESTILOS
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            st.markdown(f"""
            <div class="point-card">
                <h3>⭐ Tus Puntos de Arte</h3>  <!-- MODIFICAR título -->
                <h1 style="font-size: 4rem; margin: 0;">{puntos_usuario}</h1>
                <p>Puntos acumulados</p>  <!-- MODIFICAR texto -->
            </div>
            """, unsafe_allow_html=True)
        
        # SECCIÓN: PRODUCTOS DISPONIBLES - MODIFICAR TÍTULO/TEXTO
        st.subheader("🛍️ Galería de Delicias - Canjea tus Puntos")  <!-- MODIFICAR título -->
        
        # FILTRADO DE PRODUCTOS - NO MODIFICAR LÓGICA
        productos_disponibles = []
        productos_no_disponibles = []
        
        for producto in PRODUCTOS:
            try:
                puntos_producto = int(producto['puntos'])
                if puntos_producto <= puntos_usuario:
                    productos_disponibles.append(producto)
                else:
                    productos_no_disponibles.append(producto)
            except (KeyError, TypeError, ValueError):
                continue
        
        # MOSTRAR PRODUCTOS DISPONIBLES - MODIFICAR TEXTO/ESTILOS
        if productos_disponibles:
            st.success(f"🎉 ¡Puedes canjear {len(productos_disponibles)} productos!")  <!-- MODIFICAR texto -->
            
            cols = st.columns(3)
            for idx, producto in enumerate(productos_disponibles):
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div class="product-card">
                            <div style="position: relative;">
                                <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                                <div class="offer-badge">⭐ {producto['puntos']} pts</div>
                            </div>
                            <h4>{producto['nombre']}</h4>
                            <p>💎 <s>${producto['precio_original']}</s> <strong>GRATIS con puntos</strong></p>  <!-- MODIFICAR texto -->
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🎁 Canjear {producto['puntos']} puntos", key=f"canjear_{idx}"):
                            if puntos_usuario >= producto['puntos']:
                                nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                                if nuevos_puntos >= 0:
                                    st.success(f"🎨 ¡Felicidades! Has canjeado '{producto['nombre']}' por {producto['puntos']} puntos")  <!-- MODIFICAR texto -->
                                    st.balloons()
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ Error al procesar el canje")
        else:
            st.info("💫 Aún no tienes suficientes puntos para canjear productos. ¡Sigue acumulando!")  <!-- MODIFICAR texto -->
            
            # PRODUCTOS POR ALCANZAR - MODIFICAR TÍTULO/TEXTO
            st.subheader("🎯 Productos por Alcanzar")  <!-- MODIFICAR título -->
            cols = st.columns(3)
            for idx, producto in enumerate(productos_no_disponibles[:3]):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="product-card" style="opacity: 0.7;">
                        <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ Necesitas {producto['puntos']} puntos</p>  <!-- MODIFICAR texto -->
                        <p><small>Te faltan: {producto['puntos'] - puntos_usuario} puntos</small></p>  <!-- MODIFICAR texto -->
                    </div>
                    """, unsafe_allow_html=True)
        
        # SECCIÓN: OFERTAS EXCLUSIVAS - MODIFICAR TÍTULO/TEXTO
        st.subheader("🎪 Ofertas Exclusivas ArteParísClub")  <!-- MODIFICAR título -->
        
        for oferta in OFERTAS_ESPECIALES:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(oferta['imagen'], use_column_width=True)
            with col2:
                disponible = puntos_usuario >= oferta['puntos']
                st.markdown(f"""
                <div class="art-card">
                    <h3>{oferta['titulo']}</h3>
                    <p>{oferta['descripcion']}</p>
                    <h4>💎 {oferta['puntos']} Puntos</h4>
                    {"✅ DISPONIBLE" if disponible else "❌ Necesitas más puntos"}  <!-- MODIFICAR texto -->
                </div>
                """, unsafe_allow_html=True)
                
                if disponible:
                    if st.button(f"🎪 Canjear Oferta Especial - {oferta['puntos']} puntos", key=f"oferta_{oferta['titulo']}"):
                        nuevos_puntos = update_points_via_rest(uid, -oferta['puntos'])
                        if nuevos_puntos >= 0:
                            st.success(f"✨ ¡Obra maestra adquirida! {oferta['titulo']}")  <!-- MODIFICAR texto -->
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Error al procesar el canje")
        
        # SECCIÓN: ESTADÍSTICAS - MODIFICAR TÍTULO/TEXTO
        st.subheader("📊 Tu Trayectoria Artística")  <!-- MODIFICAR título -->
        
        # VALIDACIÓN CAMPOS NUMÉRICOS - NO MODIFICAR
        try:
            total_compras = float(perfil.get('total_compras', 0))
        except (TypeError, ValueError):
            total_compras = 0.0
            
        try:
            tickets_registrados = int(perfil.get('tickets_registrados', 0))
        except (TypeError, ValueError):
            tickets_registrados = 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Gastado", f"${total_compras:.2f}")  <!-- MODIFICAR texto -->
        with col2:
            st.metric("🎫 Tickets Registrados", tickets_registrados)  <!-- MODIFICAR texto -->
        with col3:
            # SISTEMA DE NIVELES - MODIFICAR CRITERIOS/TEXTOS
            if puntos_usuario < 50:
                nivel = "🎨 Aprendiz"
            elif puntos_usuario < 100:
                nivel = "⭐ Artista"
            elif puntos_usuario < 200:
                nivel = "👑 Maestro"
            else:
                nivel = "💎 Leyenda"
            st.metric("👑 Nivel Actual", nivel)  <!-- MODIFICAR texto -->
        
        # SECCIÓN: GESTIÓN DE PUNTOS - MODIFICAR TÍTULO/TEXTO
        st.subheader("🎯 Sigue Sumando Puntos")  <!-- MODIFICAR título -->
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎁 Registrar Nueva Compra", use_container_width=True):  <!-- MODIFICAR texto -->
                with st.form("nueva_compra_form"):
                    st.write("**📝 Registrar Nueva Compra**")  <!-- MODIFICAR texto -->
                    numero_ticket = st.text_input("Número de Ticket", placeholder="TKT-001")  <!-- MODIFICAR texto -->
                    monto_compra = st.number_input("Monto de la Compra ($)", min_value=0.0, step=0.5, value=0.0)  <!-- MODIFICAR texto -->
                    
                    if st.form_submit_button("📥 Registrar Compra"):  <!-- MODIFICAR texto -->
                        if numero_ticket.strip() and monto_compra > 0:
                            puntos_ganados = registrar_ticket_compra(uid, monto_compra, numero_ticket)
                            if puntos_ganados > 0:
                                st.success(f"✅ ¡Compra registrada! Ganaste {puntos_ganados} puntos")  <!-- MODIFICAR texto -->
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ Error al registrar la compra")
                        else:
                            st.warning("⚠️ Ingresa un número de ticket y monto válidos")  <!-- MODIFICAR texto -->
        
        with col2:
            if st.button("✨ +5 Puntos de Cortesía", use_container_width=True):  <!-- MODIFICAR texto -->
                nuevos_puntos = update_points_via_rest(uid, 5)
                if nuevos_puntos > puntos_usuario:
                    st.success(f"🎉 ¡+5 puntos de cortesía! Ahora tienes {nuevos_puntos} puntos")  <!-- MODIFICAR texto -->
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Error al agregar puntos")
    
    else:
        st.error("❌ No se pudo cargar tu perfil. Por favor, recarga la página.")  <!-- MODIFICAR texto -->
        
        if st.button("🔄 Recargar Perfil"):  <!-- MODIFICAR texto -->
            st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):  <!-- MODIFICAR texto -->
        st.session_state.user = None
        st.rerun()

# ==================================================
# INTERFAZ USUARIO NO LOGUEADO - MODIFICAR TEXTO/ESTILOS
# ==================================================
else:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="login-container">
            <h2 style="text-align: center; color: #764ba2;">🎨 Únete a Nuestra Galería</h2>  <!-- MODIFICAR texto -->
            <p style="text-align: center;">✨ <strong>¡Sé nuestro artista preferido!</strong></p>  <!-- MODIFICAR texto -->
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🚀 Ingresar", "📝 Crear Cuenta"])  <!-- MODIFICAR textos -->
        
        with tab1:
            st.info("¿Ya eres parte de nuestra comunidad artística?")  <!-- MODIFICAR texto -->
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="tu@email.com")  <!-- MODIFICAR texto -->
                password = st.text_input("🔒 Contraseña", type="password")  <!-- MODIFICAR texto -->
                
                if st.form_submit_button("🎯 Ingresar a Mi Galería"):  <!-- MODIFICAR texto -->
                    if email and password:
                        try:
                            user_info = login_user(email, password)
                            st.session_state.user = user_info
                            st.success("✅ ¡Bienvenido a tu espacio creativo!")  <!-- MODIFICAR texto -->
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")
                    else:
                        st.warning("⚠️ Completa todos los campos")  <!-- MODIFICAR texto -->
        
        with tab2:
            st.success("🎁 **¡Regístrate y recibe 10 puntos de bienvenida!**")  <!-- MODIFICAR texto -->
            with st.form("registro_form"):
                nombre = st.text_input("👤 Nombre completo", placeholder="Claude Monet")  <!-- MODIFICAR texto -->
                email = st.text_input("📧 Email", placeholder="claude@arteparis.com")  <!-- MODIFICAR texto -->
                password = st.text_input("🔒 Contraseña", type="password")  <!-- MODIFICAR texto -->
                
                if st.form_submit_button("🎨 Unirme al Arte París Club"):  <!-- MODIFICAR texto -->
                    if nombre and email and password:
                        try:
                            user_info = signup_user(email, password, nombre)
                            st.session_state.user = user_info
                            st.balloons()
                            st.success("""
                            🎉 ¡Bienvenido a nuestra familia artística!
                            
                            **🎁 Recibiste 10 puntos de bienvenida**
                            
                            Ahora puedes:
                            - Canjear puntos por obras maestras dulces
                            - Acceder a ofertas exclusivas
                            - Participar en eventos especiales
                            """)  <!-- MODIFICAR texto -->
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")
                    else:
                        st.warning("⚠️ Completa todos los campos")  <!-- MODIFICAR texto -->
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 2rem;">
            <h3>🎪 Beneficios Exclusivos</h3>  <!-- MODIFICAR título -->
            <div class="product-card">
                <h4>⭐ Puntos por cada compra</h4>  <!-- MODIFICAR texto -->
                <p>5 puntos por cada $5 gastados</p>  <!-- MODIFICAR texto -->
            </div>
            <div class="product-card">
                <h4>🎨 Ofertas de Arte</h4>  <!-- MODIFICAR texto -->
                <p>Productos exclusivos inspirados en obras maestras</p>  <!-- MODIFICAR texto -->
            </div>
            <div class="product-card">
                <h4>👑 Trato Preferencial</h4>  <!-- MODIFICAR texto -->
                <p>Descuentos y promociones especiales</p>  <!-- MODIFICAR texto -->
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================================================
# FOOTER - MODIFICAR TEXTO/INFORMACIÓN
# ==================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <h3>🎨 Arte París</h3>  <!-- MODIFICAR nombre -->
    <p><em>"Donde la pastelería se encuentra con el arte"</em></p>  <!-- MODIFICAR eslogan -->
    <p>✨ <strong>¡Sé nuestro artista preferido!</strong> ✨</p>  <!-- MODIFICAR frase -->
    <p>📍 Cada bocado es una experiencia francesa inolvidable</p>  <!-- MODIFICAR texto -->
</div>
""", unsafe_allow_html=True)
