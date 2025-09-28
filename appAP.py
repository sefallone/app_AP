import streamlit as st

# Configuración inicial
st.set_page_config(
    page_title="Arte París Café-Pastelería",
    page_icon="🍰",
    layout="wide"
)

# Menú principal
menu = st.sidebar.radio(
    "Navegación",
    ["Productos", "ArteParísClub", "Delivery", "Nosotros"]
)

# --- SECCIÓN PRODUCTOS ---
if menu == "Productos":
    st.title("🍰 Menú de Productos")
    categoria = st.selectbox(
        "Selecciona una categoría:",
        ["Bollería", "Dulces Secos", "Pastelería Fría", "Restaurant"]
    )

    if categoria == "Bollería":
        st.subheader("🥐 Bollería")
        st.write("Croissant, Napolitana de chocolate, Pan de queso...")
    
    elif categoria == "Dulces Secos":
        st.subheader("🍪 Dulces Secos")
        st.write("Galletas, Alfajores, Brownies...")

    elif categoria == "Pastelería Fría":
        st.subheader("🎂 Pastelería Fría")
        st.write("Cheesecake, Tiramisú, Tartaletas...")

    elif categoria == "Restaurant":
        st.subheader("🍴 Restaurant")
        st.write("Sandwiches, Almuerzos ejecutivos, Ensaladas...")

# --- SECCIÓN CLUB ---
elif menu == "ArteParísClub":
    st.title("🎉 ArteParísClub")
    opcion = st.radio("Selecciona una opción:", ["Registrarse", "Iniciar Sesión"])

    if opcion == "Registrarse":
        st.subheader("Formulario de Registro")
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        if st.button("Registrarme"):
            st.success(f"Usuario {nombre} registrado con éxito. ¡Bienvenido a ArteParísClub!")

    elif opcion == "Iniciar Sesión":
        st.subheader("Inicia sesión en tu cuenta")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            st.success("Inicio de sesión exitoso. ¡Ya puedes acumular puntos!")

# --- SECCIÓN DELIVERY ---
elif menu == "Delivery":
    st.title("🚚 Delivery Arte París")
    st.write("""
    📦 **Cómo funciona nuestro delivery:**
    1. Realiza tu pedido a través de la web o WhatsApp.
    2. Elige si deseas recoger en tienda o recibir en tu domicilio.
    3. Pago seguro por tarjeta o contra entrega.
    4. Tiempo estimado de entrega: 30 - 45 minutos.
    """)

# --- SECCIÓN NOSOTROS ---
elif menu == "Nosotros":
    st.title("👩‍🍳 Nosotros - Arte París")
    opcion = st.radio("Explora:", ["Visión", "Misión", "Contacto", "Trabaja con nosotros"])

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

