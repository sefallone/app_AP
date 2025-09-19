import streamlit as st
import sqlite3
import hashlib
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time
from datetime import datetime
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Arte París Deli Café",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');
    
    .main {
        background-color: #383125;
    }
    
    .stApp {
        background: linear-gradient(to bottom, #f8f5f0 0%, #e8e1d4 100%);
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: #4a2c2a;
    }
    
    p, div, input, button {
        font-family: 'Montserrat', sans-serif;
    }
    
    .arte-paris-header {
        text-align: center;
        padding: 1rem;
        background-color: #4a2c2a;
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .welcome-box {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .product-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s;
        height: 100%;
    }
    
    .product-card:hover {
        transform: translateY(-5px);
    }
    
    .promo-banner {
        background: linear-gradient(to right, #4a2c2a, #7b5a57);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .points-display {
        background: linear-gradient(to right, #d4af37, #f5d76e);
        color: #4a2c2a;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    
    .stButton>button {
        background-color: #4a2c2a;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #7b5a57;
        color: white;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Base de datos
def init_db():
    conn = sqlite3.connect('arte_paris.db')
    c = conn.cursor()
    
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password TEXT,
            verification_code TEXT,
            verified INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            registration_date TEXT,
            name TEXT
        )
    ''')
    
    # Tabla de productos
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL,
            category TEXT,
            image_url TEXT
        )
    ''')
    
    # Insertar productos de ejemplo si no existen
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = [
            ("Cappuccino Clásico", "Nuestro cappuccino signature con granos arábica y un toque de canela", 3.50, "Bebidas", "https://images.unsplash.com/photo-1572442388796-11668a67e53d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80"),
            ("Croissant de Almendra", "Crujiente croissant relleno de crema de almendra casera", 2.80, "Repostería", "https://images.unsplash.com/photo-1555507036-ab794f24d8c7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80"),
            ("Sandwich Club", "Pechuga de pollo, tocino, lechuga, tomate y mayonesa casera", 7.90, "Comida", "https://images.unsplash.com/photo-1606755962773-d324e0a13086?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80"),
            ("Té Verde Matcha", "Té matcha ceremonial batido a la perfección", 4.20, "Bebidas", "https://images.unsplash.com/photo-1559170904-2e9ffd7bf54c?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80"),
            ("Tarta de Queso", "Nuestra famosa tarta de queso con base de galleta y coulis de frutos rojos", 4.50, "Repostería", "https://images.unsplash.com/photo-1567327613488-4e3ed8ed87c9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80"),
            ("Ensalada César", "Clásica ensalada César con pollo a la parrilla y croûtons caseros", 8.50, "Comida", "https://images.unsplash.com/photo-1546793665-c74683f339c1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80")
        ]
        c.executemany("INSERT INTO products (name, description, price, category, image_url) VALUES (?, ?, ?, ?, ?)", products)
    
    conn.commit()
    conn.close()

# Función para enviar correos (configuración simplificada)
def send_verification_email(email, verification_code):
    # En una implementación real, configurarías aquí tu servidor SMTP
    # Esta es una versión simplificada para demostración
    st.info(f"En un entorno real, se enviaría un correo a {email} con el código de verificación: {verification_code}")
    return True

# Función para validar email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Función para validar teléfono (formato simple)
def is_valid_phone(phone):
    pattern = r'^\+?[0-9]{8,15}$'
    return re.match(pattern, phone) is not None

# Función para generar código de verificación
def generate_verification_code():
    return str(random.randint(100000, 999999))

# Función para hashear contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Página de registro
def show_registration_page():
    st.markdown("<div class='arte-paris-header'><h1>Arte París Deli Café</h1></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='welcome-box'><h2>¡Únete a Nuestra Comunidad!</h2>", unsafe_allow_html=True)
        st.markdown("""
        <p>Disfruta de beneficios exclusivos, premios y sorpresas. ¡Fácil, rápido y pensado para ti!</p>
        <ul>
            <li>Acumula puntos por cada compra</li>
            <li>Premios y descuentos por tu fidelidad</li>
            <li>Tu tarjeta digital siempre en tu móvil</li>
        </ul>
        """, unsafe_allow_html=True)
        
        with st.form("registration_form"):
            st.subheader("Crear una cuenta")
            name = st.text_input("Nombre completo")
            email = st.text_input("Correo electrónico")
            phone = st.text_input("Número de teléfono (opcional)")
            password = st.text_input("Contraseña", type="password")
            submit_button = st.form_submit_button("Registrarse")
            
            if submit_button:
                if not name:
                    st.error("Por favor ingresa tu nombre")
                elif not email or not is_valid_email(email):
                    st.error("Por favor ingresa un correo electrónico válido")
                elif not password or len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                else:
                    conn = sqlite3.connect('arte_paris.db')
                    c = conn.cursor()
                    
                    # Verificar si el email ya existe
                    c.execute("SELECT * FROM users WHERE email = ?", (email,))
                    if c.fetchone():
                        st.error("Este correo electrónico ya está registrado")
                    else:
                        # Generar código de verificación
                        verification_code = generate_verification_code()
                        hashed_password = hash_password(password)
                        
                        # Insertar usuario en la base de datos
                        try:
                            c.execute(
                                "INSERT INTO users (name, email, phone, password, verification_code, registration_date) VALUES (?, ?, ?, ?, ?, ?)",
                                (name, email, phone, hashed_password, verification_code, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            )
                            conn.commit()
                            
                            # Enviar correo de verificación
                            if send_verification_email(email, verification_code):
                                st.session_state['verification_email'] = email
                                st.session_state['page'] = 'verify'
                                st.rerun()
                            else:
                                st.error("Error al enviar el correo de verificación. Por favor intenta nuevamente.")
                        except Exception as e:
                            st.error(f"Error al registrar usuario: {str(e)}")
                    
                    conn.close()
    
    with col2:
        st.image("https://images.unsplash.com/photo-1554118811-1e0d58224f24?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80", use_column_width=True)
        st.markdown("""
        <div style='text-align: center; margin-top: 1rem;'>
            <p>¡Escanea el código QR de nuestro flyer y sé parte de la familia Arte París!</p>
        </div>
        """, unsafe_allow_html=True)

# Página de verificación
def show_verification_page():
    st.markdown("<div class='arte-paris-header'><h1>Verifica tu correo electrónico</h1></div>", unsafe_allow_html=True)
    
    email = st.session_state.get('verification_email', '')
    
    if not email:
        st.error("No se encontró dirección de correo para verificar")
        st.session_state['page'] = 'register'
        st.rerun()
        return
    
    st.write(f"Hemos enviado un código de verificación a {email}")
    
    verification_code = st.text_input("Ingresa el código de verificación", max_chars=6)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Verificar"):
            if verification_code:
                conn = sqlite3.connect('arte_paris.db')
                c = conn.cursor()
                
                c.execute("SELECT verification_code FROM users WHERE email = ?", (email,))
                result = c.fetchone()
                
                if result and result[0] == verification_code:
                    # Código correcto, marcar como verificado
                    c.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
                    conn.commit()
                    conn.close()
                    
                    st.success("¡Cuenta verificada correctamente! Ahora puedes iniciar sesión.")
                    time.sleep(2)
                    st.session_state['page'] = 'login'
                    st.rerun()
                else:
                    st.error("Código de verificación incorrecto")
            else:
                st.error("Por favor ingresa el código de verificación")
    
    with col2:
        if st.button("Reenviar código"):
            new_code = generate_verification_code()
            conn = sqlite3.connect('arte_paris.db')
            c = conn.cursor()
            c.execute("UPDATE users SET verification_code = ? WHERE email = ?", (new_code, email))
            conn.commit()
            conn.close()
            
            send_verification_email(email, new_code)
            st.success("Nuevo código enviado")

# Página de login
def show_login_page():
    st.markdown("<div class='arte-paris-header'><h1>Inicia Sesión en tu Cuenta</h1></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("login_form"):
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            login_button = st.form_submit_button("Iniciar Sesión")
            
            if login_button:
                if not email or not password:
                    st.error("Por favor ingresa ambos campos")
                else:
                    conn = sqlite3.connect('arte_paris.db')
                    c = conn.cursor()
                    
                    hashed_password = hash_password(password)
                    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
                    user = c.fetchone()
                    
                    if user:
                        if user[5]:  # Verificado
                            st.session_state['user_id'] = user[0]
                            st.session_state['user_name'] = user[8]
                            st.session_state['user_email'] = user[1]
                            st.session_state['user_points'] = user[6]
                            st.session_state['page'] = 'dashboard'
                            st.rerun()
                        else:
                            st.error("Por favor verifica tu correo electrónico antes de iniciar sesión")
                    else:
                        st.error("Correo electrónico o contraseña incorrectos")
                    
                    conn.close()
    
    with col2:
        st.image("https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=500&q=80", use_column_width=True)
        st.markdown("""
        <div style='text-align: center; margin-top: 1rem;'>
            <p>¿No tienes una cuenta? <a href='#' onclick='window.location.reload();'>Regístrate aquí</a></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Volver al registro"):
            st.session_state['page'] = 'register'
            st.rerun()

# Panel principal después del login
def show_dashboard():
    st.markdown(f"<div class='arte-paris-header'><h1>Bienvenido/a, {st.session_state['user_name']}</h1></div>", unsafe_allow_html=True)
    
    # Barra superior con puntos y logout
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col2:
        st.markdown(f"<div class='points-display'>{st.session_state['user_points']} Puntos</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Cerrar Sesión"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['page'] = 'register'
            st.rerun()
    
    # Promociones destacadas
    st.markdown("## 🎉 Promociones Especiales")
    promo_col1, promo_col2 = st.columns(2)
    
    with promo_col1:
        st.markdown("""
        <div class='promo-banner'>
            <h3>¡Martes de Café!</h3>
            <p>Todos los martes obtén 2x1 en cualquier café especial</p>
            <p><small>Válido hasta el 31 de diciembre</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    with promo_col2:
        st.markdown("""
        <div class='promo-banner'>
            <h3>Descuento de Cumpleaños</h3>
            <p>Preséntanos tu ID en tu cumpleaños y obtén un 20% de descuento</p>
            <p><small>Válido por 7 días después de tu cumpleaños</small></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Productos
    st.markdown("## ☕ Nuestros Productos")
    
    conn = sqlite3.connect('arte_paris.db')
    products = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    # Filtrar por categoría
    categories = ["Todos"] + list(products['category'].unique())
    selected_category = st.selectbox("Filtrar por categoría", categories)
    
    if selected_category != "Todos":
        products = products[products['category'] == selected_category]
    
    # Mostrar productos
    cols = st.columns(3)
    for idx, (_, product) in enumerate(products.iterrows()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class='product-card'>
                <img src='{product['image_url']}' style='width: 100%; height: 200px; object-fit: cover; border-radius: 8px;'>
                <h4>{product['name']}</h4>
                <p>{product['description']}</p>
                <p><strong>${product['price']}</strong></p>
            </div>
            """, unsafe_allow_html=True)
    
    # Sistema de puntos
    st.markdown("## 🏆 Sistema de Puntos")
    
    points_info = st.columns(3)
    
    with points_info[0]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background-color: white; border-radius: 10px;'>
            <h3>1 Punto</h3>
            <p>por cada $1 gastado</p>
        </div>
        """, unsafe_allow_html=True)
    
    with points_info[1]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background-color: white; border-radius: 10px;'>
            <h3>100 Puntos</h3>
            <p>= $5 de descuento</p>
        </div>
        """, unsafe_allow_html=True)
    
    with points_info[2]:
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background-color: white; border-radius: 10px;'>
            <h3>Niveles</h3>
            <p>Oro (1000+ pts), Plata (500+ pts), Bronce (100+ pts)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Información de la tienda
    st.markdown("## 📍 Nuestra Tienda")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        <div style='background-color: white; padding: 1.5rem; border-radius: 10px;'>
            <h4>Horario de Atención</h4>
            <p>Lunes a Viernes: 7:00 am - 9:00 pm</p>
            <p>Sábados y Domingos: 8:00 am - 8:00 pm</p>
            <h4>Dirección</h4>
            <p>Av. Principal #123, Ciudad</p>
            <h4>Teléfono</h4>
            <p>+1 234 567 8900</p>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.map(pd.DataFrame({
            'lat': [19.4326],  # Ejemplo: Ciudad de México
            'lon': [-99.1332]
        }), zoom=12)

# Función principal
def main():
    local_css()
    init_db()
    
    # Inicializar estado de la página si no existe
    if 'page' not in st.session_state:
        st.session_state['page'] = 'register'
    
    # Navegación entre páginas
    if st.session_state['page'] == 'register':
        show_registration_page()
    elif st.session_state['page'] == 'verify':
        show_verification_page()
    elif st.session_state['page'] == 'login':
        show_login_page()
    elif st.session_state['page'] == 'dashboard':
        show_dashboard()

if __name__ == "__main__":
    main()
