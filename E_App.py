import streamlit as st
from streamlit_lottie import st_lottie
import requests
import db_manager as db
import uuid



with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="Boutique"),st.Page("E_Quiz.py", title = "Quiz interactif"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_T.py", title= "Créateur de contrôle"), st.Page("E_Leaderboard.py", title="Leaderboard")])

pg.run()

