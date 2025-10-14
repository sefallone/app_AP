import streamlit as st
import requests
import json
import time
from datetime import datetime, date
from PIL import Image
import os
import qrcode
import io

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
CONFIG_IMAGENES = {
    "logo": "LogoAP.jpg",
    "hero": "Cafe1.jpg",
    "productos": {
        "Milhojas": "Milhojas.jpg",
        "brazo": "Brazo.jpg",
        "croissant": "Croissant.jpg",
        "cafe_especial": "Cafe1.jpg",
        "profiterol": "Profiterol.jpg"
    },
    "ofertas": {
        "cumpleanos": "Brazo.jpg",
        "combo": "Tartaletafresa1.jpg"
    }
}

# ==================================================
# DATOS DE PRODUCTOS
# ==================================================
PRODUCTOS = [
    {
        "nombre": "Milhojas",
        "puntos": 100,
        "precio_original": 4.00,
        "imagen": CONFIG_IMAGENES["productos"]["Milhojas"],
        "categoria": "clasico"
    },
    {
        "nombre": "Brazo Gitano",
        "puntos": 80,
        "precio_original": 3.00,
        "imagen": CONFIG_IMAGENES["productos"]["brazo"],
        "categoria": "clasico"
    },
    {
        "nombre": "Croissant Dulce",
        "puntos": 50,
        "precio_original": 2.50,
        "imagen": CONFIG_IMAGENES["productos"]["croissant"],
        "categoria": "panaderia"
    },
    {
        "nombre": "Café Especial Arte París",
        "puntos": 100,
        "precio_original": 4.00,
        "imagen": CONFIG_IMAGENES["productos"]["cafe_especial"],
        "categoria": "bebida"
    },
    {
        "nombre": "Profiterol",
        "puntos": 80,
        "precio_original": 35.00,
        "imagen": CONFIG_IMAGENES["productos"]["profiterol"],
        "categoria": "especial"
    }
]

# ==================================================
# OFERTAS ESPECIALES
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
        "descripcion": "Café + Tartaleta Fresas",
        "puntos": 150,
        "imagen": CONFIG_IMAGENES["ofertas"]["combo"],
        "exclusivo": True
    }
]

# ==================================================
# FUNCIONES PARA IMÁGENES OPTIMIZADAS MÓVIL
# ==================================================
def cargar_imagen_movil(ruta_imagen, ancho_maximo=300):
    try:
        if os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            ancho_original, alto_original = imagen.size
            ancho_objetivo = min(ancho_original, ancho_maximo)
            
            if ancho_original > ancho_objetivo:
                ratio = ancho_objetivo / ancho_original
                nuevo_alto = int(alto_original * ratio)
                imagen = imagen.resize((ancho_objetivo, nuevo_alto), Image.Resampling.LANCZOS)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(imagen, use_container_width=True)
            return True
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("https://via.placeholder.com/250x150/8B4513/FFFFFF?text=Imagen+No+Encontrada", 
                        use_container_width=True)
            return False
    except Exception as e:
        st.error(f"❌ Error cargando imagen: {e}")
        return False

def mostrar_logo():
    st.markdown("""
    <div style="text-align: center; background: white; padding: 0.5rem; border-radius: 15px; margin: 0.5rem 0;">
    """, unsafe_allow_html=True)
    
    if os.path.exists(CONFIG_IMAGENES["logo"]):
        logo = Image.open(CONFIG_IMAGENES["logo"])
        ancho_original, alto_original = logo.size
        if ancho_original > 400:
            ratio = 400 / ancho_original
            nuevo_alto = int(alto_original * ratio)
            logo = logo.resize((400, nuevo_alto), Image.Resampling.LANCZOS)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo, use_container_width=True)
    else:
        st.markdown("""
        <h2 style="color: #8B4513; margin: 0; font-family: 'Brush Script MT', cursive;">Arte París</h2>
        <h3 style="color: #D2691E; margin: 0; font-size: 1.2rem;">ARTE PARÍS</h3>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# SISTEMA QR PARA COMPRAS SEGURAS
# ==================================================
def generar_codigo_qr_establecimiento():
    timestamp = int(time.time()) // 300
    codigo = f"ARTEPARIS_{timestamp}_{hash(str(timestamp)) % 10000:04d}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(codigo)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#3DCCC5", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return codigo, buffer

def validar_codigo_qr(codigo_escaneado):
    try:
        timestamp_actual = int(time.time()) // 300
        for i in range(2):
            timestamp_valido = timestamp_actual - i
            codigo_valido = f"ARTEPARIS_{timestamp_valido}_{hash(str(timestamp_valido)) % 10000:04d}"
            if codigo_escaneado == codigo_valido:
                return True
        return False
    except:
        return False

def mostrar_registro_compra_seguro(uid):
    st.subheader("📥 Registrar Compra Segura")
    
    st.info("""
    **🔒 Sistema Seguro de Registro**
    - Acércate a la caja y pide que te escaneen el código QR
    - El código cambia cada 5 minutos por seguridad
    - Solo las compras verificadas en tienda acumulan puntos
    """)
    
    codigo_actual, buffer_qr = generar_codigo_qr_establecimiento()
    
    st.markdown("### 📱 Código QR Actual")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(buffer_qr, use_container_width=True)
    st.caption(f"⏰ Válido por 5 minutos | Código: `{codigo_actual}`")
    
    st.markdown("---")
    st.subheader("🏪 Escanear desde Establecimiento")
    
    with st.expander("🔍 Escanear Código del Cliente"):
        codigo_escaneado = st.text_input("Ingresa el código QR escaneado:", placeholder="ARTEPARIS_12345_6789")
        monto_compra = st.number_input("Monto de la compra ($)", min_value=0.0, step=0.5, value=0.0)
        
        if st.button("✅ Validar y Registrar Compra", use_container_width=True):
            if validar_codigo_qr(codigo_escaneado) and monto_compra > 0:
                puntos_ganados = registrar_ticket_compra(uid, monto_compra, f"QR_{int(time.time())}")
                if puntos_ganados > 0:
                    st.success(f"✅ ¡Compra verificada! {puntos_ganados} puntos añadidos")
                    st.session_state.profile = None
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Error al registrar la compra")
            else:
                st.error("❌ Código QR inválido o expirado")

# ==================================================
# FUNCIONES FIREBASE
# ==================================================
def login_user(email, password):
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

def signup_user(email, password, nombre, fecha_cumpleanos=None, acepta_terminos=False, acepta_marketing=False):
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
            save_profile_via_rest(result['localId'], nombre, email, fecha_cumpleanos, 10, acepta_terminos, acepta_marketing)
            return result
        else:
            error_msg = result.get('error', {}).get('message', 'Error desconocido')
            raise Exception(f"Registro falló: {error_msg}")
    except Exception as e:
        raise Exception(f"Error en registro: {str(e)}")

def save_profile_via_rest(uid, nombre, email, fecha_cumpleanos=None, bonus_points=0, acepta_terminos=False, acepta_marketing=False):
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/clientes/{uid}"
        
        document_data = {
            "fields": {
                "nombre": {"stringValue": nombre},
                "email": {"stringValue": email},
                "puntos": {"integerValue": bonus_points},
                "timestamp": {"timestampValue": datetime.utcnow().isoformat() + "Z"},
                "total_compras": {"doubleValue": 0.0},
                "tickets_registrados": {"integerValue": 0},
                "acepta_terminos": {"booleanValue": acepta_terminos},
                "acepta_marketing": {"booleanValue": acepta_marketing}
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
                    'tickets_registrados': int(data['fields'].get('tickets_registrados', {}).get('integerValue', 0)),
                    'acepta_terminos': data['fields'].get('acepta_terminos', {}).get('booleanValue', False),
                    'acepta_marketing': data['fields'].get('acepta_marketing', {}).get('booleanValue', False)
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
    if not fecha_cumpleanos:
        return False
    hoy = date.today()
    return fecha_cumpleanos.month == hoy.month and fecha_cumpleanos.day == hoy.day

# ==================================================
# COMPONENTES INTERFAZ MÓVIL
# ==================================================
def mostrar_producto_movil(producto, puntos_usuario, uid):
    with st.container():
        disponible = puntos_usuario >= producto['puntos']
        
        st.markdown(f"""
        <div class="mobile-card" style="opacity: {'1' if disponible else '0.7'}; text-align: center;">
            <h4>{producto['nombre']}</h4>
            <p>⭐ {producto['puntos']} puntos</p>
            <p><small>Valor: ${producto['precio_original']:.2f}</small></p>
            {"<span style='color: green; font-weight: bold;'>✅ DISPONIBLE</span>" if disponible else f"<span style='color: red;'>❌ Te faltan {producto['puntos'] - puntos_usuario} puntos</span>"}
        </div>
        """, unsafe_allow_html=True)
        
        cargar_imagen_movil(producto['imagen'], 250)
        
        if disponible:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"🎁 Canjear {producto['puntos']} pts", 
                           key=f"canjear_{producto['nombre']}", 
                           use_container_width=True):
                    nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                    if nuevos_puntos >= 0:
                        st.success(f"¡Canjeado! {producto['nombre']}")
                        st.session_state.profile = None
                        time.sleep(2)
                        st.rerun()

def mostrar_menu_inferior(seleccion_actual):
    st.markdown("""
    <style>
        .fixed-bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 2px solid #3DCCC5;
            padding: 10px 0;
            z-index: 999;
            display: flex;
            justify-content: space-around;
        }
        .nav-item {
            text-align: center;
            padding: 5px;
            flex: 1;
            cursor: pointer;
        }
        .nav-item.active {
            color: #3DCCC5;
            font-weight: bold;
        }
        .nav-icon {
            font-size: 20px;
            margin-bottom: 5px;
        }
        .main-content {
            margin-bottom: 80px;
        }
        .stButton > button {
            border: none;
            background: transparent;
            color: inherit;
        }
    </style>
    """, unsafe_allow_html=True)
    
    menu_html = f"""
    <div class="fixed-bottom-nav">
        <div class="nav-item {'active' if seleccion_actual == 'Inicio' else ''}">
            <div class="nav-icon">🏠</div>
            <div>Inicio</div>
        </div>
        <div class="nav-item {'active' if seleccion_actual == 'Productos' else ''}">
            <div class="nav-icon">🎁</div>
            <div>Productos</div>
        </div>
        <div class="nav-item {'active' if seleccion_actual == 'Perfil' else ''}">
            <div class="nav-icon">👤</div>
            <div>Perfil</div>
        </div>
    </div>
    """
    st.markdown(menu_html, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠", key="nav_inicio", use_container_width=True):
            st.session_state.pagina_actual = "Inicio"
            st.rerun()
    with col2:
        if st.button("🎁", key="nav_productos", use_container_width=True):
            st.session_state.pagina_actual = "Productos"
            st.rerun()
    with col3:
        if st.button("👤", key="nav_perfil", use_container_width=True):
            st.session_state.pagina_actual = "Perfil"
            st.rerun()

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
    .terms-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #46E0E0;
        margin: 1rem 0;
        font-size: 0.85rem;
    }
    .checkbox-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem 0;
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
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "Inicio"

# ==================================================
# INTERFAZ PRINCIPAL
# ==================================================
if st.session_state.user:
    user_info = st.session_state.user
    uid = user_info["localId"]
    
    if st.session_state.profile is None:
        with st.spinner("Cargando tu perfil..."):
            st.session_state.profile = get_profile_via_rest(uid)
    
    perfil = st.session_state.profile
    
    if perfil:
        puntos_usuario = perfil.get('puntos', 0)
        
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        if st.session_state.pagina_actual == "Inicio":
            st.markdown("""
            <div class="hero-section">
                <h3 style="margin: 0; font-style: italic;">Lo convertimos en Arte</h3>
            </div>
            """, unsafe_allow_html=True)
            
            mostrar_logo()
            
            st.markdown(f"""
            <div class="point-card-mobile">
                <h3>⭐ Tus Puntos ArteParís</h3>
                <h1 style="font-size: 3rem; margin: 0;">{puntos_usuario}</h1>
                <p>Puntos acumulados</p>
            </div>
            """, unsafe_allow_html=True)
            
            fecha_cumpleanos = perfil.get('fecha_cumpleanos')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.markdown(f"""
                <div class="birthday-card">
                    <h3>🎉 ¡Feliz Cumpleaños!</h3>
                    <p>¡Hoy es tu día especial! Disfruta de regalos exclusivos</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.subheader("☕ Nuestra Esencia")
            cargar_imagen_movil(CONFIG_IMAGENES["hero"])
            
            st.subheader("🚀 Acciones Rápidas")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Registrar Compra", use_container_width=True):
                    st.session_state.pagina_actual = "Perfil"
                    st.rerun()
            with col2:
                if st.button("🎁 Canjear Puntos", use_container_width=True):
                    st.session_state.pagina_actual = "Productos"
                    st.rerun()
            
            st.subheader("🌟 Destacados")
            for producto in PRODUCTOS[:2]:
                with st.container():
                    st.markdown(f"""
                    <div class="mobile-card">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
                    </div>
                    """, unsafe_allow_html=True)
                    cargar_imagen_movil(producto['imagen'], 250)
        
        elif st.session_state.pagina_actual == "Productos":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #3DCCC5; margin: 0;">🎁 Productos Arte París</h2>
                <p style="color: #666;">Canjea tus puntos por experiencias únicas</p>
            </div>
            """, unsafe_allow_html=True)
            
            fecha_cumpleanos = perfil.get('fecha_cumpleanos')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.markdown(f"""
                <div class="birthday-card">
                    <h3>🎁 ¡Regalo de Cumpleaños!</h3>
                    <p>Café especial + Dulce sorpresa</p>
                    <h4>¡GRATIS hoy!</h4>
                </div>
                """, unsafe_allow_html=True)
                cargar_imagen_movil(OFERTAS_ESPECIALES[0]['imagen'], 250)
                if st.button("🎁 Reclamar Mi Regalo", use_container_width=True):
                    st.success("¡Regalo reclamado! Muestra esta pantalla en tienda")
            
            st.subheader("☕ Nuestra Carta")
            for producto in PRODUCTOS:
                mostrar_producto_movil(producto, puntos_usuario, uid)
        
        elif st.session_state.pagina_actual == "Perfil":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #3DCCC5; margin: 0;">👤 Tu Perfil</h2>
                <p style="color: #666;">Gestiona tu cuenta Arte París</p>
            </div>
            """, unsafe_allow_html=True)
            
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
            
            mostrar_registro_compra_seguro(uid)
            
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.user = None
                st.session_state.profile = None
                st.session_state.pagina_actual = "Inicio"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        mostrar_menu_inferior(st.session_state.pagina_actual)

else:
    st.markdown("""
    <div class="hero-section">
        <h3 style="margin: 0; font-style: italic;">Bienvenido a Arte Paris Deli Café</h3>
    </div>
    """, unsafe_allow_html=True)
    
    mostrar_logo()
    cargar_imagen_movil(CONFIG_IMAGENES["hero"], 350)
    
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
        st.markdown("Para conseguir puntos, que podrás canjear por comida y bebidas gratis, Podrás hacer pedidos con tu celular, recibirás una recompensa de cumpleaños y mucho más.")
        st.info("🎁 **¡Regístrate y recibe 10 puntos de bienvenida!**")
        
        with st.form("registro_form"):
            nombre = st.text_input("👤 Nombre completo", placeholder="Tu nombre completo")
            email = st.text_input("📧 Email", placeholder="tu@email.com")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Crea una contraseña")
            fecha_cumpleanos = st.date_input(
                "🎂 Fecha de Cumpleaños (opcional)",
                value=None,
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            
            st.markdown("---")
            st.markdown("### 📧 Comunicaciones y Términos")
            
            st.markdown('<div class="checkbox-container">', unsafe_allow_html=True)
            acepta_marketing = st.checkbox(
                "**Sí, quiero recibir información sobre ofertas exclusivas, anuncios y nuevos productos de Arte París**",
                value=False
            )
            st.markdown("""
            <div class="terms-section">
                <small><strong>Mantente al tanto.</strong> El e-mail es una gran forma de estar al día de las ofertas y novedades de Arte París.</small>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="checkbox-container">', unsafe_allow_html=True)
            acepta_terminos = st.checkbox(
                "**Acepto las Condiciones de Uso y la Declaración de Privacidad**",
                value=False
            )
            
            st.markdown("""
            <div style="text-align: center; margin-top: 0.5rem;">
                <small>
                    <a href="#" style="color: #46E0E0; text-decoration: none; margin: 0 0.5rem;">Condiciones de uso</a> • 
                    <a href="#" style="color: #46E0E0; text-decoration: none; margin: 0 0.5rem;">Política de Privacidad</a>
                </small>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.form_submit_button("Unirme a Arte París", use_container_width=True):
                if nombre and email and password:
                    if not acepta_terminos:
                        st.error("❌ Debes aceptar las Condiciones de Uso")
                    else:
                        try:
                            user_info = signup_user(email, password, nombre, fecha_cumpleanos, acepta_terminos, acepta_marketing)
                            st.session_state.user = user_info
                            st.balloons()
                            st.success("🎉 ¡Bienvenido al Club Arte París! Recibiste 10 puntos de bienvenida")
                            time.sleep(3)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Por favor completa los campos obligatorios")
    
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

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">'
    '☕ <strong>Arte Paris Deli café</strong> - Donde cada taza cuenta una historia 🎨'
    '</div>',
    unsafe_allow_html=True
)
