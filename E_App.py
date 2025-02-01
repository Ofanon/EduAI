import streamlit as st
from streamlit_lottie import st_lottie
import db_manager as db
import sqlite3
import streamlit as st
import db_manager
import streamlit as st
import db_manager

# ✅ Récupérer ou créer un `user_id` unique par appareil
user_id = db_manager.get_or_create_user_id()

# ✅ Vérifier si l'URL contient `user_id`, sinon l'ajouter
if "user_id" not in st.experimental_get_query_params():
    st.experimental_set_query_params(user_id=user_id)

st.title("Bienvenue sur EtudIAnt 🚀")
st.write(f"✅ Votre user_id : `{user_id}`")

with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

