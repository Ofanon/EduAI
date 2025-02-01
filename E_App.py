import streamlit as st
import db_manager

st.set_page_config(page_title="EduAI - Connexion", layout="wide")

# ✅ Récupérer le gestionnaire de cookies
cookie_manager = db_manager.get_cookie_manager()

# ✅ Vérifier si l'utilisateur est connecté
user_id = cookie_manager.get("user_id")

st.sidebar.title("🔐 Connexion")

if user_id:
    # ✅ Récupérer les infos utilisateur
    user_info = db_manager.get_user_info(user_id)

    if user_info:
        email, experience_points, requests_left = user_info
        st.sidebar.success(f"Connecté en tant que : {email}")
        st.sidebar.write(f"🎓 Points d'expérience : `{experience_points}`")
        st.sidebar.write(f"⭐ Requêtes IA restantes : `{requests_left}`")

        # ✅ Navigation entre les pages
        page = st.sidebar.radio("📂 Accès Rapide", [
            "🛒 Boutique", "🎯 Quiz interactif", "📚 Aide aux devoirs", 
            "📒 Créateur de fiches de révision", "📝 Créateur de contrôle", "⭐💎 Aide"
        ])

        if page == "🛒 Boutique":
            st.experimental_set_query_params(page="E_Shop")
        elif page == "🎯 Quiz interactif":
            st.experimental_set_query_params(page="E_Quiz")
        elif page == "📚 Aide aux devoirs":
            st.experimental_set_query_params(page="E_H")
        elif page == "📒 Créateur de fiches de révision":
            st.experimental_set_query_params(page="E_R")
        elif page == "📝 Créateur de contrôle":
            st.experimental_set_query_params(page="E_T")
        elif page == "⭐💎 Aide":
            st.experimental_set_query_params(page="E_Help")

        # ✅ Bouton pour se déconnecter
        if st.sidebar.button("🚪 Déconnexion"):
            cookie_manager.delete("user_id")
            st.sidebar.success("Déconnecté avec succès !")
            st.experimental_rerun()

    st.title("Bienvenue sur EduAI 🚀")
    st.write(f"✅ Votre user_id : `{user_id}`")

else:
    # ✅ Interface Unique : Connexion / Inscription
    st.sidebar.subheader("Connexion ou Inscription")
    
    mode = st.sidebar.radio("Choisissez une option :", ["Se connecter", "Créer un compte"])

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Mot de passe", type="password")

    if mode == "Créer un compte":
        if st.sidebar.button("📝 Créer un compte"):
            if db_manager.register_user(email, password):
                st.sidebar.success("✅ Compte créé avec succès ! Connectez-vous.")
                st.experimental_rerun()
            else:
                st.sidebar.error("❌ Cet email est déjà utilisé.")

    else:
        if st.sidebar.button("🔑 Se connecter"):
            user_id = db_manager.login_user(email, password)
            if user_id:
                cookie_manager.set("user_id", user_id)
                st.sidebar.success("✅ Connexion réussie !")
                st.experimental_rerun()
            else:
                st.sidebar.error("❌ Email ou mot de passe incorrect.")
