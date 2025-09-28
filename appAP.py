import streamlit as st

st.set_page_config(page_title="Arte París", layout="wide")

# ==== CSS estilo Starbucks ====
st.markdown("""
<style>
body {
    font-family: 'Poppins', sans-serif;
    background-color: #ffffff;
    color: #333;
    margin: 0;
    padding: 0;
}
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: white;
    border-bottom: 1px solid #eee;
    padding: 1rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 999;
}
.navbar a {
    color: #333;
    margin-left: 30px;
    text-decoration: none;
    font-weight: 600;
}
.navbar a:hover {
    color: #8B4513;
}
.hero {
    height: 90vh;
    background-image: url("https://images.unsplash.com/photo-1509042239860-f550ce710b93");
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    color: white;
    text-shadow: 0px 2px 6px rgba(0,0,0,0.5);
}
.hero h1 {
    font-size: 3.5rem;
}
.hero a {
    margin-top: 20px;
    background: #8B4513;
    color: white;
    padding: 14px 30px;
    border-radius: 30px;
    text-decoration: none;
    font-weight: bold;
}
.section {
    padding: 6rem 4rem;
    text-align: center;
}
.section img {
    width: 100%;
    border-radius: 16px;
    margin-top: 20px;
}
.footer {
    text-align: center;
    padding: 3rem;
    background: #f8f8f8;
    color: #555;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# ==== Navbar ====
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

# ==== Hero ====
st.markdown("""
<div class="hero">
    <h1>Arte París Café & Pastelería</h1>
    <p>Dulces momentos para compartir</p>
    <a href="#productos">Explora nuestro menú</a>
</div>
""", unsafe_allow_html=True)

# ==== Productos ====
st.markdown('<div id="productos" class="section">', unsafe_allow_html=True)
st.markdown("## 🥐 Nuestros Productos")
col1, col2 = st.columns(2)

with col1:
    st.image("https://images.unsplash.com/photo-1509440159596-0249088772ff")
    st.subheader("Bollería")
    st.write("Recién horneada cada mañana, con mantequilla de verdad.")
    st.button("Ver más", key="bolleria")

with col2:
    st.image("https://images.unsplash.com/photo-1604152135912-04a022e23696")
    st.subheader("Dulces Secos")
    st.write("Perfectos para acompañar tu café en cualquier momento.")
    st.button("Ver más", key="dulces")
    
col3, col4 = st.columns(2)

with col3:
    st.image("https://images.unsplash.com/photo-1548943487-a2e4e43b4853")
    st.subheader("Pastelería Fría")
    st.write("Postres frescos y cremosos para cada ocasión.")
    st.button("Ver más", key="fria")

with col4:
    st.image("https://images.unsplash.com/photo-1604908554049-889c2b6f5c3f")
    st.subheader("Restaurant")
    st.write("Platos ligeros para complementar tu experiencia dulce.")
    st.button("Ver más", key="restaurant")

st.markdown("</div>", unsafe_allow_html=True)

# ==== Club ====
st.markdown('<div id="club" class="section" style="background:#fdf6f0;">', unsafe_allow_html=True)
st.markdown("## 🎉 ArteParísClub")
st.write("Únete a nuestro club, acumula puntos y gana recompensas exclusivas.")
st.button("👉 Únete ahora", key="club")
st.markdown("</div>", unsafe_allow_html=True)

# ==== Delivery ====
st.markdown('<div id="delivery" class="section">', unsafe_allow_html=True)
st.markdown("## 🚚 Delivery")
st.image("https://images.unsplash.com/photo-1600891964599-f61ba0e24092")
st.write("""
Pide desde la comodidad de tu casa:  
1. Haz tu pedido online o por WhatsApp.  
2. Elige recogida o envío.  
3. Pago online o contra entrega.  
4. Entrega en 30-45 min.
""")
st.button("📦 Pide ahora", key="delivery")
st.markdown("</div>", unsafe_allow_html=True)

# ==== Nosotros ====
st.markdown('<div id="nosotros" class="section" style="background:#f8f8f8;">', unsafe_allow_html=True)
st.markdown("## 👩‍🍳 Sobre Nosotros")
st.image("https://images.unsplash.com/photo-1527169402691-a3fb2e5259fe")
st.write("**Visión:** Ser la pastelería de referencia en la ciudad...")  
st.write("**Misión:** Ofrecer experiencias dulces únicas...")
st.write("📍 Dirección: Calle Principal 123, Ciudad")  
st.write("📧 contacto@arteparis.com | ☎️ 123-456-789")
st.markdown("</div>", unsafe_allow_html=True)

# ==== Footer ====
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


