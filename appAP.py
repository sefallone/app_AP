import streamlit as st

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Arte París Café - Pastelería", page_icon="🍰", layout="wide")

# --- ESTILOS CSS ---
st.markdown(
    """
    <style>
        body {
            background-color: white;
        }
        .menu {
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 1rem;
            background-color: #fff;
            border-bottom: 2px solid #f0f0f0;
            font-family: 'Arial', sans-serif;
        }
        .menu a {
            text-decoration: none;
            color: #333;
            font-weight: bold;
            font-size: 18px;
        }
        .menu a:hover {
            color: #b5651d; /* color café */
        }
        .title {
            text-align: center;
            padding: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- MENÚ SUPERIOR ---
st.markdown(
    """
    <div class="menu">
        <a href="?page=productos">Productos</a>
        <a href="?page=club">ArteParísClub</a>
        <a href="?page=delivery">Delivery</a>
        <a href="?page=nosotros">Nosotros</a>
    </div>
    """,
    unsafe_allow_html=True
)

# --- LÓGICA DE NAVEGACIÓN ---
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["productos"])[0]

# --- CONTENIDO ---
if page == "productos":
    st.markdown("<h1 class='title'>🍰 Menú de Productos</h1>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.image("https://images.unsplash.com/photo-1509440159598-05d26c92d3a1", use_container_width=True)
        st.subheader("🥐 Bollería")
        st.write("Croissant, Napolitana, Pan de queso...")

    with col2:
        st.image("https://images.unsplash.com/photo-1606788075761-7a07aab8f207", use_container_width=True)
        st.subheader("🍪 Dulces Secos")
        st.write("Galletas, Alfajores, Brownies...")

    with col3:
        st.image("https://images.unsplash.com/photo-1622495896520-3f5f6ad39e1d", use_container_width=True)
        st.subheader("🎂 Pastelería Fría")
        st.write("Cheesecake, Tiramisú, Tartaletas...")

    with col4:
        st.image("https://images.unsplash.com/photo-1529042410759-befb1204b468", use_container_width=True)
        st.subheader("🍴 Restaurant")
        st.write("Sandwiches, Almuerzos, Ensaladas...")

elif page == "club":
    st.markdown("<h1 class='title'>🎉 ArteParísClub</h1>", unsafe_allow_html=True)
    opcion = st.radio("Selecciona una opción:", ["Registrarse", "Iniciar Sesión"], horizontal=True)

    if opcion == "Registrarse":
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        if st.button("Registrarme"):
            st.success(f"Usuario {nombre} registrado con éxito 🎉")

    elif opcion == "Iniciar Sesión":
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            st.success("Inicio de sesión exitoso ✅")

elif page == "delivery":
    st.markdown("<h1 class='title'>🚚 Delivery</h1>", unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1617196037302-9b845a1efb1b", use_container_width=True)
    st.write("""
    📦 **Cómo funciona nuestro delivery:**
    1. Haz tu pedido online o por WhatsApp.
    2. Escoge recogida en tienda o envío a domicilio.
    3. Paga con tarjeta o contra entrega.
    4. Tiempo estimado: 30-45 minutos.
    """)

elif page == "nosotros":
    st.markdown("<h1 class='title'>👩‍🍳 Nosotros</h1>", unsafe_allow_html=True)
    opcion = st.radio("Explora:", ["Visión", "Misión", "Contacto", "Trabaja con nosotros"], horizontal=True)

    if opcion == "Visión":
        st.subheader("🌟 Nuestra Visión")
        st.write("Ser la pastelería de referencia en la ciudad...")

    elif opcion == "Misión":
        st.subheader("🎯 Nuestra Misión")
        st.write("Ofrecer experiencias dulces únicas...")

    elif opcion == "Contacto":
        st.subheader("📞 Contáctanos")
        st.write("📍 Dirección: Calle Ejemplo 123, Ciudad")
        st.write("📧 Email: info@arteparis.com")
        st.write("📱 Teléfono: +34 600 123 456")

    elif opcion == "Trabaja con nosotros":
        st.subheader("💼 Forma parte de nuestro equipo")
        nombre = st.text_input("Nombre")
        email = st.text_input("Correo electrónico")
        cv = st.file_uploader("Adjunta tu CV", type=["pdf", "docx"])
        if st.button("Enviar solicitud"):
            st.success("Tu solicitud ha sido enviada. ¡Gracias por postularte!")


