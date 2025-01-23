import google.generativeai as genai
import streamlit as st
import json

genai.configure(api_key=st.text_input("La clé api"))

level = st.selectbox('Sélectionne ton niveau : ', ["6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox('Sélectionne la matière de ta fiche de révision:', ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"])

if "data" not in st.session_state:
    st.session_state["data"] = None
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 1

def get_question():
    model = genai.GenerativeModel("gemini-1.5-flash-002")
    with st.spinner("Le quiz est en cours de création"):
        response = model.generate_content(f"Crée un QCM d'une question de niveau {level} et de matière {subject}, avec 4 réponses pour une réponse correcte. La réponse doit etre en format text, pas code, decodable par JSON avec : question, choices, correct_answer, explanation ")
    st.write(response.text)
    data = json.loads({
  "question": "Quel mot est un synonyme de \"joie\" ?",
  "choices": [
    "tristesse",
    "bonheur",
    "colère",
    "peur"
  ],
  "correct_answer": "bonheur",
  "explanation": "Le mot \"bonheur\" exprime un sentiment de satisfaction et de contentement, tout comme le mot \"joie\"."
})
    return data

if st.button("Commencer le quiz"):
    st.session_state["data"] = get_question()
    quiz_data = st.session_state["data"]
    st.subheader(f"Question {st.session_state["question_count"]} : {quiz_data}")

