import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import io

# Configuración de la página
st.set_page_config(
    page_title="Café & Pastelería Delicia",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #8B4513;
        text-align: center;
        margin-bottom: 2rem;
    }
    .category-header {
        font-size: 2rem;
        color: #654321;
        border-bottom: 2px solid #8B4513;
        padding-bottom: 0.5rem;
    }
    .product-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 0.5rem;
        text-align: center;
    }
    .price-tag {
        font-size: 1.2rem;
        color: #8B4513;
        font-weight: bold;
    }
    .points-card {
        background: linear-gradient(135deg, #8B4513, #D2691E);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sistema de base de datos simple (en producción usarías una base de datos real)
def inicializar_base_datos():
    if 'usuarios' not in st.session_state:
        st.session_state.usuarios = {}
    if 'transacciones' not in st.session_state:
        st.session_state.transacciones = []

# Datos de productos
productos = {
    "Cafés": [
        {"nombre": "Espresso", "precio": 2.50, "descripcion": "Café intenso y aromático"},
        {"nombre": "Cappuccino", "precio": 3.50, "descripcion": "Café con leche espumosa"},
        {"nombre": "Latte", "precio": 4.00, "descripcion": "Café suave con leche vaporizada"},
        {"nombre": "Mocha", "precio": 4.50, "descripcion": "Café con chocolate y leche"},
    ],
    "Pasteles": [
        {"nombre": "Tarta de Chocolate", "precio": 4.50, "descripcion": "Deliciosa tarta de chocolate belga"},
        {"nombre": "Cheesecake", "precio": 4.00, "descripcion": "Suave cheesecake con base de galleta"},
        {"nombre": "Tarta de Zanahoria", "precio": 3.75, "descripcion": "Especialidad de la casa"},
        {"nombre": "Croissant", "precio": 2.00, "descripcion": "Crujiente y mantecoso"},
    ],
    "Bebidas Frías": [
        {"nombre": "Iced Coffee", "precio": 3.50, "descripcion": "Café frío refrescante"},
        {"nombre": "Frappé", "precio": 4.50, "descripcion": "Bebida helada de café"},
        {"nombre": "Té Helado", "precio": 3.00, "descripcion": "Té frío natural"},
    ]
}

def main():
    inicializar_base_datos()
    
    # Header principal
    st.markdown('<h1 class="main-header">☕ Café & Pastelería Delicia</h1>', unsafe_allow_html=True)
    
    # Barra de navegación
    menu = st.sidebar.selectbox("Navegación", ["Inicio", "Menú", "Pedidos", "Programa Fidelidad", "Contacto", "Sobre Nosotros"])
    
    if menu == "Inicio":
        mostrar_inicio()
    elif menu == "Menú":
        mostrar_menu()
    elif menu == "Pedidos":
        mostrar_pedidos()
    elif menu == "Programa Fidelidad":
        mostrar_programa_fidelidad()
    elif menu == "Contacto":
        mostrar_contacto()
    elif menu == "Sobre Nosotros":
        mostrar_sobre_nosotros()

def mostrar_inicio():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## ¡Bienvenido a nuestra cafetería!")
        st.write("""
        Disfruta de los mejores cafés y pasteles artesanales en un ambiente acogedor.
        
        **¡Nuevo! Programa de Fidelidad**
        - Regístrate y obtén 10 puntos de bienvenida
        - Gana 10 puntos por cada 1000 Bs en compras
        - Canjea puntos por productos gratis
        
        **Horario:**
        - Lunes a Viernes: 7:00 AM - 8:00 PM
        - Sábados y Domingos: 8:00 AM - 6:00 PM
        """)
    
    with col2:
        st.image("https://via.placeholder.com/300x200", caption="Nuestro acogedor espacio")

def mostrar_menu():
    st.markdown("## 🍰 Nuestro Menú")
    
    for categoria, items in productos.items():
        st.markdown(f'<h2 class="category-header">{categoria}</h2>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        for idx, producto in enumerate(items):
            with cols[idx % 4]:
                with st.container():
                    st.markdown(f'<div class="product-card">', unsafe_allow_html=True)
                    st.write(f"**{producto['nombre']}**")
                    st.write(producto['descripcion'])
                    st.markdown(f'<p class="price-tag">{producto["precio"]:.2f} Bs</p>', unsafe_allow_html=True)
                    
                    if st.button(f"Agregar 🛒", key=f"{categoria}_{producto['nombre']}"):
                        agregar_al_carrito(producto)
                        st.success(f"¡{producto['nombre']} agregado al carrito!")
                    
                    st.markdown('</div>', unsafe_allow_html=True)

def mostrar_pedidos():
    st.markdown("## 🛒 Tu Pedido")
    
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    
    if not st.session_state.carrito:
        st.info("Tu carrito está vacío")
    else:
        total = 0
        for item in st.session_state.carrito:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{item['nombre']}**")
            with col2:
                st.write(f"{item['precio']:.2f} Bs")
            with col3:
                if st.button("❌", key=f"eliminar_{item['nombre']}"):
                    st.session_state.carrito.remove(item)
                    st.rerun()
            
            total += item['precio']
        
        st.markdown(f"**Total: {total:.2f} Bs**")
        
        # Calcular puntos que ganaría
        puntos_ganados = calcular_puntos_compra(total)
        st.info(f"¡Con esta compra ganarías {puntos_ganados} puntos en nuestro programa de fidelidad!")
        
        # Información del pedido
        st.markdown("### Información de entrega")
        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")
        direccion = st.text_area("Dirección de entrega")
        notas = st.text_area("Notas especiales para tu pedido")
        
        # Opción para usuario registrado
        st.markdown("### ¿Eres miembro de nuestro programa de fidelidad?")
        codigo_usuario = st.text_input("Código de usuario (opcional)")
        
        if st.button("Realizar Pedido", type="primary"):
            if nombre and telefono and direccion:
                # Generar ticket de compra
                ticket = generar_ticket_compra(nombre, total, codigo_usuario, puntos_ganados)
                
                st.success("¡Pedido realizado con éxito! Te contactaremos pronto.")
                st.download_button(
                    label="📄 Descargar Ticket",
                    data=ticket,
                    file_name=f"ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                # Si hay código de usuario, asignar puntos
                if codigo_usuario and codigo_usuario in st.session_state.usuarios:
                    usuario = st.session_state.usuarios[codigo_usuario]
                    usuario['puntos'] += puntos_ganados
                    usuario['historial_compras'].append({
                        'fecha': datetime.now().isoformat(),
                        'monto': total,
                        'puntos_ganados': puntos_ganados
                    })
                    st.success(f"¡Se han asignado {puntos_ganados} puntos a tu cuenta!")
                
                st.session_state.carrito = []
            else:
                st.error("Por favor completa todos los campos requeridos")

def mostrar_programa_fidelidad():
    st.markdown("## 🏆 Programa de Fidelidad")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Registrarse", "Mi Cuenta", "Escanear Ticket", "Premios"])
    
    with tab1:
        mostrar_registro()
    
    with tab2:
        mostrar_mi_cuenta()
    
    with tab3:
        mostrar_escanear_ticket()
    
    with tab4:
        mostrar_premios()

def mostrar_registro():
    st.markdown("### ¡Únete a nuestro programa de fidelidad!")
    st.write("Regístrate ahora y obtén **10 puntos de bienvenida** inmediatamente")
    
    with st.form("registro_form"):
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Email")
        telefono = st.text_input("Teléfono")
        fecha_nacimiento = st.date_input("Fecha de nacimiento")
        
        if st.form_submit_button("Registrarme"):
            if nombre and email and telefono:
                codigo_usuario = generar_codigo_usuario(nombre)
                
                st.session_state.usuarios[codigo_usuario] = {
                    'nombre': nombre,
                    'email': email,
                    'telefono': telefono,
                    'fecha_nacimiento': fecha_nacimiento.isoformat() if fecha_nacimiento else None,
                    'fecha_registro': datetime.now().isoformat(),
                    'puntos': 10,  # Puntos de bienvenida
                    'historial_compras': []
                }
                
                st.success(f"¡Registro exitoso! Tu código de usuario es: **{codigo_usuario}**")
                st.info("Guarda este código para acumular puntos en tus compras")
            else:
                st.error("Por favor completa todos los campos requeridos")

def mostrar_mi_cuenta():
    st.markdown("### Consulta tu saldo de puntos")
    
    codigo_usuario = st.text_input("Ingresa tu código de usuario")
    
    if codigo_usuario:
        if codigo_usuario in st.session_state.usuarios:
            usuario = st.session_state.usuarios[codigo_usuario]
            
            st.markdown(f'<div class="points-card">', unsafe_allow_html=True)
            st.markdown(f"### ¡Hola, {usuario['nombre']}!")
            st.markdown(f"## {usuario['puntos']} Puntos")
            st.markdown("Disponibles para canjear")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Historial de compras
            st.markdown("### Historial de Compras")
            if usuario['historial_compras']:
                for compra in reversed(usuario['historial_compras'][-5:]):  # Últimas 5 compras
                    fecha = datetime.fromisoformat(compra['fecha']).strftime("%d/%m/%Y %H:%M")
                    st.write(f"**{fecha}** - {compra['monto']:.2f} Bs - +{compra['puntos_ganados']} puntos")
            else:
                st.info("Aún no tienes compras registradas")
        else:
            st.error("Código de usuario no encontrado. Verifica el código o regístrate.")

def mostrar_escanear_ticket():
    st.markdown("### Escanear Ticket de Compra")
    st.write("¿Olvidaste proporcionar tu código en la compra? Escanea tu ticket para acumular puntos")
    
    uploaded_file = st.file_uploader("Sube una foto de tu ticket", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # En una implementación real, aquí procesarías la imagen con OCR
        # Por ahora simulamos el proceso
        image = Image.open(uploaded_file)
        st.image(image, caption="Ticket escaneado", width=300)
        
        st.info("Procesando ticket...")
        
        # Simulación de procesamiento
        time.sleep(2)
        
        # Datos simulados del ticket (en producción usarías OCR)
        codigo_usuario = st.text_input("Ingresa tu código de usuario para asignar los puntos")
        monto_compra = st.number_input("Monto total de la compra (Bs)", min_value=0.0, step=0.1)
        
        if st.button("Asignar Puntos"):
            if codigo_usuario and monto_compra > 0:
                if codigo_usuario in st.session_state.usuarios:
                    puntos_ganados = calcular_puntos_compra(monto_compra)
                    usuario = st.session_state.usuarios[codigo_usuario]
                    usuario['puntos'] += puntos_ganados
                    usuario['historial_compras'].append({
                        'fecha': datetime.now().isoformat(),
                        'monto': monto_compra,
                        'puntos_ganados': puntos_ganados
                    })
                    st.success(f"¡Se han asignado {puntos_ganados} puntos a tu cuenta!")
                else:
                    st.error("Código de usuario no encontrado")
            else:
                st.error("Por favor completa todos los campos")

def mostrar_premios():
    st.markdown("### 🎁 Canjea tus puntos por premios")
    
    premios = [
        {"nombre": "Café Gratis", "puntos": 50, "descripcion": "Un café de la casa gratis"},
        {"nombre": "Postre Especial", "puntos": 100, "descripcion": "Postre del día gratis"},
        {"nombre": "Combo Desayuno", "puntos": 150, "descripcion": "Café + pastel gratis"},
        {"nombre": "Box de Pasteles", "puntos": 300, "descripcion": "Selección de 4 pasteles"},
    ]
    
    cols = st.columns(2)
    for idx, premio in enumerate(premios):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f'<div class="product-card">', unsafe_allow_html=True)
                st.write(f"**{premio['nombre']}**")
                st.write(premio['descripcion'])
                st.markdown(f'<p class="price-tag">{premio["puntos"]} puntos</p>', unsafe_allow_html=True)
                
                codigo_usuario = st.text_input("Tu código de usuario", key=f"canje_{premio['nombre']}")
                if st.button(f"Canjear Premio", key=f"btn_{premio['nombre']}"):
                    if codigo_usuario:
                        canjear_premio(codigo_usuario, premio)
                    else:
                        st.error("Ingresa tu código de usuario")
                
                st.markdown('</div>', unsafe_allow_html=True)

def canjear_premio(codigo_usuario, premio):
    if codigo_usuario in st.session_state.usuarios:
        usuario = st.session_state.usuarios[codigo_usuario]
        if usuario['puntos'] >= premio['puntos']:
            usuario['puntos'] -= premio['puntos']
            st.success(f"¡Premio canjeado! Disfruta de tu {premio['nombre'].lower()}")
            st.info("Presenta este mensaje en nuestra cafetería para reclamar tu premio")
        else:
            st.error(f"No tienes suficientes puntos. Necesitas {premio['puntos']} puntos")
    else:
        st.error("Código de usuario no encontrado")

def calcular_puntos_compra(monto):
    """Calcula puntos ganados: 10 puntos por cada 1000 Bs"""
    return int((monto // 1000) * 10)

def generar_codigo_usuario(nombre):
    """Genera un código único para el usuario"""
    import hashlib
    timestamp = str(datetime.now().timestamp())
    base_string = nombre + timestamp
    return hashlib.md5(base_string.encode()).hexdigest()[:8].upper()

def generar_ticket_compra(nombre, total, codigo_usuario=None, puntos_ganados=0):
    """Genera un ticket de compra en texto"""
    ticket = f"""
    {'='*40}
    CAFÉ & PASTELERÍA DELICIA
    {'='*40}
    Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    Cliente: {nombre}
    {'='*40}
    """
    
    for item in st.session_state.carrito:
        ticket += f"{item['nombre']:20} {item['precio']:6.2f} Bs\n"
    
    ticket += f"""
    {'='*40}
    TOTAL: {total:.2f} Bs
    {'='*40}
    """
    
    if codigo_usuario:
        ticket += f"Código Usuario: {codigo_usuario}\n"
        ticket += f"Puntos Ganados: {puntos_ganados}\n"
    else:
        ticket += "¿No tienes nuestro programa de fidelidad?\n"
        ticket += "¡Regístrate y gana puntos!\n"
    
    ticket += f"""
    {'='*40}
    ¡Gracias por tu compra!
    """
    
    return ticket

def agregar_al_carrito(producto):
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []
    st.session_state.carrito.append(producto)

def mostrar_contacto():
    st.markdown("## 📞 Contacto")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Información de Contacto:**
        📍 Dirección: [Tu dirección aquí]
        📞 Teléfono: [Tu teléfono]
        📧 Email: [tu-email@cafeteria.com]
        """)
    with col2:
        st.markdown("### Envíanos un mensaje")
        nombre = st.text_input("Tu nombre", key="contact_nombre")
        email = st.text_input("Tu email", key="contact_email")
        mensaje = st.text_area("Mensaje", key="contact_mensaje")
        if st.button("Enviar Mensaje"):
            if nombre and email and mensaje:
                st.success("¡Mensaje enviado! Te responderemos pronto.")

def mostrar_sobre_nosotros():
    st.markdown("## ℹ️ Sobre Nosotros")
    st.write("""
    ### Nuestra Historia
    Café & Pastelería Delicia nació en 2020 con la pasión de servir 
    los mejores cafés y pasteles artesanales.
    
    ### Programa de Fidelidad
    Valoramos a nuestros clientes frecuentes. Por eso creamos este 
    programa donde cada compra te acerca a premios especiales.
    """)

if __name__ == "__main__":
    main()

