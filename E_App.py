import streamlit as st
import db_manager
user_id = db_manager.get_or_create_user_id()

st.title("Bienvenue sur EtudIAnt 🚀")
st.write(f"✅ Votre user_id : `{user_id}`")

# ✅ Afficher les infos de l'utilisateur
requests_left = db_manager.get_requests_left()
experience_points = db_manager.get_experience_points()

st.write(f"⭐ Requêtes IA restantes : `{requests_left}`")
st.write(f"🎓 Points d'expérience : `{experience_points}`")

# ✅ Ajouter un bouton pour utiliser une requête
if st.button("🤖 Utiliser une requête IA"):
    if db_manager.consume_request():
        st.success("✅ Requête utilisée avec succès !")
    else:
        st.error("❌ Plus de requêtes disponibles. Achetez-en avec vos points d'expérience !")

with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db_manager.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

