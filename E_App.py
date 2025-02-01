import streamlit as st
from streamlit_lottie import st_lottie
import sqlite3
import streamlit as st
import streamlit as st
import db_manager

# Récupérer ou créer un identifiant unique pour l'utilisateur
user_id = db_manager.get_user_id()
st.session_state["user_id"] = user_id

st.title("Bienvenue sur l'App EtudIAnt")
st.write(f"Votre identifiant unique : `{user_id}`")

# Afficher les points d'expérience et les requêtes restantes
points = db_manager.get_experience_points(user_id)
requests_left = db_manager.get_requests_left(user_id)

st.write(f"Points d'expérience : `{points}`")
st.write(f"Requêtes restantes : `{requests_left}`")

# Ajouter des points et des requêtes (exemple d'interaction)
if st.button("Gagner 10 points d'expérience"):
    db_manager.update_experience_points(user_id, 10)
    st.success("10 points ajoutés !")
    st.rerun()

if st.button("Acheter 1 requête avec 20 points"):
    if points >= 20:
        db_manager.update_experience_points(user_id, -20)
        db_manager.update_requests(user_id, 1)
        st.success("1 requête ajoutée !")
        st.rerun()
    else:
        st.error("Pas assez de points pour acheter une requête.")

if st.button("Utiliser une requête"):
    if requests_left > 0:
        db_manager.update_requests(user_id, -1)
        st.success("Requête utilisée !")
        st.rerun()
    else:
        st.error("Vous n'avez plus de requêtes disponibles.")


with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db_manager.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

