import streamlit as st

# Configuración general
st.set_page_config(page_title="Arte París", layout="wide")

# CSS personalizado
st.markdown("""
<style>
/* Fondo */
body {
    background-color: #ffffff;
    color: #222222;
    font-family: 'Poppins', sans-serif;
}

/* Navbar */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #4b2e2e;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 999;
}
.navbar a {
    color: white;
    margin-left: 20px;
    text-decoration: none;
    font-weight: bold;
}
.navbar a:hover {
    color: #e6d3b3;
}
.hero {
    text-align: center;
    padding: 8rem 2rem;
    background-image: url("https://images.unsplash.com/photo-1515442261605-65987783cb6a");
    background-size: cover;
    background-position: center;
    color: white;
}
.section {
    padding: 6rem 2rem;
}
.section h2 {
    color: #4b2e2e;
    margin-bottom: 2rem;
}
.card-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
}
.card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 1rem;
    text-align: center;
}
.footer {
    text-align: center;
    padding: 2rem;
    background: #f8f8f8;
    color: #555;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# Navbar HTML
st.markdown("""
<div class="navbar">
    <div><b>Arte París</b></div>
    <div>
        <a href="#productos">Productos</a>
        <a href="#club">Club</a>
        <a href="#delivery">Delivery</a>
        <a href="#nosotros">Nosotros</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero">
    <h1>Arte París — Café & Pastelería</h1>
    <p>Dulces momentos para compartir</p>
    <a href="#productos" style="background:#e6d3b3; padding:12px 24px; border-radius:8px; color:#4b2e2e; text-decoration:none;">Explora nuestro menú</a>
</div>
""", unsafe_allow_html=True)

# Productos
st.markdown('<div id="productos" class="section">', unsafe_allow_html=True)
st.markdown("## 🥐 Nuestros Productos")
st.markdown("""
<div class="card-grid">
    <div class="card">
        <h4>Bollería</h4>
        <img src="https://images.unsplash.com/photo-1509440159596-0249088772ff" width="100%"/>
    </div>
    <div class="card">
        <h4>Dulces Secos</h4>
        <img src="https://images.unsplash.com/photo-1604152135912-04a022e23696" width="100%"/>
    </div>
    <div class="card">
        <h4>Pastelería Fría</h4>
        <img src="https://images.unsplash.com/photo-1548943487-a2e4e43b4853" width="100%"/>
    </div>
    <div class="card">
        <h4>Restaurant</h4>
        <img src="https://images.unsplash.com/photo-1604908554049-889c2b6f5c3f" width="100%"/>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Club
st.markdown('<div id="club" class="section" style="background:#fef8f2;">', unsafe_allow_html=True)
st.markdown("## 🎉 ArteParísClub")
st.write("Únete a nuestro club, acumula puntos y gana recompensas.")
if st.button("👉 Registrarse"):
    st.info("Aquí conectamos con registro/login.")
if st.button("🔑 Iniciar Sesión"):
    st.info("Aquí va el login del club.")
st.markdown("</div>", unsafe_allow_html=True)

# Delivery
st.markdown('<div id="delivery" class="section">', unsafe_allow_html=True)
st.markdown("## 🚚 Delivery")
st.write("""
1. Haz tu pedido online o por WhatsApp.  
2. Escoge recogida o envío.  
3. Pago online o contra entrega.  
4. Entrega en 30-45 min.
""")
st.button("📦 Pide Ahora")
st.markdown("</div>", unsafe_allow_html=True)

# Nosotros
st.markdown('<div id="nosotros" class="section" style="background:#f8f8f8;">', unsafe_allow_html=True)
st.markdown("## 👩‍🍳 Sobre Nosotros")
st.write("**Visión:** Ser la pastelería de referencia en la ciudad...")  
st.write("**Misión:** Ofrecer experiencias dulces únicas...")
st.write("📍 Dirección: Calle Principal 123, Ciudad")  
st.write("📧 contacto@arteparis.com | ☎️ 123-456-789")
st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Arte París © 2025 — Todos los derechos reservados</p>
    <p>
        <a href="https://instagram.com" target="_blank">Instagram</a> |
        <a href="https://facebook.com" target="_blank">Facebook</a> |
        <a href="https://tiktok.com" target="_blank">TikTok</a>
    </p>
</div>
""", unsafe_allow_html=True)



