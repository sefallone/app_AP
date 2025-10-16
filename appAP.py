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

# ==================================================
# CONFIGURACIÓN FIREBASE (Existente)
# ==================================================
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# ==================================================
# NUEVAS CONFIGURACIONES
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
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/pedidos?where=usuario_uid='{uid}'&orderBy=timestamp desc"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            pedidos = []
            
            if 'documents' in data:
                for doc in data['documents']:
                    pedido_data = json.loads(doc['fields']['pedido_data']['stringValue'])
                    pedidos.append(pedido_data)
            
            return pedidos
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
        return
    
    for pedido in pedidos[:10]:  # Mostrar últimos 10 pedidos
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
            
            with st.expander("Ver detalles"):
                for item in pedido['items']:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {item['producto']} x{item['cantidad']}")
                    with col2:
                        st.write(f"{item['puntos']} ⭐")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Tienda:** {obtener_nombre_tienda(pedido['tienda_id'])}")
                    st.write(f"**Método de pago:** {pedido['metodo_pago']}")
                with col2:
                    st.write(f"**Total puntos:** {pedido['total_puntos']} ⭐")
                    st.write(f"**Valor total:** ${pedido['total_dinero']:.2f}")

def obtener_nombre_tienda(tienda_id):
    for tienda in TIENDAS:
        if tienda["id"] == tienda_id:
            return tienda["nombre"]
    return "Tienda no encontrada"

# ==================================================
# SISTEMA DE NOTIFICACIONES PUSH
# ==================================================

def crear_notificacion(uid, titulo, mensaje, tipo="info"):
    try:
        notificacion_id = str(uuid.uuid4())[:8]
        notificacion_data = {
            "id": notificacion_id,
            "uid": uid,
            "titulo": titulo,
            "mensaje": mensaje,
            "tipo": tipo,
            "leida": False,
            "timestamp": datetime.now().isoformat()
        }
        
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/notificaciones/{notificacion_id}"
        document_data = {
            "fields": {
                "notificacion_data": {"stringValue": json.dumps(notificacion_data)}
            }
        }
        
        requests.patch(url, json=document_data)
        return True
    except:
        return False

def obtener_notificaciones(uid, no_leidas=False):
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/notificaciones?where=uid='{uid}'&orderBy=timestamp desc"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            notificaciones = []
            
            if 'documents' in data:
                for doc in data['documents']:
                    notif_data = json.loads(doc['fields']['notificacion_data']['stringValue'])
                    if no_leidas and notif_data['leida']:
                        continue
                    notificaciones.append(notif_data)
            
            return notificaciones
        return []
    except:
        return []

def marcar_notificacion_leida(notificacion_id):
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/notificaciones/{notificacion_id}"
        
        # Primero obtener la notificación actual
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            notif_data = json.loads(data['fields']['notificacion_data']['stringValue'])
            notif_data['leida'] = True
            
            # Actualizar
            update_data = {
                "fields": {
                    "notificacion_data": {"stringValue": json.dumps(notif_data)}
                }
            }
            requests.patch(url, json=update_data)
            return True
        return False
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
    
    for notif in notificaciones[:10]:  # Mostrar últimas 10
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
# PROGRAMA DE REFERIDOS
# ==================================================

def generar_codigo_referido(uid):
    return f"ARTE{uid[:4].upper()}PARIS"

def obtener_info_referidos(uid):
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/referidos?where=usuario_referidor='{uid}'"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            referidos = []
            
            if 'documents' in data:
                for doc in data['documents']:
                    referido_data = json.loads(doc['fields']['referido_data']['stringValue'])
                    referidos.append(referido_data)
            
            return referidos
        return []
    except:
        return []

def registrar_referido(uid_referidor, email_referido):
    try:
        referido_id = str(uuid.uuid4())[:8]
        referido_data = {
            "id": referido_id,
            "usuario_referidor": uid_referidor,
            "email_referido": email_referido,
            "fecha_registro": datetime.now().isoformat(),
            "estado": "pendiente",  # pendiente, registrado, activo
            "puntos_otorgados": False
        }
        
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['PROJECT_ID']}/databases/(default)/documents/referidos/{referido_id}"
        document_data = {
            "fields": {
                "referido_data": {"stringValue": json.dumps(referido_data)}
            }
        }
        
        response = requests.patch(url, json=document_data)
        return response.status_code == 200
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
                    # Aquí podrías integrar con un servicio de email
                else:
                    st.error("❌ Error al enviar la invitación")
    
    # Historial de referidos
    st.markdown("---")
    st.subheader("📊 Tus Referidos")
    
    referidos = obtener_info_referidos(uid)
    
    if not referidos:
        st.info("👥 Aún no has referido a nadie")
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
# ACTUALIZACIÓN DEL MENÚ INFERIOR
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
# ACTUALIZACIÓN DE LA INTERFAZ PRINCIPAL
# ==================================================

# ... (tu código existente continúa)

# ACTUALIZAR LA SECCIÓN PRINCIPAL DONDE SE MANEJAN LAS PÁGINAS:

# En la parte donde manejas st.session_state.pagina_actual, agregar:

elif st.session_state.pagina_actual == "Pedidos":
    mostrar_pagina_pedidos(uid, perfil)

elif st.session_state.pagina_actual == "Tiendas":
    mostrar_pagina_tiendas()

# Y actualizar el menú inferior para usar la versión nueva:
mostrar_menu_inferior_actualizado()
