import streamlit as st

pg = st.navigation([st.Page("E_API_Key.py", title ="Connexion à l'EtudIAnt"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_T.py", title="Créateur de contrôles")])

pg.run()