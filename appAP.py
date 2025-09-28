# ==================================================
# CONFIGURACIÓN DE IMÁGENES - MODIFICA ESTAS RUTAS
# ==================================================
CONFIG_IMAGENES = {
    "logo": "logo.jpg",  # Ruta a tu logo
    "imagen_principal": "cafe_principal.jpg",  # Ruta a tu imagen principal
    "productos": {
        "macarons": "macarons.jpg",
        "eclair": "eclair.jpg", 
        "croissant": "croissant.jpg"
    }
}

# ==================================================
# FUNCIÓN PARA CARGAR IMÁGENES LOCALES
# ==================================================
def cargar_imagen(ruta_imagen, texto_alternativo=""):
    """
    Carga una imagen local y maneja errores gracefulmente
    """
    try:
        from PIL import Image
        imagen = Image.open(ruta_imagen)
        return imagen
    except Exception as e:
        st.warning(f"No se pudo cargar {ruta_imagen}: {e}")
        # Usar imagen por defecto de internet si la local falla
        return texto_alternativo

# ==================================================
# VERSIÓN MEJORADA DEL CÓDIGO CON TUS IMÁGENES
# ==================================================
import streamlit as st
import requests
import json
import time
from datetime import datetime, date
from streamlit_option_menu import option_menu
from PIL import Image
import os

# Configuración de página
st.set_page_config(
    page_title="Ait Paris Delicafé",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS (mantener el mismo)
st.markdown("""
<style>
    .main > div { padding: 0.5rem; }
    .hero-section {
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .logo-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem auto;
        max-width: 200px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 25px;
        font-weight: bold;
        margin: 0.25rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================================================
# CONFIGURACIÓN DE TUS IMÁGENES
# ==================================================
# MODIFICA ESTAS RUTAS CON TUS ARCHIVOS
TUS_IMAGENES = {
    "logo": "logo_nuevo.jpg",  # Coloca tu archivo logo_nuevo.jpg en la misma carpeta
    "hero": "cafe_arte.jpg",   # Imagen principal de café con arte
    "productos": [
        "https://images.unsplash.com/photo-1558326560-355b61cf86f7?w=300",  # Macarons
        "https://images.unsplash.com/photo-1571115764595-644a1f56a55c?w=300",  # Eclair
        "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=300",  # Croissant
    ]
}

# ==================================================
# FUNCIÓN PARA MOSTRAR TU LOGO
# ==================================================
def mostrar_logo():
    """
    Muestra tu logo personalizado
    """
    try:
        # Intenta cargar tu logo local
        logo = Image.open(TUS_IMAGENES["logo"])
        st.image(logo, use_column_width=True)
    except:
        # Si falla, muestra el logo en texto
        st.markdown("""
        <div class="logo-container">
            <h2 style="color: #8B4513; margin: 0; font-family: 'Brush Script MT', cursive;">Ait Paris</h2>
            <h3 style="color: #D2691E; margin: 0; font-size: 1.2rem;">DELICAFÉ</h3>
        </div>
        """, unsafe_allow_html=True)

# ==================================================
# FUNCIÓN PARA MOSTRAR IMAGEN PRINCIPAL
# ==================================================
def mostrar_imagen_principal():
    """
    Muestra tu imagen principal de café
    """
    try:
        hero_image = Image.open(TUS_IMAGENES["hero"])
        st.image(hero_image, caption="🎨 Donde el café se encuentra con el arte", use_column_width=True)
    except:
        # Si falla, usa imagen de internet
        st.image("https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400", 
                caption="🎨 Cada taza es una experiencia artística")

# ==================================================
# PRODUCTOS CON TUS IMÁGENES
# ==================================================
PRODUCTOS = [
    {
        "nombre": "Caja de Macarons Surpresa",
        "puntos": 50,
        "precio_original": 25.00,
        "imagen": TUS_IMAGENES["productos"][0],  # Tu imagen de macarons
        "categoria": "clasico"
    },
    {
        "nombre": "Éclair de Temporada", 
        "puntos": 30,
        "precio_original": 12.00,
        "imagen": TUS_IMAGENES["productos"][1],  # Tu imagen de eclair
        "categoria": "clasico"
    },
    {
        "nombre": "Croissant Artístico",
        "puntos": 25, 
        "precio_original": 8.00,
        "imagen": TUS_IMAGENES["productos"][2],  # Tu imagen de croissant
        "categoria": "panaderia"
    }
]

# ==================================================
# RESTA DEL CÓDIGO (MANTENER LAS FUNCIONES DE FIREBASE)
# ==================================================
FIREBASE_CONFIG = {
    "API_KEY": "AIzaSyAr3RChPqT89oy_dBakL7PO_qU03TTLE0k",
    "PROJECT_ID": "webap-6e49a"
}

# [MANTENER TODAS LAS FUNCIONES DE FIREBASE IGUAL...]
# login_user, signup_user, save_profile_via_rest, etc.

# ==================================================
# INTERFAZ MODIFICADA CON TUS IMÁGENES
# ==================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "profile" not in st.session_state:
    st.session_state.profile = None

if st.session_state.user:
    # Usuario logueado - INTERFAZ PRINCIPAL
    user_info = st.session_state.user
    uid = user_info["localId"]
    
    if st.session_state.profile is None:
        with st.spinner("Cargando tu perfil..."):
            # [CÓDIGO PARA CARGAR PERFIL...]
            pass
    
    # NAVEGACIÓN
    with st.container():
        selected = option_menu(
            menu_title=None,
            options=["Inicio", "Productos", "Perfil"],
            icons=["house", "gift", "person"],
            menu_icon="cast", 
            default_index=0,
            orientation="horizontal"
        )
    
    if selected == "Inicio":
        # HERO SECTION CON TU LOGO
        st.markdown("""
        <div class="hero-section">
            <h3 style="margin: 1rem 0 0 0; font-style: italic;">Donde el café se encuentra con el arte</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # MOSTRAR TU LOGO
        mostrar_logo()
        
        # [RESTA DEL CÓDIGO DE INICIO...]
        
    elif selected == "Productos":
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <h2 style="color: #8B4513; margin: 0;">🎁 Nuestros Productos</h2>
            <p style="color: #666;">Disfruta de nuestras delicias</p>
        </div>
        """, unsafe_allow_html=True)
        
        # PRODUCTOS CON TUS IMÁGENES
        for producto in PRODUCTOS:
            with st.container():
                st.markdown(f"""
                <div class="mobile-card">
                    <img src="{producto['imagen']}" width="100%" style="border-radius: 10px;">
                    <h4>{producto['nombre']}</h4>
                    <p>⭐ {producto['puntos']} puntos</p>
                </div>
                """, unsafe_allow_html=True)

else:
    # PANTALLA DE LOGIN MEJORADA
    st.markdown("""
    <div class="hero-section">
        <h3 style="margin: 1rem 0 0 0; font-style: italic;">Bienvenido a Ait Paris Delicafé</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # MOSTRAR TU LOGO
    mostrar_logo()
    
    # MOSTRAR TU IMAGEN PRINCIPAL
    mostrar_imagen_principal()
    
    # [RESTA DEL CÓDIGO DE LOGIN...]

# FOOTER
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem;">'
    '☕ <strong>Ait Paris Delicafé</strong> - Donde cada taza cuenta una historia 🎨'
    '</div>',
    unsafe_allow_html=True
)
