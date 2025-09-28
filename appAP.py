import streamlit as st

# Configuración inicial
st.set_page_config(page_title="Arte París", layout="wide")

# Estilo general + navbar
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        font-family: "Helvetica Neue", sans-serif;
    }
    /* Navbar */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background-color: white;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        z-index: 999;
    }
    .navbar button {
        background: none;
        border: none;
        font-weight: 500;
        font-size: 16px;
        color: #333;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .navbar button:hover {
        color: #b8860b;
    }
    .content {
        margin-top: 80px;
        padding: 20px 60px;
    }
    .section img {
        max-width: 80%;
        border-radius: 10px;
        margin: 20px auto;
        display: block;
    }
    .title {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 10px;
        text-align: center;
    }
    .subtitle {
        font-size: 18px;
        font-weight: 400;
        text-align: center;
        margin-bottom: 40px;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

# Crear la barra de navegación con botones
st.markdown('<div class="navbar">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1,1,1,1])

with col1:
    if st.button("Productos"):
        st.session_state.section = "menu"
with col2:
    if st.button("ArteParísClub"):
        st.session_state.section = "club"
with col3:
    if st.button("Delivery"):
        st.session_state.section = "delivery"
with col4:
    if st.button("Nosotros"):
        st.session_state.section = "nosotros"

st.markdown('</div>', unsafe_allow_html=True)

# Estado inicial de la sección
if "section" not in st.session_state:
    st.session_state.section = "menu"

# Contenido dinámico
st.markdown('<div class="content">', unsafe_allow_html=True)

if st.session_state.section == "menu":
    st.markdown('<div class="title">Nuestro Menú</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Bollería • Dulces Secos • Pastelería Fría • Restaurant</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://images.unsplash.com/photo-1509042239860-f550ce710b93", caption="Bollería", use_container_width=True)
    with col2:
        st.image("https://images.unsplash.com/photo-1578985545062-69928b1d9587", caption="Pastelería", use_container_width=True)

elif st.session_state.section == "club":
    st.markdown('<div class="title">ArteParísClub</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Regístrate o inicia sesión para acumular puntos</div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1523906834658-6e24ef2386f9", use_container_width=True)

elif st.session_state.section == "delivery":
    st.markdown('<div class="title">Delivery</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Llevamos tu pedido a la puerta de tu casa</div>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1600891964599-f61ba0e24092", use_container_width=True)

elif st.session_state.section == "nosotros":
    st.markdown('<div class="title">Nosotros</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Conoce nuestra historia y filosofía</div>', unsafe_allow_html=True)
    st.write("### Visión")
    st.write("Ser el lugar preferido para disfrutar café y pastelería artesanal en un ambiente acogedor.")
    st.write("### Misión")
    st.write("Ofrecer productos de alta calidad elaborados con pasión y dedicación.")
    st.write("### Contacto")
    st.write("📍 Dirección: Calle Principal #123, Ciudad")
    st.write("📞 Teléfono: +34 600 000 000")
    st.write("✉️ Email: contacto@arteparis.com")
    st.write("### Trabaja con nosotros")
    st.write("Si quieres unirte a nuestro equipo, envía tu CV a rrhh@arteparis.com")

st.markdown('</div>', unsafe_allow_html=True)
``


