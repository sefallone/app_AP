import streamlit as st
import requests
import json
import time
from datetime import datetime, date, timedelta
from PIL import Image
import os
import qrcode
import io
import uuid
from math import radians, sin, cos, sqrt, atan2
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import re

# ==================================================
# CONFIGURACIÓN FIREBASE
# ==================================================
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# CONFIGURACIÓN DE EMAIL Y SMS
# ==================================================
CONFIG_EMAIL = {
    "smtp_server": "smtp.gmail.com",  # Cambiar según tu proveedor
    "smtp_port": 587,
    "sender_email": "tucorreo@arteparis.com",  # Configurar con tu email
    "sender_password": "tu_password"  # Configurar con tu password
}

CONFIG_SMS = {
    "api_key": "tu_api_key_sms",  # Configurar con API de servicio SMS
    "sender_id": "ARTEPARIS"
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
# DATOS DE PRODUCTOS MEJORADOS
# ==================================================
PRODUCTOS = [
    {
        "nombre": "Milhojas Clásico",
        "puntos": 100,
        "precio_original": 4.00,
        "imagen": CONFIG_IMAGENES["productos"]["Milhojas"],
        "categoria": "pasteleria",
        "descripcion": "Capas crujientes de hojaldre intercaladas con crema pastelera suave. Un clásico francés que nunca pasa de moda.",
        "destacado": True
    },
    {
        "nombre": "Brazo Gitano",
        "puntos": 80,
        "precio_original": 3.00,
        "imagen": CONFIG_IMAGENES["productos"]["brazo"],
        "categoria": "pasteleria", 
        "descripcion": "Bizcocho esponjoso relleno de dulce de leche o crema, enrollado a la perfección. Tradición en cada rebanada.",
        "destacado": False
    },
    {
        "nombre": "Croissant de Mantequilla",
        "puntos": 50,
        "precio_original": 2.50,
        "imagen": CONFIG_IMAGENES["productos"]["croissant"],
        "categoria": "panaderia",
        "descripcion": "Capas doradas y crujientes con el auténtico sabor de la mantequilla. Perfecto para empezar el día.",
        "destacado": True
    },
    {
        "nombre": "Café Especial Arte París",
        "puntos": 100,
        "precio_original": 4.00,
        "imagen": CONFIG_IMAGENES["productos"]["cafe_especial"],
        "categoria": "bebida",
        "descripcion": "Mezcla exclusiva de granos arábica tostados a la perfección. Aromas intensos con un final suave y persistente.",
        "destacado": True
    },
    {
        "nombre": "Profiteroles",
        "puntos": 80,
        "precio_original": 35.00,
        "imagen": CONFIG_IMAGENES["productos"]["profiterol"],
        "categoria": "especial",
        "descripcion": "Bolitas de profiterol rellenas de crema y bañadas en salsa de chocolate belga. Indulgencia pura.",
        "destacado": False
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
# NUEVAS CONFIGURACIONES - SISTEMAS ADICIONALES
# ==================================================

# Configuración de tiendas
TIENDAS = [
    {
        "id": 1,
        "nombre": "Arte París Centro",
        "direccion": "Av. Principal 123, Centro",
        "telefono": "+1234567890",
        "horario": "Lun-Dom: 7:00 AM - 10:00 PM",
        "latitud": 4.710989,
        "longitud": -74.072092,
        "servicios": ["WiFi", "Estacionamiento", "Terraza", "Reservas"]
    },
    {
        "id": 2,
        "nombre": "Arte París Norte",
        "direccion": "Calle Norte 456, Zona Norte",
        "telefono": "+1234567891",
        "horario": "Lun-Dom: 6:30 AM - 9:30 PM",
        "latitud": 4.750989,
        "longitud": -74.052092,
        "servicios": ["WiFi", "Para llevar", "Eventos"]
    },
    {
        "id": 3,
        "nombre": "Arte París Sur",
        "direccion": "Carrera Sur 789, Zona Sur",
        "telefono": "+1234567892",
        "horario": "Lun-Dom: 7:30 AM - 10:30 PM",
        "latitud": 4.680989,
        "longitud": -74.092092,
        "servicios": ["WiFi", "Estacionamiento", "Delivery"]
    }
]

# Estados de pedidos
ESTADOS_PEDIDO = {
    "pendiente": "⏳ Pendiente",
    "confirmado": "✅ Confirmado",
    "preparando": "👨‍🍳 Preparando",
    "listo": "🎉 Listo para recoger",
    "entregado": "📦 Entregado",
    "cancelado": "❌ Cancelado"
}

# ==================================================
# SISTEMA DE VALIDACIÓN DE TELÉFONO Y EMAIL
# ==================================================

def validar_telefono(telefono):
    """Valida que el número de teléfono tenga formato correcto"""
    # Patrón para números internacionales: + seguido de 10-15 dígitos
    patron = r'^\+[1-9]\d{9,14}$'
    return re.match(patron, telefono) is not None

def validar_email(email):
    """Valida formato básico de email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def enviar_email_verificacion(email, nombre, codigo_verificacion):
    """Envía email de verificación al usuario"""
    try:
        # Configurar el mensaje
        mensaje = MimeMultipart()
        mensaje['From'] = CONFIG_EMAIL['sender_email']
        mensaje['To'] = email
        mensaje['Subject'] = "Verifica tu cuenta - Arte París"
        
        # Cuerpo del email
        cuerpo = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h2 style="color: #8B4513;">Arte París</h2>
                        <h3 style="color: #333;">Verificación de Cuenta</h3>
                    </div>
                    
                    <p>Hola <strong>{nombre}</strong>,</p>
                    
                    <p>¡Gracias por registrarte en Arte París! Para activar tu cuenta y comenzar a disfrutar de todos nuestros beneficios, por favor verifica tu dirección de email.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border: 2px dashed #8B4513;">
                            <h4 style="margin: 0; color: #8B4513;">Código de Verificación</h4>
                            <h2 style="margin: 10px 0; color: #333; letter-spacing: 3px;">{codigo_verificacion}</h2>
                        </div>
                    </div>
                    
                    <p>Ingresa este código en la aplicación para completar tu registro.</p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #666; font-size: 12px;">
                            Si no solicitaste este registro, por favor ignora este mensaje.<br>
                            © 2024 Arte París. Todos los derechos reservados.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        mensaje.attach(MimeText(cuerpo, 'html'))
        
        # Conectar y enviar
        server = smtplib.SMTP(CONFIG_EMAIL['smtp_server'], CONFIG_EMAIL['smtp_port'])
        server.starttls()
        server.login(CONFIG_EMAIL['sender_email'], CONFIG_EMAIL['sender_password'])
        server.send_message(mensaje)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Error enviando email: {e}")
        return False

def enviar_sms_promocional(telefono, mensaje):
    """Envía SMS promocional al usuario"""
    try:
        # Simulación de envío de SMS - En producción usarías una API real como Twilio
        st.info(f"📱 SMS enviado a {telefono}: {mensaje}")
        
        # Código ejemplo para Twilio (descomentar y configurar):
        """
        from twilio.rest import Client
        
        account_sid = 'tu_account_sid'
        auth_token = 'tu_auth_token'
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=mensaje,
            from_=CONFIG_SMS['sender_id'],
            to=telefono
        )
        """
        
        return True
    except Exception as e:
        st.error(f"Error enviando SMS: {e}")
        return False

def generar_codigo_verificacion():
    """Genera un código de verificación de 6 dígitos"""
    return str(uuid.uuid4().int)[:6]

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

def cargar_imagen_producto(ruta_imagen, ancho_maximo=200):
    """Versión mejorada para diseño estético"""
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
            st.image("https://via.placeholder.com/200x150/8B4513/FFFFFF?text=Imagen+No+Encontrada", 
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
# DISEÑO ESTÉTICO MEJORADO PARA PRODUCTOS
# ==================================================
def mostrar_hero_inicio():
    """Sección hero mejorada para inicio"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: #8B4513; font-size: 2rem; margin-bottom: 1rem; font-family: 'Georgia', serif;">
            Bienvenido a Arte París
        </h1>
        <p style="color: #666; font-size: 1.1rem; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            Donde cada taza de café y cada bocado cuentan una historia de tradición, 
            pasión y el arte de lo bien hecho. Descubre experiencias únicas creadas especialmente para ti.
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_hero_productos():
    """Sección hero mejorada para productos"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem; border-radius: 20px; margin-bottom: 2rem;">
        <h1 style="color: #8B4513; font-size: 2rem; margin-bottom: 1rem; font-family: 'Georgia', serif;">
            Lo Mejor de Arte París
        </h1>
        <p style="color: #666; font-size: 1.1rem; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            Descubre nuestros productos artesanales, donde cada detalle cuenta una historia de sabor y tradición. 
            Desde el primer sorbo hasta el último bocado, experiencias creadas para momentos especiales.
        </p>
    </div>
    """, unsafe_allow_html=True)

def mostrar_producto_elegante(producto, puntos_usuario, uid):
    """Diseño elegante tipo magazine para productos"""
    disponible = puntos_usuario >= producto['puntos']
    
    # Crear un contenedor con borde y sombra usando HTML/CSS
    st.markdown("""
    <div style="border-radius: 15px; padding: 1rem; margin: 1rem 0; background: white; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #E9ECEF;">
    """, unsafe_allow_html=True)
    
    # Layout de dos columnas
    col_imagen, col_texto = st.columns([2, 3])
    
    with col_imagen:
        # Imagen con estilo elegante
        st.markdown("""
        <div style="border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        cargar_imagen_producto(producto['imagen'], 250)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Badge de puntos
        st.markdown(f"""
        <div style="text-align: center; margin-top: 0.5rem;">
            <span style="background: linear-gradient(135deg, #FFD700, #FFA500); 
                        color: white; padding: 0.5rem 1rem; border-radius: 20px; 
                        font-weight: bold; font-size: 0.9rem;">
                ⭐ {producto['puntos']} puntos
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para agregar al carrito
        if st.button(f"🛒 Agregar al Carrito", 
                   key=f"carrito_{producto['nombre']}", 
                   use_container_width=True):
            agregar_al_carrito(producto)
            st.rerun()
    
    with col_texto:
        # Título del producto
        st.markdown(f"""
        <h3 style="color: #8B4513; font-size: 1.4rem; margin-bottom: 0.5rem; 
                  font-family: 'Georgia', serif; border-bottom: 2px solid #F4A460; 
                  padding-bottom: 0.5rem;">
            {producto['nombre']}
        </h3>
        """, unsafe_allow_html=True)
        
        # Descripción del producto
        st.write(producto['descripcion'])
        
        # Información de precio y disponibilidad
        st.markdown(f"""
        <div style="background: #FFF8E1; padding: 0.8rem; border-radius: 10px; 
                   border-left: 4px solid #FFA500; margin: 1rem 0;">
            <p style="color: #8B4513; margin: 0; font-size: 0.9rem;">
                <strong>Valor original:</strong> ${producto['precio_original']:.2f}
            </p>
            <p style="color: {'#2E8B57' if disponible else '#FF6B6B'}; margin: 0.3rem 0 0 0; 
                       font-weight: bold; font-size: 0.9rem;">
                {"✅ Listo para canjear" if disponible else f"❌ Necesitas {producto['puntos'] - puntos_usuario} puntos más"}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón de canje
        if disponible:
            if st.button(f"🎁 Canjear {producto['puntos']} puntos", 
                       key=f"canjear_{producto['nombre']}", 
                       use_container_width=True):
                nuevos_puntos = update_points_via_rest(uid, -producto['puntos'])
                if nuevos_puntos >= 0:
                    st.success(f"¡Canjeado! Disfruta de tu {producto['nombre']}")
                    st.session_state.profile = None
                    time.sleep(2)
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

def mostrar_producto_destacado(producto, puntos_usuario, uid):
    """Versión compacta para productos destacados en inicio"""
    disponible = puntos_usuario >= producto['puntos']
    
    # Contenedor para el producto destacado
    st.markdown("""
    <div style="border-radius: 12px; padding: 1rem; margin: 1rem 0; background: white; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #F0F0F0;">
    """, unsafe_allow_html=True)
    
    col_imagen, col_texto = st.columns([2, 3])
    
    with col_imagen:
        cargar_imagen_producto(producto['imagen'], 180)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 0.5rem;">
            <span style="background: linear-gradient(135deg, #FFD700, #FFA500); 
                        color: white; padding: 0.3rem 0.8rem; border-radius: 15px; 
                        font-weight: bold; font-size: 0.8rem;">
                ⭐ {producto['puntos']} pts
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🛒 Agregar", key=f"carrito_compact_{producto['nombre']}", use_container_width=True):
            agregar_al_carrito(producto)
            st.rerun()
    
    with col_texto:
        # Título
        st.markdown(f"""
        <h4 style="color: #8B4513; font-size: 1.1rem; margin-bottom: 0.3rem; 
                  font-family: 'Georgia', serif;">
            {producto['nombre']}
        </h4>
        """, unsafe_allow_html=True)
        
        # Descripción
        st.write(producto['descripcion'])
        
        # Información de precio y disponibilidad
        st.markdown(f"""
        <div style="background: #FFF8E1; padding: 0.6rem; border-radius: 8px; 
                   border-left: 3px solid #FFA500; margin-top: 0.5rem;">
            <p style="color: #8B4513; margin: 0; font-size: 0.8rem;">
                <strong>Valor:</strong> ${producto['precio_original']:.2f}
            </p>
            <p style="color: {'#2E8B57' if disponible else '#FF6B6B'}; margin: 0.2rem 0 0 0; 
                       font-weight: bold; font-size: 0.8rem;">
                {"✅ Disponible" if disponible else f"❌ +{producto['puntos'] - puntos_usuario} pts"}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def mostrar_categorias_productos():
    """Selector de categorías estético"""
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h3 style="color: #8B4513; margin-bottom: 1rem;">Nuestras Categorías</h3>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(4)
    categorias = [
        {"nombre": "🥐 Panadería", "icono": "🥐"},
        {"nombre": "🍰 Pastelería", "icono": "🍰"},
        {"nombre": "☕ Bebidas", "icono": "☕"},
        {"nombre": "🎁 Especiales", "icono": "🎁"}
    ]
    
    for i, categoria in enumerate(categorias):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #FFF8E1; 
                        border-radius: 10px; border: 2px solid #F4A460;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{categoria['icono']}</div>
                <div style="color: #8B4513; font-weight: bold;">{categoria['nombre']}</div>
            </div>
            """, unsafe_allow_html=True)

# ==================================================
# SISTEMA DE PEDIDOS ONLINE
# ==================================================

def inicializar_carrito():
    if "carrito" not in st.session_state:
        st.session_state.carrito = []
    if "direccion_entrega" not in st.session_state:
        st.session_state.direccion_entrega = ""
    if "metodo_pago" not in st.session_state:
        st.session_state.metodo_pago = "efectivo"

def agregar_al_carrito(producto, cantidad=1, notas=""):
    item = {
        "id": str(uuid.uuid4())[:8],
        "producto": producto["nombre"],
        "puntos": producto["puntos"],
        "precio_original": producto["precio_original"],
        "cantidad": cantidad,
        "notas": notas,
        "imagen": producto["imagen"],
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.carrito.append(item)
    st.success(f"✅ {producto['nombre']} agregado al carrito")

def calcular_total_carrito():
    total_puntos = sum(item["puntos"] * item["cantidad"] for item in st.session_state.carrito)
    total_dinero = sum(item["precio_original"] * item["cantidad"] for item in st.session_state.carrito)
    return total_puntos, total_dinero

def mostrar_carrito():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8B4513;">🛒 Tu Carrito</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.carrito:
        st.info("🛒 Tu carrito está vacío")
        return
    
    total_puntos, total_dinero = calcular_total_carrito()
    
    # Resumen del carrito
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%); 
                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between;">
            <span><strong>Total Puntos:</strong></span>
            <span style="color: #8B4513; font-weight: bold;">{total_puntos} ⭐</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
            <span><strong>Valor Total:</strong></span>
            <span style="color: #2E8B57; font-weight: bold;">${total_dinero:.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Items del carrito
    for i, item in enumerate(st.session_state.carrito):
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                cargar_imagen_producto(item["imagen"], 80)
            
            with col2:
                st.write(f"**{item['producto']}**")
                st.write(f"Cantidad: {item['cantidad']}")
                if item['notas']:
                    st.write(f"Notas: {item['notas']}")
                st.write(f"Puntos: {item['puntos']} ⭐")
            
            with col3:
                if st.button("🗑️", key=f"eliminar_{i}"):
                    st.session_state.carrito.pop(i)
                    st.rerun()

def procesar_pedido(uid, tienda_id, metodo_pago, direccion_entrega=""):
    try:
        total_puntos, total_dinero = calcular_total_carrito()
        perfil = get_profile_via_rest(uid)
        
        if perfil.get('puntos', 0) < total_puntos:
            return False, "Puntos insuficientes"
        
        pedido_id = str(uuid.uuid4())[:8]
        pedido_data = {
            "pedido_id": pedido_id,
            "usuario_uid": uid,
            "usuario_nombre": perfil['nombre'],
            "usuario_email": perfil['email'],
            "items": st.session_state.carrito.copy(),
            "total_puntos": total_puntos,
            "total_dinero": total_dinero,
            "tienda_id": tienda_id,
            "metodo_pago": metodo_pago,
            "direccion_entrega": direccion_entrega,
            "estado": "pendiente",
            "timestamp": datetime.now().isoformat(),
            "estado_historial": [
                {
                    "estado": "pendiente",
                    "timestamp": datetime.now().isoformat(),
                    "nota": "Pedido creado"
                }
            ]
        }
        
        # Guardar pedido en Firebase
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/pedidos/{pedido_id}"
        document_data = {
            "fields": {
                "pedido_data": {"stringValue": json.dumps(pedido_data)}
            }
        }
        
        response = requests.patch(url, json=document_data)
        
        if response.status_code == 200:
            # Restar puntos al usuario
            update_points_via_rest(uid, -total_puntos)
            
            # Limpiar carrito
            st.session_state.carrito = []
            
            # Crear notificación
            crear_notificacion(
                uid,
                "🎉 ¡Pedido Confirmado!",
                f"Tu pedido #{pedido_id} ha sido recibido y está siendo procesado.",
                "pedido"
            )
            
            # Enviar SMS de confirmación si el usuario aceptó marketing
            if perfil.get('acepta_marketing', False) and perfil.get('telefono'):
                mensaje_sms = f"Arte París: ¡Pedido #{pedido_id} confirmado! Estamos preparando tu orden. Total: {total_puntos} puntos"
                enviar_sms_promocional(perfil['telefono'], mensaje_sms)
            
            return True, pedido_id
        else:
            return False, "Error al guardar pedido"
            
    except Exception as e:
        return False, str(e)

# ==================================================
# HISTORIAL DE TRANSACCIONES
# ==================================================

def obtener_historial_pedidos(uid):
    try:
        # En una implementación real, aquí harías la consulta a Firebase
        # Por ahora simulamos datos de ejemplo
        return []
    except:
        return []

def mostrar_historial_transacciones(uid):
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8B4513;">📊 Historial de Transacciones</h2>
    </div>
    """, unsafe_allow_html=True)
    
    pedidos = obtener_historial_pedidos(uid)
    
    if not pedidos:
        st.info("📝 Aún no tienes transacciones registradas")
        st.info("💡 **Prueba haciendo tu primer pedido** - Tus transacciones aparecerán aquí automáticamente")
        return
    
    for pedido in pedidos[:10]:
        with st.container():
            estado_info = ESTADOS_PEDIDO.get(pedido['estado'], pedido['estado'])
            fecha = datetime.fromisoformat(pedido['timestamp']).strftime("%d/%m/%Y %H:%M")
            
            st.markdown(f"""
            <div style="border: 1px solid #E9ECEF; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; 
                       background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #8B4513;">Pedido #{pedido['pedido_id']}</h4>
                    <span style="background: #E8F5E8; color: #2E8B57; padding: 0.3rem 0.8rem; 
                               border-radius: 15px; font-size: 0.8rem; font-weight: bold;">
                        {estado_info}
                    </span>
                </div>
                <div style="color: #666; margin: 0.5rem 0;">{fecha}</div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
                    <span>Items: {len(pedido['items'])}</span>
                    <span style="font-weight: bold; color: #8B4513;">{pedido['total_puntos']} ⭐</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def obtener_nombre_tienda(tienda_id):
    for tienda in TIENDAS:
        if tienda["id"] == tienda_id:
            return tienda["nombre"]
    return "Tienda no encontrada"

# ==================================================
# SISTEMA DE NOTIFICACIONES PUSH (SMS)
# ==================================================

def crear_notificacion(uid, titulo, mensaje, tipo="info"):
    try:
        # En implementación real, guardarías en Firebase
        # Por ahora solo mostramos en la interfaz
        if "notificaciones" not in st.session_state:
            st.session_state.notificaciones = []
        
        notificacion = {
            "id": str(uuid.uuid4())[:8],
            "uid": uid,
            "titulo": titulo,
            "mensaje": mensaje,
            "tipo": tipo,
            "leida": False,
            "timestamp": datetime.now().isoformat()
        }
        
        st.session_state.notificaciones.insert(0, notificacion)
        return True
    except:
        return False

def obtener_notificaciones(uid, no_leidas=False):
    if "notificaciones" not in st.session_state:
        st.session_state.notificaciones = []
    
    notificaciones = st.session_state.notificaciones
    
    if no_leidas:
        return [n for n in notificaciones if not n['leida']]
    
    return notificaciones

def marcar_notificacion_leida(notificacion_id):
    try:
        if "notificaciones" in st.session_state:
            for notif in st.session_state.notificaciones:
                if notif['id'] == notificacion_id:
                    notif['leida'] = True
                    break
        return True
    except:
        return False

def mostrar_notificaciones(uid):
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8B4513;">🔔 Notificaciones</h2>
    </div>
    """, unsafe_allow_html=True)
    
    notificaciones = obtener_notificaciones(uid)
    
    if not notificaciones:
        st.info("📱 No tienes notificaciones")
        # Crear notificación de bienvenida si es la primera vez
        if len(notificaciones) == 0:
            crear_notificacion(
                uid,
                "🎉 ¡Bienvenido a Arte París!",
                "Gracias por unirte a nuestro programa de fidelidad. Disfruta de tus beneficios.",
                "bienvenida"
            )
            st.rerun()
        return
    
    notificaciones_no_leidas = [n for n in notificaciones if not n['leida']]
    
    if notificaciones_no_leidas:
        st.markdown(f"""
        <div style="background: #FFF3CD; border: 1px solid #FFEAA7; border-radius: 10px; 
                   padding: 1rem; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.2rem; margin-right: 0.5rem;">🔔</span>
                <span style="font-weight: bold;">Tienes {len(notificaciones_no_leidas)} notificaciones no leídas</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    for notif in notificaciones[:10]:
        icono = "🔔" if not notif['leida'] else "📭"
        color_borde = "#3DCCC5" if not notif['leida'] else "#E9ECEF"
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style="border-left: 4px solid {color_borde}; padding-left: 1rem; margin: 0.5rem 0;">
                <div style="display: flex; align-items: center; margin-bottom: 0.3rem;">
                    <span style="font-size: 1.1rem; margin-right: 0.5rem;">{icono}</span>
                    <strong>{notif['titulo']}</strong>
                </div>
                <div style="color: #666; font-size: 0.9rem;">{notif['mensaje']}</div>
                <div style="color: #999; font-size: 0.8rem; margin-top: 0.3rem;">
                    {datetime.fromisoformat(notif['timestamp']).strftime("%d/%m/%Y %H:%M")}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if not notif['leida'] and st.button("📬", key=f"leer_{notif['id']}", help="Marcar como leída"):
                marcar_notificacion_leida(notif['id'])
                st.rerun()

# ==================================================
# SISTEMA DE ENVÍO DE SMS PROMOCIONALES
# ==================================================

def enviar_campana_sms():
    """Interfaz para enviar campañas SMS a usuarios"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8B4513;">📱 Campañas SMS</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("🚨 **Función administrativa** - Solo para uso autorizado")
    
    with st.form("campana_sms"):
        st.subheader("Nueva Campaña SMS")
        
        tipo_campana = st.selectbox(
            "Tipo de campaña",
            ["promocion", "oferta_especial", "evento", "recordatorio", "general"]
        )
        
        mensaje = st.text_area(
            "Mensaje SMS",
            placeholder="Escribe tu mensaje promocional (máx. 160 caracteres)...",
            max_chars=160,
            height=100
        )
        
        grupo_destinatarios = st.multiselect(
            "Destinatarios",
            ["todos_usuarios", "usuarios_activos", "cumpleaños_mes", "sin_compras_30_dias"],
            default=["todos_usuarios"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            enviar_inmediatamente = st.checkbox("Enviar inmediatamente", value=True)
        with col2:
            programar_envio = st.checkbox("Programar envío")
        
        if programar_envio:
            fecha_envio = st.date_input("Fecha de envío")
            hora_envio = st.time_input("Hora de envío")
        
        if st.form_submit_button("🚀 Enviar Campaña SMS", use_container_width=True):
            if mensaje:
                # Simular envío de campaña
                st.success("✅ Campaña SMS programada para envío")
                st.info(f"📊 La campaña llegará a aproximadamente X usuarios")
                
                # Aquí iría la lógica real para enviar SMS a todos los usuarios
                # que cumplan con los criterios seleccionados
            else:
                st.error("❌ El mensaje no puede estar vacío")

# ==================================================
# PROGRAMA DE REFERIDOS
# ==================================================

def generar_codigo_referido(uid):
    return f"ARTE{uid[:4].upper()}PARIS"

def obtener_info_referidos(uid):
    # En implementación real, consultarías Firebase
    return []

def registrar_referido(uid_referidor, email_referido):
    try:
        # En implementación real, guardarías en Firebase
        crear_notificacion(
            uid_referidor,
            "👥 Referido Registrado",
            f"Has referido a {email_referido}. Recibirás 25 puntos cuando se registre.",
            "referido"
        )
        return True
    except:
        return False

def mostrar_programa_referidos(uid):
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8B4513;">👥 Programa de Referidos</h2>
    </div>
    """, unsafe_allow_html=True)
    
    codigo_referido = generar_codigo_referido(uid)
    
    # Tarjeta de código de referido
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; color: white;
                margin-bottom: 2rem; box-shadow: 0 8px 25px rgba(139, 69, 19, 0.3);">
        <h3 style="color: white; margin-bottom: 1rem;">🎁 Invita a tus Amigos</h3>
        <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="color: #FFD700; margin: 0; font-family: 'Courier New', monospace;">
                {codigo_referido}
            </h2>
        </div>
        <p style="margin: 0; opacity: 0.9;">
            Comparte este código y ambos recibirán <strong>25 puntos ⭐</strong> cuando se registren
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario para referir amigos
    with st.form("referir_amigo"):
        st.subheader("📧 Invitar por Email")
        email_amigo = st.text_input("Email de tu amigo", placeholder="amigo@email.com")
        
        if st.form_submit_button("🎯 Enviar Invitación", use_container_width=True):
            if email_amigo:
                if registrar_referido(uid, email_amigo):
                    st.success(f"✅ Invitación enviada a {email_amigo}")
                else:
                    st.error("❌ Error al enviar la invitación")
    
    # Historial de referidos
    st.markdown("---")
    st.subheader("📊 Tus Referidos")
    
    referidos = obtener_info_referidos(uid)
    
    if not referidos:
        st.info("👥 Aún no has referido a nadie")
        st.info("💡 **Comparte tu código** - Cuando tus amigos se registren, aparecerán aquí")
    else:
        referidos_exitosos = [r for r in referidos if r['estado'] == 'activo']
        
        st.metric("Referidos Exitosos", len(referidos_exitosos))
        
        for referido in referidos:
            estado_color = {
                "pendiente": "#FFA500",
                "registrado": "#3DCCC5", 
                "activo": "#2E8B57"
            }.get(referido['estado'], "#666")
            
            st.markdown(f"""
            <div style="border-left: 4px solid {estado_color}; padding: 1rem; margin: 0.5rem 0; 
                       background: white; border-radius: 0 10px 10px 0;">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <strong>{referido['email_referido']}</strong>
                    <span style="background: {estado_color}; color: white; padding: 0.2rem 0.8rem; 
                               border-radius: 12px; font-size: 0.8rem;">
                        {referido['estado'].title()}
                    </span>
                </div>
                <div style="color: #666; font-size: 0.8rem; margin-top: 0.3rem;">
                    {datetime.fromisoformat(referido['fecha_registro']).strftime("%d/%m/%Y")}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==================================================
# GEOLOCALIZACIÓN DE TIENDAS
# ==================================================

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Fórmula de Haversine para calcular distancia
    R = 6371  # Radio de la Tierra en km
    
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def obtener_tiendas_cercanas(lat_usuario, lon_usuario, radio_km=10):
    tiendas_cercanas = []
    
    for tienda in TIENDAS:
        distancia = calcular_distancia(
            lat_usuario, lon_usuario,
            tienda["latitud"], tienda["longitud"]
        )
        
        if distancia <= radio_km:
            tienda_con_distancia = tienda.copy()
            tienda_con_distancia["distancia"] = round(distancia, 2)
            tiendas_cercanas.append(tienda_con_distancia)
    
    # Ordenar por distancia
    tiendas_cercanas.sort(key=lambda x: x["distancia"])
    return tiendas_cercanas

def mostrar_geolocalizacion_tiendas():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #8B4513;">📍 Nuestras Tiendas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de método para obtener ubicación
    metodo_ubicacion = st.radio(
        "Cómo encontrar tiendas cercanas:",
        ["📍 Usar mi ubicación actual", "🔍 Buscar por dirección"],
        horizontal=True
    )
    
    if metodo_ubicacion == "📍 Usar mi ubicación actual":
        # En una app real, aquí usarías el GPS del dispositivo
        # Por ahora simulamos una ubicación en el centro
        lat_usuario, lon_usuario = 4.710989, -74.072092
        
        st.info("""
        **📍 Funcionalidad de GPS**  
        En una aplicación móvil real, esta función usaría el GPS de tu dispositivo 
        para encontrar las tiendas más cercanas a tu ubicación actual.
        """)
        
        tiendas_cercanas = obtener_tiendas_cercanas(lat_usuario, lon_usuario)
        
    else:
        # Búsqueda por dirección (simulada)
        direccion = st.text_input("Ingresa tu dirección:", placeholder="Ej: Carrera 15 # 88-64")
        
        if direccion:
            # Simulación: asumimos que todas las tiendas están cerca
            tiendas_cercanas = TIENDAS.copy()
            for tienda in tiendas_cercanas:
                tienda["distancia"] = round(2.5 + (tienda["id"] * 0.8), 1)
            tiendas_cercanas.sort(key=lambda x: x["distancia"])
        else:
            tiendas_cercanas = []
    
    # Mostrar tiendas
    if not tiendas_cercanas:
        st.info("🔍 Ingresa una dirección para encontrar tiendas cercanas")
        return
    
    st.subheader(f"🏪 {len(tiendas_cercanas)} Tiendas Encontradas")
    
    for tienda in tiendas_cercanas:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <h4 style="color: #8B4513; margin-bottom: 0.5rem;">{tienda['nombre']}</h4>
                    <p style="margin: 0.2rem 0; color: #666;">📍 {tienda['direccion']}</p>
                    <p style="margin: 0.2rem 0; color: #666;">📞 {tienda['telefono']}</p>
                    <p style="margin: 0.2rem 0; color: #666;">🕒 {tienda['horario']}</p>
                    <div style="margin-top: 0.5rem;">
                        {" ".join([f"<span style='background: #E8F5E8; color: #2E8B57; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.8rem; margin-right: 0.3rem;'>{servicio}</span>" for servicio in tienda['servicios']])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                distancia = tienda.get('distancia', 'N/A')
                st.markdown(f"""
                <div style="text-align: center; background: #46E0E0; color: white; 
                           padding: 0.8rem; border-radius: 10px;">
                    <div style="font-size: 1.5rem;">🚗</div>
                    <div style="font-weight: bold; font-size: 1.1rem;">{distancia} km</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Botones de acción
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🗺️ Ver Ruta", key=f"ruta_{tienda['id']}", use_container_width=True):
                    st.info(f"🗺️ Navegando a {tienda['nombre']}...")
            with col2:
                if st.button("📞 Llamar", key=f"llamar_{tienda['id']}", use_container_width=True):
                    st.info(f"📞 Llamando a {tienda['telefono']}...")
            with col3:
                if st.button("🎯 Seleccionar", key=f"seleccionar_{tienda['id']}", use_container_width=True):
                    st.session_state.tienda_seleccionada = tienda['id']
                    st.success(f"✅ {tienda['nombre']} seleccionada para pedidos")
            
            st.markdown("---")

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
# FUNCIONES FIREBASE ACTUALIZADAS
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

def signup_user(email, password, nombre, telefono=None, fecha_cumpleanos=None, acepta_terminos=False, acepta_marketing=False):
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
            # Generar código de verificación
            codigo_verificacion = generar_codigo_verificacion()
            
            # Guardar código en sesión para verificación
            st.session_state.codigo_verificacion = codigo_verificacion
            st.session_state.email_verificacion = email
            st.session_state.datos_registro = {
                'nombre': nombre,
                'telefono': telefono,
                'fecha_cumpleanos': fecha_cumpleanos,
                'acepta_terminos': acepta_terminos,
                'acepta_marketing': acepta_marketing,
                'uid': result['localId']
            }
            
            # Enviar email de verificación
            if enviar_email_verificacion(email, nombre, codigo_verificacion):
                st.success("✅ Usuario registrado - Verifica tu email")
                return {"needs_verification": True, "localId": result['localId']}
            else:
                st.error("❌ Error enviando email de verificación")
                return None
        else:
            error_msg = result.get('error', {}).get('message', 'Error desconocido')
            raise Exception(f"Registro falló: {error_msg}")
    except Exception as e:
        raise Exception(f"Error en registro: {str(e)}")

def verify_email_code(codigo_ingresado):
    """Verifica el código de email ingresado por el usuario"""
    if (hasattr(st.session_state, 'codigo_verificacion') and 
        hasattr(st.session_state, 'email_verificacion') and
        hasattr(st.session_state, 'datos_registro')):
        
        if codigo_ingresado == st.session_state.codigo_verificacion:
            # Código correcto, guardar perfil completo
            datos = st.session_state.datos_registro
            success = save_profile_via_rest(
                datos['uid'],
                datos['nombre'],
                st.session_state.email_verificacion,
                datos['telefono'],
                datos['fecha_cumpleanos'],
                10,  # puntos de bienvenida
                datos['acepta_terminos'],
                datos['acepta_marketing']
            )
            
            if success:
                # Limpiar datos de verificación
                del st.session_state.codigo_verificacion
                del st.session_state.email_verificacion
                del st.session_state.datos_registro
                
                return True
        else:
            st.error("❌ Código de verificación incorrecto")
            return False
    
    st.error("❌ Error en el proceso de verificación")
    return False

def save_profile_via_rest(uid, nombre, email, telefono=None, fecha_cumpleanos=None, bonus_points=0, acepta_terminos=False, acepta_marketing=False):
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
                "acepta_marketing": {"booleanValue": acepta_marketing},
                "email_verificado": {"booleanValue": True},
                "telefono_verificado": {"booleanValue": telefono is not None}
            }
        }
        
        if telefono:
            document_data["fields"]["telefono"] = {"stringValue": telefono}
        
        if fecha_cumpleanos:
            document_data["fields"]["fecha_cumpleanos"] = {
                "timestampValue": fecha_cumpleanos.isoformat() + "T00:00:00Z"
            }
        
        response = requests.patch(url, json=document_data)
        
        if response.status_code == 200:
            # Enviar SMS de bienvenida si aceptó marketing y tiene teléfono
            if acepta_marketing and telefono:
                mensaje_bienvenida = f"¡Bienvenido a Arte París, {nombre}! Disfruta de 10 puntos de bienvenida. Canjea por deliciosos productos."
                enviar_sms_promocional(telefono, mensaje_bienvenida)
            
            return True
        return False
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
                    'acepta_marketing': data['fields'].get('acepta_marketing', {}).get('booleanValue', False),
                    'email_verificado': data['fields'].get('email_verificado', {}).get('booleanValue', False),
                    'telefono_verificado': data['fields'].get('telefono_verificado', {}).get('booleanValue', False)
                }
                
                if 'telefono' in data['fields']:
                    profile_data['telefono'] = data['fields']['telefono'].get('stringValue', '')
                
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
            
            # Enviar SMS de confirmación si el usuario aceptó marketing
            if puntos_ganados > 0 and perfil.get('acepta_marketing', False) and perfil.get('telefono'):
                mensaje_sms = f"Arte París: ¡+{puntos_ganados} puntos! Compra de ${monto_compra:.2f} registrada. Total: {nuevos_puntos} puntos"
                enviar_sms_promocional(perfil['telefono'], mensaje_sms)
            
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
# PÁGINAS NUEVAS PARA LAS FUNCIONALIDADES
# ==================================================

def mostrar_pagina_pedidos(uid, perfil):
    """Página unificada para pedidos, historial y notificaciones"""
    
    tab1, tab2, tab3, tab4 = st.tabs(["🛒 Carrito", "📊 Historial", "🔔 Notificaciones", "👥 Referidos"])
    
    with tab1:
        inicializar_carrito()
        mostrar_carrito()
        
        if st.session_state.carrito:
            st.markdown("---")
            st.subheader("🚀 Finalizar Pedido")
            
            col1, col2 = st.columns(2)
            
            with col1:
                tienda_seleccionada = st.selectbox(
                    "🏪 Seleccionar Tienda",
                    options=[t["id"] for t in TIENDAS],
                    format_func=lambda x: next((t["nombre"] for t in TIENDAS if t["id"] == x), "Tienda")
                )
                
                metodo_pago = st.radio(
                    "💳 Método de Pago",
                    ["efectivo", "tarjeta", "puntos"],
                    format_func=lambda x: {
                        "efectivo": "💵 Efectivo", 
                        "tarjeta": "💳 Tarjeta",
                        "puntos": "⭐ Solo Puntos"
                    }[x]
                )
            
            with col2:
                direccion_entrega = st.text_area(
                    "📍 Dirección de Entrega (opcional)",
                    placeholder="Si deseas delivery, ingresa tu dirección...",
                    height=80
                )
            
            total_puntos, total_dinero = calcular_total_carrito()
            puntos_usuario = perfil.get('puntos', 0)
            
            if metodo_pago == "puntos" and puntos_usuario < total_puntos:
                st.error(f"❌ No tienes suficientes puntos. Necesitas {total_puntos}, tienes {puntos_usuario}")
            else:
                if st.button("🎯 Confirmar Pedido", use_container_width=True, type="primary"):
                    success, resultado = procesar_pedido(uid, tienda_seleccionada, metodo_pago, direccion_entrega)
                    if success:
                        st.success(f"✅ ¡Pedido #{resultado} confirmado! Recibirás una notificación con los detalles.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {resultado}")
    
    with tab2:
        mostrar_historial_transacciones(uid)
    
    with tab3:
        mostrar_notificaciones(uid)
    
    with tab4:
        mostrar_programa_referidos(uid)

def mostrar_pagina_tiendas():
    """Página de geolocalización de tiendas"""
    mostrar_geolocalizacion_tiendas()

# ==================================================
# PÁGINA DE VERIFICACIÓN DE EMAIL
# ==================================================

def mostrar_pagina_verificacion():
    """Página para verificar el email del usuario"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <h1 style="color: #8B4513; margin-bottom: 1rem;">📧 Verifica tu Email</h1>
        <p style="color: #666; margin-bottom: 2rem;">Hemos enviado un código de verificación a tu correo electrónico</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("🔐 **Verificación Requerida**\n\nPara proteger tu cuenta, necesitamos verificar tu dirección de email.")
        
        codigo = st.text_input(
            "Código de Verificación",
            placeholder="Ingresa el código de 6 dígitos",
            max_chars=6
        )
        
        if st.button("✅ Verificar Cuenta", use_container_width=True):
            if codigo and len(codigo) == 6:
                if verify_email_code(codigo):
                    st.success("🎉 ¡Email verificado correctamente! Tu cuenta ha sido activada.")
                    st.session_state.user = {"localId": st.session_state.datos_registro['uid']}
                    st.session_state.pagina_actual = "Inicio"
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("❌ El código debe tener 6 dígitos")
        
        st.markdown("---")
        st.write("¿No recibiste el código?")
        if st.button("🔄 Reenviar Código", use_container_width=True):
            if hasattr(st.session_state, 'email_verificacion') and hasattr(st.session_state, 'datos_registro'):
                nuevo_codigo = generar_codigo_verificacion()
                st.session_state.codigo_verificacion = nuevo_codigo
                if enviar_email_verificacion(
                    st.session_state.email_verificacion,
                    st.session_state.datos_registro['nombre'],
                    nuevo_codigo
                ):
                    st.success("✅ Código reenviado a tu email")

# ==================================================
# MENÚ INFERIOR ACTUALIZADO
# ==================================================
def mostrar_menu_inferior_actualizado():
    """Menú inferior actualizado con nuevas funcionalidades"""
    
    st.markdown("""
    <style>
    .bottom-nav-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 2px solid #3DCCC5;
        padding: 8px 0;
        z-index: 9999;
        display: flex;
        justify-content: space-around;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    .nav-item {
        text-align: center;
        padding: 5px;
        flex: 1;
        border-radius: 8px;
        margin: 0 2px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .nav-item.active {
        background: #f0f9f9;
        color: #3DCCC5;
        font-weight: bold;
    }
    
    .nav-icon {
        font-size: 18px;
        margin-bottom: 2px;
    }
    
    .nav-text {
        font-size: 11px;
        font-weight: normal;
    }
    
    .main-content {
        margin-bottom: 70px;
        padding-bottom: 10px;
    }
    
    .nav-button-overlay {
        position: fixed;
        bottom: 0;
        height: 60px;
        background: transparent;
        border: none;
        cursor: pointer;
        z-index: 10000;
    }
    
    .nav-button-1 { left: 0%; width: 20%; }
    .nav-button-2 { left: 20%; width: 20%; }
    .nav-button-3 { left: 40%; width: 20%; }
    .nav-button-4 { left: 60%; width: 20%; }
    .nav-button-5 { left: 80%; width: 20%; }
    </style>
    """, unsafe_allow_html=True)
    
    pagina_actual = st.session_state.get('pagina_actual', 'Inicio')
    
    # Mostrar el menú visual
    menu_html = f"""
    <div class="bottom-nav-container">
        <div class="nav-item {'active' if pagina_actual == 'Inicio' else ''}" id="nav-inicio">
            <div class="nav-icon">🏠</div>
            <div class="nav-text">Inicio</div>
        </div>
        <div class="nav-item {'active' if pagina_actual == 'Productos' else ''}" id="nav-productos">
            <div class="nav-icon">🎁</div>
            <div class="nav-text">Productos</div>
        </div>
        <div class="nav-item {'active' if pagina_actual == 'Pedidos' else ''}" id="nav-pedidos">
            <div class="nav-icon">🛒</div>
            <div class="nav-text">Pedidos</div>
        </div>
        <div class="nav-item {'active' if pagina_actual == 'Tiendas' else ''}" id="nav-tiendas">
            <div class="nav-icon">📍</div>
            <div class="nav-text">Tiendas</div>
        </div>
        <div class="nav-item {'active' if pagina_actual == 'Perfil' else ''}" id="nav-perfil">
            <div class="nav-icon">👤</div>
            <div class="nav-text">Perfil</div>
        </div>
    </div>
    """
    st.markdown(menu_html, unsafe_allow_html=True)
    
    # Botones invisibles para navegación
    st.markdown('<div style="position: relative; height: 60px;">', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("", key="nav_inicio_hidden"):
            if st.session_state.pagina_actual != "Inicio":
                st.session_state.pagina_actual = "Inicio"
                st.rerun()
    
    with col2:
        if st.button(" ", key="nav_productos_hidden"):
            if st.session_state.pagina_actual != "Productos":
                st.session_state.pagina_actual = "Productos"
                st.rerun()
    
    with col3:
        if st.button("  ", key="nav_pedidos_hidden"):
            if st.session_state.pagina_actual != "Pedidos":
                st.session_state.pagina_actual = "Pedidos"
                st.rerun()
    
    with col4:
        if st.button("   ", key="nav_tiendas_hidden"):
            if st.session_state.pagina_actual != "Tiendas":
                st.session_state.pagina_actual = "Tiendas"
                st.rerun()
    
    with col5:
        if st.button("    ", key="nav_perfil_hidden"):
            if st.session_state.pagina_actual != "Perfil":
                st.session_state.pagina_actual = "Perfil"
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

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
        background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 25px;
        font-weight: bold;
        margin: 0.25rem 0;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #A0522D 0%, #8B4513 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
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
    
    /* Ocultar los botones del menú */
    div[data-testid="column"] button {
        opacity: 0;
        height: 60px;
        width: 100%;
        position: absolute;
        bottom: 0;
        cursor: pointer;
        z-index: 10000;
    }
    
    /* Posicionar cada botón en su área correspondiente */
    div[data-testid="column"]:nth-child(1) button {
        left: 0;
    }
    div[data-testid="column"]:nth-child(2) button {
        left: 20%;
    }
    div[data-testid="column"]:nth-child(3) button {
        left: 40%;
    }
    div[data-testid="column"]:nth-child(4) button {
        left: 60%;
    }
    div[data-testid="column"]:nth-child(5) button {
        left: 80%;
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
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "notificaciones" not in st.session_state:
    st.session_state.notificaciones = []
if "needs_verification" not in st.session_state:
    st.session_state.needs_verification = False

# ==================================================
# INTERFAZ PRINCIPAL
# ==================================================

# Primero verificar si el usuario necesita verificación de email
if hasattr(st.session_state, 'needs_verification') and st.session_state.needs_verification:
    mostrar_pagina_verificacion()

elif st.session_state.user:
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
            # HERO SECTION MEJORADA PARA INICIO
            mostrar_hero_inicio()
            
            mostrar_logo()
            
            # TARJETA DE PUNTOS ELEGANTE
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); 
                        padding: 1.5rem; border-radius: 15px; margin: 1rem 0; color: white; 
                        text-align: center; box-shadow: 0 8px 25px rgba(139, 69, 19, 0.3);">
                <h3 style="margin: 0; color: white;">⭐ Tus Puntos Arte París</h3>
                <h1 style="font-size: 3rem; margin: 0.5rem 0; color: #FFD700;">{puntos_usuario}</h1>
                <p style="margin: 0; opacity: 0.9;">Acumulados para vivir experiencias únicas</p>
            </div>
            """, unsafe_allow_html=True)
            
            # OFERTA DE CUMPLEAÑOS
            fecha_cumpleanos = perfil.get('fecha_cumpleanos')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                            padding: 1.5rem; border-radius: 15px; margin: 1rem 0; 
                            text-align: center; box-shadow: 0 8px 25px rgba(255, 165, 0, 0.3);">
                    <h3 style="color: #8B4513; margin: 0;">🎉 ¡Feliz Cumpleaños!</h3>
                    <p style="color: #8B4513; margin: 0.5rem 0;">Disfruta de regalos exclusivos en tu día especial</p>
                    <div style="background: rgba(255,255,255,0.3); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                        <h4 style="color: #8B4513; margin: 0;">🎁 Café especial + Dulce sorpresa</h4>
                        <p style="color: #8B4513; margin: 0.5rem 0 0 0; font-weight: bold;">¡GRATIS para ti hoy!</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # IMAGEN PRINCIPAL
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h3 style="color: #8B4513; font-family: 'Georgia', serif; margin-bottom: 1rem;">
                    ☕ Nuestra Esencia
                </h3>
            </div>
            """, unsafe_allow_html=True)
            cargar_imagen_movil(CONFIG_IMAGENES["hero"])
            
            # ACCIONES RÁPIDAS
            st.markdown("""
            <div style="text-align: center; margin: 2rem 0;">
                <h3 style="color: #8B4513; font-family: 'Georgia', serif; margin-bottom: 1rem;">
                    🚀 Acciones Rápidas
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 Registrar Compra", use_container_width=True):
                    st.session_state.pagina_actual = "Perfil"
                    st.rerun()
            with col2:
                if st.button("🎁 Canjear Puntos", use_container_width=True):
                    st.session_state.pagina_actual = "Productos"
                    st.rerun()
            with col3:
                if st.button("🛒 Ver Pedidos", use_container_width=True):
                    st.session_state.pagina_actual = "Pedidos"
                    st.rerun()
            
            # PRODUCTOS DESTACADOS
            st.markdown("""
            <div style="text-align: center; margin: 3rem 0 2rem 0;">
                <h3 style="color: #8B4513; font-family: 'Georgia', serif; 
                          border-bottom: 3px solid #F4A460; padding-bottom: 0.5rem;
                          display: inline-block;">
                    🌟 Productos Destacados
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar solo productos destacados en diseño compacto
            productos_destacados = [p for p in PRODUCTOS if p.get('destacado', False)]
            for producto in productos_destacados[:2]:  # Máximo 2 productos en inicio
                mostrar_producto_destacado(producto, puntos_usuario, uid)
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Botón para ver todos los productos
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("📋 Ver Todos los Productos", use_container_width=True):
                    st.session_state.pagina_actual = "Productos"
                    st.rerun()
        
        elif st.session_state.pagina_actual == "Productos":
            # HERO SECTION MEJORADA
            mostrar_hero_productos()
            
            # TARJETA DE PUNTOS
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%); 
                        padding: 1.5rem; border-radius: 15px; margin: 1rem 0; color: white; 
                        text-align: center; box-shadow: 0 8px 25px rgba(139, 69, 19, 0.3);">
                <h3 style="margin: 0; color: white;">⭐ Tus Puntos Disponibles</h3>
                <h1 style="font-size: 3rem; margin: 0.5rem 0; color: #FFD700;">{puntos_usuario}</h1>
                <p style="margin: 0; opacity: 0.9;">Listos para canjear por experiencias únicas</p>
            </div>
            """, unsafe_allow_html=True)
            
            # OFERTA DE CUMPLEAÑOS
            fecha_cumpleanos = perfil.get('fecha_cumpleanos')
            if fecha_cumpleanos and es_cumpleanos_hoy(fecha_cumpleanos):
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
                            padding: 1.5rem; border-radius: 15px; margin: 1rem 0; 
                            text-align: center; box-shadow: 0 8px 25px rgba(255, 165, 0, 0.3);">
                    <h3 style="color: #8B4513; margin: 0;">🎉 ¡Feliz Cumpleaños!</h3>
                    <p style="color: #8B4513; margin: 0.5rem 0;">Disfruta de regalos exclusivos en tu día especial</p>
                    <div style="background: rgba(255,255,255,0.3); padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                        <h4 style="color: #8B4513; margin: 0;">🎁 Café especial + Dulce sorpresa</h4>
                        <p style="color: #8B4513; margin: 0.5rem 0 0 0; font-weight: bold;">¡GRATIS para ti hoy!</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # CATEGORÍAS
            mostrar_categorias_productos()
            
            # PRODUCTOS
            st.markdown("""
            <div style="text-align: center; margin: 3rem 0 2rem 0;">
                <h2 style="color: #8B4513; font-family: 'Georgia', serif; 
                          border-bottom: 3px solid #F4A460; padding-bottom: 0.5rem;
                          display: inline-block;">
                    Nuestra Selección
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
            for producto in PRODUCTOS:
                mostrar_producto_elegante(producto, puntos_usuario, uid)
        
        elif st.session_state.pagina_actual == "Pedidos":
            mostrar_pagina_pedidos(uid, perfil)
            
        elif st.session_state.pagina_actual == "Tiendas":
            mostrar_pagina_tiendas()
            
        elif st.session_state.pagina_actual == "Perfil":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #3DCCC5; margin: 0;">👤 Tu Perfil</h2>
                <p style="color: #666;">Gestiona tu cuenta Arte París</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar estado de verificación
            col1, col2 = st.columns(2)
            with col1:
                if perfil.get('email_verificado', False):
                    st.success("✅ Email verificado")
                else:
                    st.warning("⚠️ Email no verificado")
            
            with col2:
                if perfil.get('telefono_verificado', False):
                    st.success("✅ Teléfono verificado")
                else:
                    st.warning("⚠️ Teléfono no verificado")
            
            st.markdown(f"""
            <div class="mobile-card">
                <h4 style="color: #2C5530;">👋 Hola, {perfil['nombre']}</h4>
                <p style="color: #4A6741;">📧 {perfil['email']}</p>
                <p style="color: #4A6741;">📱 {perfil.get('telefono', 'No registrado')}</p>
                <p style="color: #4A6741;">⭐ {puntos_usuario} puntos acumulados</p>
                <p style="color: #4A6741;">💰 ${perfil.get('total_compras', 0):.2f} gastados</p>
                <p style="color: #4A6741;">🎫 {perfil.get('tickets_registrados', 0)} tickets registrados</p>
                <p style="color: #4A6741;">{"🎂 " + perfil['fecha_cumpleanos'].strftime('%d/%m/%Y') if perfil.get('fecha_cumpleanos') else "🎂 Sin fecha de cumpleaños"}</p>
            </div>
            """, unsafe_allow_html=True)
            
            mostrar_registro_compra_seguro(uid)
            
            # Sección administrativa (solo para demostración)
            if perfil.get('email') == 'admin@arteparis.com':  # Ejemplo de admin
                st.markdown("---")
                st.subheader("👨‍💼 Panel Administrativo")
                enviar_campana_sms()
            
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.user = None
                st.session_state.profile = None
                st.session_state.pagina_actual = "Inicio"
                st.session_state.carrito = []
                st.session_state.notificaciones = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # MOSTRAR MENÚ INFERIOR ACTUALIZADO
        mostrar_menu_inferior_actualizado()

else:
    # PÁGINA DE LOGIN (sin menú inferior)
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
            
            # NUEVO CAMPO: Teléfono
            telefono = st.text_input(
                "📱 Número de Teléfono (opcional)",
                placeholder="+1234567890",
                help="Formato internacional: + seguido del código país y número"
            )
            
            if telefono and not validar_telefono(telefono):
                st.error("❌ Formato de teléfono inválido. Usa formato internacional: +1234567890")
            
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
                "**Sí, quiero recibir ofertas exclusivas por SMS y email**",
                value=False
            )
            st.markdown("""
            <div class="terms-section">
                <small><strong>Mantente al tanto.</strong> Recibe ofertas especiales, promociones y novedades de Arte París por SMS y email.</small>
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
                    if not validar_email(email):
                        st.error("❌ Formato de email inválido")
                    elif telefono and not validar_telefono(telefono):
                        st.error("❌ Formato de teléfono inválido")
                    elif not acepta_terminos:
                        st.error("❌ Debes aceptar las Condiciones de Uso")
                    else:
                        try:
                            result = signup_user(email, password, nombre, telefono, fecha_cumpleanos, acepta_terminos, acepta_marketing)
                            if result and result.get("needs_verification"):
                                st.session_state.needs_verification = True
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
        <div class="benefit-item">
            <span>🛒 Pedidos online</span>
        </div>
        <div class="benefit-item">
            <span>📱 Notificaciones SMS</span>
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
        <div class="benefit-item">
            <span>👥 Programa de referidos</span>
        </div>
        <div class="benefit-item">
            <span>🔒 Cuenta verificada</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">'
    '☕ <strong>Arte Paris Deli café</strong> - Donde cada taza cuenta una historia 🎨'
    '</div>',
    unsafe_allow_html=True
)
