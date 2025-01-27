import streamlit as st
from streamlit_lottie import st_lottie
import requests
import data.db_manager as db_manager

with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db_manager.get_requests_left()}")
logo = "logo.png"

pg = st.navigation([st.Page("E_Quiz.py", title = "Quiz interactif"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_T.py", title= "Créateur de contrôle")])

pg.run()

