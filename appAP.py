import streamlit as st

# --------------------
# Config
# --------------------
st.set_page_config(page_title="Arte París - Café & Pastelería", page_icon="🍰", layout="wide")

# --------------------
# Estilos (fondo blanco y limpieza)
# --------------------
st.markdown(
    """
    <style>
    /* Fondo general */
    .stApp {
        background: #ffffff;
        color: #222222;
        font-family: "Inter", "Arial", sans-serif;
    }

    /* Encabezado */
    .app-header {
        display:flex;
        align-items:center;
        gap: 16px;
        padding: 12px 8px;
    }
    .app-title {
        margin: 0;
    }

    /* Tarjetas de producto */
    .product-card {
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        background: #ffffff;
    }

    /* Ajustes responsivos */
    @media (max-width: 640px) {
        .app-header { flex-direction: column; gap: 6px; text-align:center; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------
# Header (logo + nombre)
# --------------------
header_col1, header_col2 = st.columns([1, 5])
with header_col1:
    # si tienes logo local, úsalo: st.image("logo.png", width=90)
    st.image("https://images.unsplash.com/photo-1542281286-9e0a16bb7366?q=80&w=400&auto=format&fit=crop&ixlib=rb-4.0.3&s=1a8fa9f4b8c1a3ea4b6df6b3e9a6f0b0",
             width=90)
with header_col2:
    st.markdown("<h1 class='app-title' style='margin:0'>Arte París</h1>"
                "<div style='color:#6b4a2a'>Café • Pastelería</div>",
                unsafe_allow_html=True)

st.markdown("---")

# --------------------
# Navegación principal: TABS (se queda en la misma página)
# --------------------
tabs = st.tabs(["Productos", "ArteParísClub", "Delivery", "Nosotros"])

# ---------- TAB: Productos ----------
with tabs[0]:
    st.markdown("## 🍰 Menú de Productos")
    # categorías
    categorias = ["Bollería", "Dulces Secos", "Pastelería Fría", "Restaurant"]
    imagenes = [
        "https://images.unsplash.com/photo-1509440159598-05d26c92d3a1?q=80&w=700&auto=format&fit=crop&ixlib=rb-4.0.3&s=0be6c8d4e9b7e1e1c6a9a3bebb3a2b2b",
        "https://images.unsplash.com/photo-1606788075761-7a07aab8f207?q=80&w=700&auto=format&fit=crop&ixlib=rb-4.0.3&s=b3c6d3b48b0f7b8b8a8a6a5b6c5d4e3f",
        "https://images.unsplash.com/photo-1622495896520-3f5f6ad39e1d?q=80&w=700&auto=format&fit=crop&ixlib=rb-4.0.3&s=1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f",
        "https://images.unsplash.com/photo-1529042410759-befb1204b468?q=80&w=700&auto=format&fit=crop&ixlib=rb-4.0.3&s=abcdef1234567890abcdef1234567890"
    ]

    cols = st.columns(4, gap="large")
    for i, cat in enumerate(categorias):
        with cols[i]:
            st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
            st.image(imagenes[i], use_container_width=True)
            st.subheader(cat)
            # Ejemplo de items; luego puedes cargar desde DB
            if cat == "Bollería":
                st.write("- Croissant\n- Napolitana de chocolate\n- Pan de queso")
            elif cat == "Dulces Secos":
                st.write("- Galletas\n- Alfajores\n- Brownies")
            elif cat == "Pastelería Fría":
                st.write("- Cheesecake\n- Tiramisú\n- Tartaletas")
            else:
                st.write("- Sandwiches\n- Almuerzos\n- Ensaladas")
            st.markdown("</div>", unsafe_allow_html=True)

# ---------- TAB: ArteParísClub ----------
with tabs[1]:
    st.markdown("## 🎉 ArteParísClub — acumula puntos")
    # Si el usuario ya está en session_state mostramos perfil simple
    if st.session_state.get("user_logged", False):
        st.success(f"Bienvenido/a, {st.session_state.get('user_name')} — Puntos: {st.session_state.get('points', 0)}")
        if st.button("Cerrar sesión", key="logout_button"):
            st.session_state["user_logged"] = False
            st.session_state.pop("user_name", None)
            st.session_state.pop("points", None)
            st.experimental_rerun()

    else:
        modo = st.radio("¿Quieres:", ["Registrarse", "Iniciar sesión"], horizontal=True)
        if modo == "Registrarse":
            with st.form("form_reg", clear_on_submit=True):
                nombre = st.text_input("Nombre completo")
                email = st.text_input("Correo electrónico")
                password = st.text_input("Contraseña", type="password")
                send = st.form_submit_button("Registrarme")
                if send:
                    # Aquí sólo simulamos registro (en prod: guardar en DB y hashear pass)
                    st.session_state["user_logged"] = True
                    st.session_state["user_name"] = nombre or email.split("@")[0]
                    st.session_state["points"] = 0
                    st.success("Registro exitoso 🎉")
        else:  # Iniciar sesión (simulación)
            with st.form("form_login", clear_on_submit=False):
                email = st.text_input("Correo electrónico", key="login_email")
                password = st.text_input("Contraseña", type="password", key="login_pwd")
                submit = st.form_submit_button("Entrar")
                if submit:
                    # Simulación: en producción validar contra DB
                    st.session_state["user_logged"] = True
                    st.session_state["user_name"] = email.split("@")[0] if email else "Cliente"
                    st.session_state.setdefault("points", 0)
                    st.success("Has iniciado sesión ✅")

    st.markdown("---")
    st.write("Cómo funcionan los puntos (ejemplo):")
    st.write("- 1€ gastado = 1 punto\n- 100 puntos = 5€ de descuento\n- Promos exclusivas para socios")

# ---------- TAB: Delivery ----------
with tabs[2]:
    st.markdown("## 🚚 Delivery")
    st.image("https://images.unsplash.com/photo-1617196037302-9b845a1efb1b?q=80&w=1400&auto=format&fit=crop&ixlib=rb-4.0.3&s=1234567890abcdef", use_container_width=True)
    st.write("""
    **Cómo funciona nuestro delivery**
    1. Haz el pedido por la web o por WhatsApp.
    2. Escoge recogida en tienda o envío a domicilio.
    3. Modalidades de pago: tarjeta en línea / contra entrega.
    4. Tiempo estimado: 30 - 45 minutos (depende de la zona).
    """)
    st.info("Si quieres, puedo agregar un formulario de pedido o integración con un sistema de pedidos.")

# ---------- TAB: Nosotros ----------
with tabs[3]:
    st.markdown("## 👩‍🍳 Nosotros")
    sub = st.radio("", ["Visión", "Misión", "Contacto", "Trabaja con nosotros"], horizontal=True)
    if sub == "Visión":
        st.subheader("🌟 Nuestra Visión")
        st.write("Ser la pastelería de referencia en la ciudad, ofreciendo productos artesanales y una experiencia cálida.")
    elif sub == "Misión":
        st.subheader("🎯 Nuestra Misión")
        st.write("Elaborar productos frescos, con ingredientes de calidad y atención cercana a nuestros clientes.")
    elif sub == "Contacto":
        st.subheader("📞 Contáctanos")
        st.write("📍 Calle Ejemplo 123 — Ciudad")
        st.write("📧 info@arteparis.com")
        st.write("📱 +34 600 123 456")
    else:
        st.subheader("💼 Trabaja con nosotros")
        with st.form("form_apply", clear_on_submit=True):
            nombre = st.text_input("Nombre")
            correo = st.text_input("Correo electrónico", key="apply_email")
            cv = st.file_uploader("Adjunta tu CV (pdf/docx)", type=["pdf", "docx"])
            enviar = st.form_submit_button("Enviar solicitud")
            if enviar:
                st.success("Gracias — recibimos tu solicitud. Te contactaremos si hay vacantes.")




