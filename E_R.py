import google.generativeai as genai
import streamlit as st
import time

st.title("EtudIAnt : fiche de révision")

genai.configure(api_key=st.text_input("Ta clée API."))
model = genai.GenerativeModel("gemini-1.5-flash-002")

st.subheader("Sur quoi veux-tu créer une fiche de révision ?")
prompt = "Crée une fiche de revision le plus précisement possible"
prompt_user = st.chat_input("ex : sur la seconde guerre mondiale")

if prompt_user:
    st.write("Analyse de l'image en cours...")
    time.sleep(3)
    with st.spinner("L'ia réfléchit"):
        response = model.generate_content([prompt_user, prompt])
        st.write(response.text)


