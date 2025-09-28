import streamlit as st
import requests
import json
import time
from datetime import datetime

# ==================================================
# CONFIGURACIÓN FIREBASE (mantener igual)
# ==================================================

FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# DATOS DE PRODUCTOS Y OFERTAS
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
# FUNCIONES (mantener igual que antes)
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
# INTERFAZ MEJORADA - DISEÑO ARTÍSTICO Y ELEGANTE
# ==================================================

st.set_page_config(
    page_title="Arte París - Dulces Franceses", 
    page_icon="🎨", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado mejorado con tema artístico
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
        background: blue;
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

# Header principal con logo artístico
st.markdown("""
<div class="welcome-section">
    <h1 style="font-size: 4rem; margin-bottom: 0;">🎨 Arte París</h1>
    <h3 style="font-style: italic;">Donde cada dulce es una obra maestra</h3>
    <p style="font-size: 1.2rem; margin-top: 1rem;">✨ <strong>¡Sé nuestro artista preferido!</strong> ✨</p>
</div>
""", unsafe_allow_html=True)

# Galería de inspiración artística
st.subheader("🎭 Inspirado en la Belleza del Arte")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.image("https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=200", caption="🎨 Monet - Inspiración Impresionista")
with col2:
    st.image("https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=200", caption="📚 Cultura Francesa")
with col3:
    st.image("https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=200", caption="🎬 Cine de Arte")
with col4:
    st.image("https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=200", caption="🏛️ Arte Clásico")

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
    
    # Obtener perfil
    perfil = get_profile_via_rest(uid)
    
    if perfil:
        # Bienvenida personalizada
        st.success(f"✨ ¡Bienvenido de nuevo, {perfil['nombre']}! Eres nuestro artista preferido 🎨")
        
        # Tarjeta de puntos principal
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            st.markdown(f"""
            <div class="point-card">
                <h3>⭐ Tus Puntos de Arte</h3>
                <h1 style="font-size: 4rem; margin: 0;">{perfil['puntos']}</h1>
                <p>Puntos acumulados</p>
            </div>
            """, unsafe_allow_html=True)
        
        # SECCIÓN: PRODUCTOS DISPONIBLES
        st.subheader("🛍️ Galería de Delicias - Canjea tus Puntos")
        
        # Filtrar productos que el usuario puede canjear
        productos_disponibles = [p for p in PRODUCTOS if p['puntos'] <= perfil['puntos']]
        productos_no_disponibles = [p for p in PRODUCTOS if p['puntos'] > perfil['puntos']]
        
        if productos_disponibles:
            st.success(f"🎉 ¡Puedes canjear {len(productos_disponibles)} productos!")
            
            # Mostrar productos disponibles en columnas
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
                            <p>💎 <s>${producto['precio_original']}</s> <strong>GRATIS con puntos</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🎁 Canjear {producto['puntos']} puntos", key=f"canjear_{idx}"):
                            if perfil['puntos'] >= producto['puntos']:
                                nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                                st.success(f"🎨 ¡Felicidades! Has canjeado '{producto['nombre']}' por {producto['puntos']} puntos")
                                st.balloons()
                                st.rerun()
        
        # SECCIÓN: OFERTAS EXCLUSIVAS ARTE PARÍS CLUB
        st.subheader("🎪 Ofertas Exclusivas ArteParísClub")
        
        for oferta in OFERTAS_ESPECIALES:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(oferta['imagen'], use_column_width=True)
            with col2:
                st.markdown(f"""
                <div class="art-card">
                    <h3>{oferta['titulo']}</h3>
                    <p>{oferta['descripcion']}</p>
                    <h4>💎 {oferta['puntos']} Puntos</h4>
                    {"✅ DISPONIBLE" if perfil['puntos'] >= oferta['puntos'] else "❌ Necesitas más puntos"}
                </div>
                """, unsafe_allow_html=True)
                
                if perfil['puntos'] >= oferta['puntos']:
                    if st.button(f"🎪 Canjear Oferta Especial - {oferta['puntos']} puntos", key=f"oferta_{oferta['titulo']}"):
                        nuevos_puntos = update_points_via_rest(uid, -oferta['puntos'])
                        st.success(f"✨ ¡Obra maestra adquirida! {oferta['titulo']}")
                        st.rerun()
        
        # SECCIÓN: PROGRESIÓN Y ESTADÍSTICAS
        st.subheader("📊 Tu Trayectoria Artística")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Gastado", f"${perfil['total_compras']:.2f}")
        with col2:
            st.metric("🎫 Tickets Registrados", perfil['tickets_registrados'])
        with col3:
            st.metric("👑 Nivel Actual", "Artista Novato" if perfil['puntos'] < 100 else "Artista Consagrado")
        
        # Sección de gestión de puntos (mantener funcionalidades existentes)
        st.subheader("🎯 Sigue Sumando Puntos")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎁 Registrar Nueva Compra", use_container_width=True):
                with st.form("nueva_compra"):
                    ticket = st.text_input("Número de Ticket")
                    monto = st.number_input("Monto ($)", min_value=0.0, step=0.5)
                    if st.form_submit_button("📥 Registrar"):
                        if ticket and monto > 0:
                            puntos_ganados = registrar_ticket_compra(uid, monto, ticket)
                            st.success(f"¡+{puntos_ganados} puntos! Total: {perfil['puntos'] + puntos_ganados}")
                            st.rerun()
        
        with col2:
            if st.button("✨ +5 Puntos de Cortesía", use_container_width=True):
                nuevos_puntos = update_points_via_rest(uid, 5)
                st.success(f"¡+5 puntos de cortesía! Ahora tienes {nuevos_puntos} puntos")
                st.rerun()
    
    else:
        st.warning("⚠️ Perfil no encontrado")
        
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()

else:
    # === USUARIO NO LOGUEADO - DISEÑO MEJORADO ===
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="login-container">
            <h2 style="text-align: center; color: #764ba2;">🎨 Únete a Nuestra Galería</h2>
            <p style="text-align: center;">✨ <strong>¡Sé nuestro artista preferido!</strong></p>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🚀 Ingresar", "📝 Crear Cuenta"])
        
        with tab1:
            st.info("¿Ya eres parte de nuestra comunidad artística?")
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="tu@email.com")
                password = st.text_input("🔒 Contraseña", type="password")
                
                if st.form_submit_button("🎯 Ingresar a Mi Galería"):
                    if email and password:
                        try:
                            user_info = login_user(email, password)
                            st.session_state.user = user_info
                            st.success("✅ ¡Bienvenido a tu espacio creativo!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")
                    else:
                        st.warning("⚠️ Completa todos los campos")
        
        with tab2:
            st.success("🎁 **¡Regístrate y recibe 10 puntos de bienvenida!**")
            with st.form("registro_form"):
                nombre = st.text_input("👤 Nombre completo", placeholder="Claude Monet")
                email = st.text_input("📧 Email", placeholder="claude@arteparis.com")
                password = st.text_input("🔒 Contraseña", type="password")
                
                if st.form_submit_button("🎨 Unirme al Arte París Club"):
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
                            """)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")
                    else:
                        st.warning("⚠️ Completa todos los campos")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 2rem;">
            <h3>🎪 Beneficios Exclusivos</h3>
            <div class="product-card">
                <h4>⭐ Puntos por cada compra</h4>
                <p>5 puntos por cada $5 gastados</p>
            </div>
            <div class="product-card">
                <h4>🎨 Ofertas de Arte</h4>
                <p>Productos exclusivos inspirados en obras maestras</p>
            </div>
            <div class="product-card">
                <h4>👑 Trato Preferencial</h4>
                <p>Descuentos y promociones especiales</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer artístico
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <h3>🎨 Arte París</h3>
    <p><em>"Donde la pastelería se encuentra con el arte"</em></p>
    <p>✨ <strong>¡Sé nuestro artista preferido!</strong> ✨</p>
    <p>📍 Cada bocado es una experiencia francesa inolvidable</p>
</div>
""", unsafe_allow_html=True)
