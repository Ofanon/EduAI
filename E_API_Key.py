import streamlit as st

api_key = st.text_input("Clée API")

if st.button("Enregistrer la clé API"):
    if api_key:
        st.session_state["api_key"] = api_key
        st.success("Clé API enregistrée dans la session!")
    else:
        st.error("Veuillez entrer une clé API valide.")