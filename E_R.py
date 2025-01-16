import google.generativeai as genai
import streamlit as st

st.title("EtudIAnt : fiche de révision")

genai.configure(api_key=st.text_area("Ta clée API."))
model = genai.GenerativeModel("gemini-1.5-flash-002")

st.subheader("Sur quoi veux-tu créer une fiche de révision ?")
prompt = "Crée une fiche de revision le plus précisement possible"
prompt_user = st.text_input("ex : sur la seconde guerre mondiale")

if prompt_user:
    response = model.generate_content([prompt_user, prompt])
    st.write(response.text)


