import streamlit as st

logo = "logo.png"
st.set_page_config(
    page_title="EtudIAnt",
    page_icon= logo,
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)
pg = st.navigation([st.Page("E_API_Key.py", title ="Connexion à l'EtudIAnt"),st.Page("E_Quiz.py", title = "Quiz interactif"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_T.py", title= "Créateur de contrôle")])

pg.run()
