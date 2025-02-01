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

        # ✅ Vérifier si l'appareil est bien associé à cet utilisateur
        stored_device_id = db_manager.generate_device_id()
        
        if stored_device_id:
            st.sidebar.write(f"🔒 Appareil associé : `{stored_device_id}`")
        else:
            st.sidebar.error("❌ Cet appareil n'est pas autorisé à accéder à ce compte.")

        # ✅ Bouton pour se déconnecter
        if st.sidebar.button("🚪 Déconnexion"):
            cookie_manager.delete("user_id")
            st.sidebar.success("Déconnecté avec succès !")
            st.experimental_rerun()
    
    st.title("Bienvenue sur EduAI 🚀")
    st.write(f"✅ Votre user_id : `{user_id}`")

else:
    # ✅ Formulaire d'inscription
    st.sidebar.subheader("Créer un compte")
    new_email = st.sidebar.text_input("Email", key="new_email")
    new_password = st.sidebar.text_input("Mot de passe", type="password", key="new_password")
    
    if st.sidebar.button("📝 S'inscrire"):
        if db_manager.register_user(new_email, new_password):
            st.sidebar.success("✅ Inscription réussie ! Connectez-vous.")
        else:
            st.sidebar.error("❌ Cet email est déjà utilisé.")

    # ✅ Formulaire de connexion
    st.sidebar.subheader("Se connecter")
    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Mot de passe", type="password", key="login_password")
    
    if st.sidebar.button("🔑 Connexion"):
        user_id = db_manager.login_user(email, password)
        if user_id:
            cookie_manager.set("user_id", user_id)
            st.sidebar.success("✅ Connexion réussie !")
            st.experimental_rerun()
        else:
            st.sidebar.error("❌ Email ou mot de passe incorrect.")


st.write(f"⭐ Etoiles restantes : {db_manager.get_requests_left()}")
pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

