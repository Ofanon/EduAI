import streamlit as st
import google.generativeai as genai
import random
import json
import time
import os

st.title("EtudIAnt : Quiz interactif")


if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clé API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")


model = genai.GenerativeModel("gemini-1.5-flash-002")

level = st.selectbox('Sélectionne ton niveau : ', ["3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox("Sélectionne la matière du quiz :", ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"]) 

def get_question():
    response_ai =  model.generate_content([f"Créer un quiz de niveau juste pour une question {level}, et dans la matière {subject} avec 4 choix de réponses pour une correcte. Tu dois parler en français pas en anglais. Crée la réponse comme un container JSON qui contient : question, choices, correct_answer, explanation."])
    response_json = response_ai.text
    time.sleep(3)
    data = json.loads(response_json)
    return data

if "form_count" not in st.session_state:
    st.session_state["form_count"] = 0


if st.button("Créer un quiz"):
    st.session_state["data"] = get_question()
    quiz_data = st.session_state["data"]
    st.markdown(f"Question : {quiz_data['question']}")
    form = st.form(key=f"quiz_form_{st.session_state["form_count"]}")
    user_choice = form.radio(f"Trouve la bonne réponse :", quiz_data['choices'])
    submitted = form.form_submit_button("Verifier")

    if submitted:
        if user_choice == quiz_data['correct_answer']:
            st.success("Bonne réponse !")
        else:
            st.error("Pas la bonne réponse, tu fera mieux la prochaine fois !") 
            st.markdown(f"Explication : {quiz_data['explanation']}")

        next_question = st.button("Prochaine question")
        with st.spinner("L'EtudIAnt réflechit..."):
            st.session_state["data"] = get_question()

        if next_question :
            st.session_state["form_count"] += 1
