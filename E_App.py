import streamlit as st
from streamlit_lottie import st_lottie
import requests
import data.db_manager as db_manager
st.markdown("""
    <style>
    .css-18e3th9 { 
        background-color: #effff0;  /* Vert clair */
        font-family: 'Comic Sans MS', cursive; 
    }
    .stButton>button {
        background-color: #3DDC84; /* Vert Duolingo */
        color: white;
        font-size: 16px;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)
with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db_manager.get_requests_left()}")
    pg = st.navigation([st.Page("E_Quiz.py", title = "Quiz interactif"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_T.py", title= "Créateur de contrôle")])

pg.run()

