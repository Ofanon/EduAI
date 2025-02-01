import streamlit as st
import db_manager
import streamlit as st
import db_manager

# ✅ Récupérer ou créer un `user_id` unique et permanent
user_id = db_manager.get_or_create_user_id()

st.title("Bienvenue sur EtudIAnt 🚀")
st.write(f"✅ Votre user_id : `{user_id}`")

# ✅ Vérifier si l'utilisateur a encore des requêtes IA
requests_left = db_manager.get_requests_left()
st.write(f"⭐ Requêtes IA restantes : `{requests_left}`")


with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db_manager.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

