import streamlit as st

page = st.sidebar.selectbox("Choisir une page", ("Aide aux devoirs", "Créateur de fiche de révision","Configuration de la clée API"))

if page == "Aide aux devoirs":
    import E_H
elif page == "Créateur de fiche de révision":
    import E_R

elif page == "Configuration de la clée API":
    import E_API_Key