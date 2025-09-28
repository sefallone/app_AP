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
    }
]

# ==================================================
# OFERTAS ESPECIALES - MODIFICAR SEGÚN TUS OFERTAS
# ==================================================
OFERTAS_ESPECIALES = [
    {
        "titulo": "🎁 Regalo de Cumpleaños",
        "descripcion": "Dulce sorpresa especial para tu día",
        "puntos": 0,
        "imagen": "https://images.unsplash.com/photo-1535254973040-607b474cb50d?w=300",
        "exclusivo": True,
        "cumpleanos": True
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
    page_title="Arte París",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================================================
# CSS PARA MÓVIL
# ==================================================
st.markdown("""
<style>
    /* Estilos móviles */
    .main > div {
        padding: 0.5rem;
    }
    
    .mobile-header {
        font-size: 2rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Brush Script MT', cursive;
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
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
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
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 25px;
        font-weight: bold;
        margin: 0.25rem 0;
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
                    "icon": {"color": "orange", "font-size": "12px"}, 
                    "nav-link": {"font-size": "12px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#764ba2"},
                }
            )
        
        # PÁGINA DE INICIO
        if selected == "Inicio":
            st.markdown('<div class="mobile-header">🎨 Arte París</div>', unsafe_allow_html=True)
            
            # Tarjeta de puntos
            st.markdown(f"""
            <div class="point-card-mobile">
                <h3>⭐ Tus Puntos</h3>
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
            
            # Acciones rápidas
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Registrar Compra"):
                    st.session_state.registrar_compra = True
                    st.rerun()
            with col2:
                if st.button("🎁 Canjear Puntos"):
                    st.session_state.canjear_puntos = True
                    st.rerun()
            
            # Productos destacados
            st.subheader("🛍️ Destacados")
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
            st.markdown('<div class="mobile-header">🎁 Productos</div>', unsafe_allow_html=True)
            
            # Ofertas de cumpleaños
            fecha_cumpleanos = perfil.get('fecha_cumpleanos')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.subheader("🎁 Regalo de Cumpleaños")
                for oferta in OFERTAS_ESPECIALES:
                    if oferta.get('cumpleanos'):
                        st.markdown(f"""
                        <div class="birthday-card">
                            <h3>{oferta['titulo']}</h3>
                            <p>{oferta['descripcion']}</p>
                            <h4>¡GRATIS en tu cumpleaños!</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("🎁 Reclamar Regalo", key="cumpleanos"):
                            st.success("¡Regalo reclamado! Presenta esta pantalla en tienda")
            
            # Todos los productos
            st.subheader("Todos los Productos")
            for producto in PRODUCTOS:
                with st.container():
                    disponible = puntos_usuario >= producto['puntos']
                    st.markdown(f"""
                    <div class="mobile-card" style="opacity: {'1' if disponible else '0.7'}">
                        <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                        <h4>{producto['nombre']}</h4>
                        <p>⭐ {producto['puntos']} puntos</p>
                        {"✅ DISPONIBLE" if disponible else f"❌ Te faltan {producto['puntos'] - puntos_usuario} puntos"}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if disponible and st.button(f"Canjear {producto['puntos']} pts", key=f"canjear_{producto['nombre']}"):
                        nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                        if nuevos_puntos >= 0:
                            st.success(f"¡Canjeado! {producto['nombre']}")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
        
        # PÁGINA DE PERFIL
        elif selected == "Perfil":
            st.markdown('<div class="mobile-header">👤 Perfil</div>', unsafe_allow_html=True)
            
            # Información del perfil
            st.markdown(f"""
            <div class="mobile-card">
                <h4>👋 Hola, {perfil['nombre']}</h4>
                <p>📧 {perfil['email']}</p>
                <p>⭐ {puntos_usuario} puntos</p>
                {"🎂 " + perfil['fecha_cumpleanos'].strftime('%d/%m/%Y') if perfil.get('fecha_cumpleanos') else "🎂 No especificada"}
            </div>
            """, unsafe_allow_html=True)
            
            # Estadísticas
            st.subheader("📊 Estadísticas")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Gastado", f"${perfil.get('total_compras', 0):.2f}")
            with col2:
                st.metric("Tickets", perfil.get('tickets_registrados', 0))
            
            # Registrar compra
            if st.button("📥 Registrar Nueva Compra", use_container_width=True):
                with st.form("compra_form"):
                    numero_ticket = st.text_input("Número de Ticket")
                    monto_compra = st.number_input("Monto ($)", min_value=0.0, step=0.5)
                    
                    if st.form_submit_button("Registrar"):
                        if numero_ticket and monto_compra > 0:
                            puntos_ganados = registrar_ticket_compra(uid, monto_compra, numero_ticket)
                            if puntos_ganados > 0:
                                st.success(f"¡+{puntos_ganados} puntos!")
                                time.sleep(2)
                                st.rerun()
            
            # Cerrar sesión
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.user = None
                st.rerun()

# ==================================================
# INTERFAZ DE LOGIN/CREAR CUENTA PARA MÓVIL
# ==================================================
else:
    st.markdown('<div class="mobile-header">🎨 Arte París</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Ingresar", "Crear Cuenta"])
    
    with tab1:
        st.subheader("🚀 Ingresar")
        with st.form("login_form"):
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Contraseña", type="password")
            
            if st.form_submit_button("Ingresar", use_container_width=True):
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
        st.subheader("📝 Crear Cuenta")
        st.info("🎁 ¡Recibe 10 puntos de bienvenida!")
        
        with st.form("registro_form"):
            nombre = st.text_input("👤 Nombre completo")
            email = st.text_input("📧 Email")
            password = st.text_input("🔒 Contraseña", type="password")
            fecha_cumpleanos = st.date_input(
                "🎂 Fecha de Cumpleaños (opcional)",
                value=None,
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )
            
            if st.form_submit_button("Crear Cuenta", use_container_width=True):
                if nombre and email and password:
                    try:
                        user_info = signup_user(email, password, nombre, fecha_cumpleanos)
                        st.session_state.user = user_info
                        st.balloons()
                        st.success("¡Cuenta creada! 10 puntos de regalo")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Completa los campos obligatorios")

# ==================================================
# FOOTER MÓVIL
# ==================================================
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem;">'
    '🎨 Arte París - Tu pastelería francesa favorita'
    '</div>',
    unsafe_allow_html=True
)
