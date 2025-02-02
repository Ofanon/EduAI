import streamlit as st
from user_manager import (
    authenticate, register_user, can_user_make_request, consume_request,
    update_experience_points, purchase_requests, get_experience_points, get_requests_left
)

st.title("🔐 Connexion / Création de Compte")

# Interface d'authentification
if "username" not in st.session_state:
    tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])

    with tab1:
        st.subheader("Connexion")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            success, user_data = authenticate(username, password)
            if success:
                st.success(f"Bienvenue {username} ! 🎉")
                st.session_state["username"] = username
                st.session_state["user_data"] = user_data
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with tab2:
        st.subheader("Créer un compte")
        new_username = st.text_input("Nom d'utilisateur", key="register_username")
        new_email = st.text_input("Email", key="register_email")
        new_password = st.text_input("Mot de passe", type="password", key="register_password")

        if st.button("S'inscrire"):
            if new_username and new_password and new_email:
                success, message = register_user(new_username, new_password, new_email)
                if success:
                    success, user_data = authenticate(username, password)
                    if success:
                        st.success(f"Bienvenue {username} ! 🎉")
                        st.session_state["username"] = username
                        st.session_state["user_data"] = user_data
                        st.session_state.authenticated = True
                        st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Veuillez remplir tous les champs.")

# Interface utilisateur après connexion
if "username" in st.session_state:
    st.subheader(f"👤 Profil de {st.session_state['username']}")

    # Récupérer les infos utilisateur si elles ne sont pas déjà chargées
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = {
            "requests": 0,
            "purchase_requests": 0,
            "experience_points": 0
        }

    # Charger les données depuis le fichier utilisateur
    requests_left = get_requests_left()
    experience = get_experience_points()

    st.write(f"**Requests restantes :** {requests_left}")
    st.write(f"**Points d'expérience :** {experience}")

