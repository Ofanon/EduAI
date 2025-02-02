import streamlit as st
import user_manager

st.title("🔑 Authentification sécurisée")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if user_manager.authenticate(username, password):  
                st.success(f"✅ Bienvenue {username} !")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["experience_points"] = user_manager.get_experience_points(username)
                st.session_state["requests"] = user_manager.get_requests_left(username)
                st.rerun()

    with tab2:
        new_username = st.text_input("Nom d'utilisateur", key="new_user")
        new_email = st.text_input("Email", key="new_email")
        new_password = st.text_input("Mot de passe", type="password", key="new_password")

        if st.button("Créer un compte"):
            success, message = user_manager.initialize_user(new_username, new_email, new_password)
            if success:
                st.success(message)
                st.session_state["authenticated"] = True
                st.session_state["username"] = new_username
                st.session_state["experience_points"] = 0
                st.session_state["requests"] = 5
                st.rerun()
            else:
                st.error(message)
