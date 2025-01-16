import streamlit as st

pg = st.navigation([st.Page("E_H.py", title = "Aide aux devoirs"), st.Page("E_R.py", title = "Créateur de fiches de révision"), st.Page("E_API_Key.py", title ="Configuration de la clée API")])

pg.run()
st.sidebar("Aide au devoirs", "Créateur de fiches de révision", "Configuration de la clée API")