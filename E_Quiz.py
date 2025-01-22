import streamlit as st
import google.generativeai as genai
import json

st.title("EtudIAnt : Quiz interactif")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clé API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")
    
if "quiz_data_ai" not in st.session_state:
    st.session_state["quiz_data_ai"] = []

level = st.selectbox('Sélectionne ton niveau : ', ["3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox("Sélectionne la matière du quiz :", ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"]) 
model = genai.GenerativeModel("gemini-1.5-flash-002")

def get_question():
    prompt = f"Créer un QCM d'une question, de niveau {level}, dans la matière {subject}, avec 4 choix de réponses pour une reponse correcte. Repond comme un container JSON avec : question, choices, correct_answer, explanation."
    response_ai = model.generate_content(prompt)
    st.write(response_ai.text)
    data = json.loads(response_ai.text)
    return data

if st.button("Créer un quiz"):
    quiz_data = get_question()
    st.markdown(f"Question : {quiz_data['question']}")
    form = st.form(key=f"quiz_form_{st.session_state["form_count"]}")
    user_choice = form.radio(f"Trouve la bonne réponse :", quiz_data['choices'])
