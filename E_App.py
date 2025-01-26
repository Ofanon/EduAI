import streamlit as st

logo = "logo.png"

hide_github_icon = """
#GithubIcon {
  visibility: hidden;
}
"""
st.markdown(hide_github_icon, unsafe_allow_html=True)
pg = st.navigation([st.Page("E_API_Key.py", title ="Connexion à l'EtudIAnt"),st.Page("E_Quiz.py", title = "Quiz interactif"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_T.py", title= "Créateur de contrôle")])

pg.run()
