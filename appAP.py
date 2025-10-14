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

def cargar_imagen_producto(ruta_imagen, ancho_maximo=120):
    """Versión más pequeña para productos en layout horizontal"""
    try:
        if os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            ancho_original, alto_original = imagen.size
            ancho_objetivo = min(ancho_original, ancho_maximo)
            
            if ancho_original > ancho_objetivo:
                ratio = ancho_objetivo / ancho_original
                nuevo_alto = int(alto_original * ratio)
                imagen = imagen.resize((ancho_objetivo, nuevo_alto), Image.Resampling.LANCZOS)
            
            st.image(imagen, use_container_width=True)
            return True
        else:
            st.image("https://via.placeholder.com/100x80/8B4513/FFFFFF?text=Img", 
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
def mostrar_producto_horizontal(producto, puntos_usuario, uid):
    """Mostrar producto en layout horizontal con imagen a la derecha"""
    disponible = puntos_usuario >= producto['puntos']
    
    # Crear contenedor horizontal
    with st.container():
        col_texto, col_imagen = st.columns([3, 2])
        
        with col_texto:
            st.markdown(f"""
            <div class="product-card-horizontal">
                <h4 style="color: #2C5530; margin-bottom: 8px; font-size: 1.1rem;">{producto['nombre']}</h4>
                <p style="color: #4A6741; margin: 4px 0; font-size: 0.95rem;">⭐ <strong>{producto['puntos']} puntos</strong></p>
                <p style="color: #666; margin: 4px 0; font-size: 0.85rem;">Valor: ${producto['precio_original']:.2f}</p>
                <p style="color: {'#2E8B57' if disponible else '#FF6B6B'}; margin: 8px 0; font-weight: bold; font-size: 0.9rem;">
                    {"✅ DISPONIBLE" if disponible else f"❌ Te faltan {producto['puntos'] - puntos_usuario} puntos"}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de canje
            if disponible:
                if st.button(f"🎁 Canjear {producto['puntos']} pts", 
                           key=f"canjear_{producto['nombre']}", 
                           use_container_width=True):
                    nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                    if nuevos_puntos >= 0:
                        st.success(f"¡Canjeado! {producto['nombre']}")
                        st.session_state.profile = None
                        time.sleep(2)
                        st.rerun()
        
        with col_imagen:
            # Imagen más pequeña a la derecha
            cargar_imagen_producto(producto['imagen'], 120)

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
# CSS PERSONALIZADO MEJORADO
# ==================================================
st.markdown("""
<style>
    .main > div {
        padding: 0.5rem;
        margin-bottom: 80px;
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
    .product-card-horizontal {
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border: 2px solid #E9ECEF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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
        color: white;
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
    
    /* MENÚ INFERIOR FIJO - CORREGIDO */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 2px solid #3DCCC5;
        padding: 10px 0;
        z-index: 9999;
        display: flex;
        justify-content: space-around;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    .nav-item {
        text-align: center;
        padding: 5px;
        flex: 1;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .nav-item.active {
        color: #3DCCC5;
        font-weight: bold;
        background: #f0f9f9;
        border-radius: 10px;
        margin: 0 5px;
    }
    .nav-icon {
        font-size: 20px;
        margin-bottom: 2px;
    }
    .nav-text {
        font-size: 12px;
        font-weight: normal;
    }
    
    /* Botones invisibles para el menú */
    .nav-button {
        position: absolute;
        width: 33.33%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
        z-index: 10000;
    }
    .nav-button-1 { left: 0; }
    .nav-button-2 { left: 33.33%; }
    .nav-button-3 { left: 66.66%; }
</style>
""", unsafe_allow_html=True)

def mostrar_menu_inferior(pagina_actual):
    """Menú inferior fijo que SÍ funciona"""
    # HTML del menú visual
    menu_html = f"""
    <div class="bottom-nav">
        <div class="nav-item {'active' if pagina_actual == 'Inicio' else ''}">
            <div class="nav-icon">🏠</div>
            <div class="nav-text">Inicio</div>
        </div>
        <div class="nav-item {'active' if pagina_actual == 'Productos' else ''}">
            <div class="nav-icon">🎁</div>
            <div class="nav-text">Productos</div>
        </div>
        <div class="nav-item {'active' if pagina_actual == 'Perfil' else ''}">
            <div class="nav-icon">👤</div>
            <div class="nav-text">Perfil</div>
        </div>
        
        <!-- Botones invisibles superpuestos -->
        <button class="nav-button nav-button-1" onclick="window.navigateTo('Inicio')"></button>
        <button class="nav-button nav-button-2" onclick="window.navigateTo('Productos')"></button>
        <button class="nav-button nav-button-3" onclick="window.navigateTo('Perfil')"></button>
    </div>
    
    <script>
        function navigateTo(pagina) {{
            // Esta función se ejecutará cuando se haga clic en los botones
            const event = new CustomEvent('navigate', {{ detail: {{ page: pagina }} }});
            window.dispatchEvent(event);
        }}
        
        // Escuchar el evento personalizado
        window.addEventListener('navigate', function(event) {{
            // Enviar el comando a Streamlit
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: event.detail.page
            }}, '*');
        }});
    </script>
    """
    
    st.markdown(menu_html, unsafe_allow_html=True)
    
    # Usar componentes de Streamlit para capturar los clics
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(" ", key="nav_inicio_btn"):
            st.session_state.pagina_actual = "Inicio"
            st.rerun()
    with col2:
        if st.button("  ", key="nav_productos_btn"):
            st.session_state.pagina_actual = "Productos"
            st.rerun()
    with col3:
        if st.button("   ", key="nav_perfil_btn"):
            st.session_state.pagina_actual = "Perfil"
            st.rerun()

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
        
        # CONTENIDO PRINCIPAL
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
                        <h4 style="color: #2C5530;">{producto['nombre']}</h4>
                        <p style="color: #4A6741;">⭐ {producto['puntos']} puntos</p>
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
                mostrar_producto_horizontal(producto, puntos_usuario, uid)
                st.markdown("---")
        
        elif st.session_state.pagina_actual == "Perfil":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #3DCCC5; margin: 0;">👤 Tu Perfil</h2>
                <p style="color: #666;">Gestiona tu cuenta Arte París</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="mobile-card">
                <h4 style="color: #2C5530;">👋 Hola, {perfil['nombre']}</h4>
                <p style="color: #4A6741;">📧 {perfil['email']}</p>
                <p style="color: #4A6741;">⭐ {puntos_usuario} puntos acumulados</p>
                <p style="color: #4A6741;">💰 ${perfil.get('total_compras', 0):.2f} gastados</p>
                <p style="color: #4A6741;">🎫 {perfil.get('tickets_registrados', 0)} tickets registrados</p>
                <p style="color: #4A6741;">{"🎂 " + perfil['fecha_cumpleanos'].strftime('%d/%m/%Y') if perfil.get('fecha_cumpleanos') else "🎂 Sin fecha de cumpleaños"}</p>
            </div>
            """, unsafe_allow_html=True)
            
            mostrar_registro_compra_seguro(uid)
            
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.user = None
                st.session_state.profile = None
                st.session_state.pagina_actual = "Inicio"
                st.rerun()
        
        # MENÚ INFERIOR - SIEMPRE AL FINAL
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
