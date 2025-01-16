import google.generativeai as genai
import streamlit as st
import time

st.title("EtudIAnt : fiche de révision")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])

else:
    st.error("Clée API non enregistrée, veuillez vous rendre dans l'onglet 'Configuration de la clée API' pour l'enregistrer.")

model = genai.GenerativeModel("gemini-1.5-flash-002")

st.subheader("Sur quoi veux-tu créer une fiche de révision ?")
prompt = "Crée une fiche de revision le plus précisement possible, en parlant en francais, jamais en anglais"
prompt_user = st.chat_input("ex : sur la seconde guerre mondiale")

if prompt_user:
    st.write("Analyse de l'image en cours...")
    time.sleep(3)
    with st.spinner("L'ia réfléchit"):
        response = model.generate_content([prompt_user, prompt])
        st.write(response.text)


