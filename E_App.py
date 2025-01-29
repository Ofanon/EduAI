import streamlit as st
from streamlit_lottie import st_lottie
import requests
import db_manager as db
import uuid

if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

import streamlit as st
import db_manager

if "user_id" not in st.session_state:
    st.session_state["user_id"] = db_manager.get_user_id()

st.write(f"👤 ID utilisateur : `{st.session_state['user_id']}`")
st.write(f"⭐ Requêtes restantes : {db_manager.get_requests_left()}")
st.write(f"💰 Points d'expérience : {db_manager.get_experience_points()}")


with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="Boutique"),st.Page("E_Quiz.py", title = "Quiz interactif"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_T.py", title= "Créateur de contrôle")])

pg.run()

