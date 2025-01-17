import streamlit as st

pg = st.navigation([st.Page("E_API_Key.py", title ="Configuration de ta clée API"), st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision")])

pg.run()