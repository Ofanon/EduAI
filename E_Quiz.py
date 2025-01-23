import google.generativeai as genai
import streamlit as st
import json
import	time

genai.configure(api_key=st.text_input("La clé api"))

level = st.selectbox('Sélectionne ton niveau : ', ["6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox('Sélectionne la matière de ta fiche de révision:', ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"])

if "data" not in st.session_state:
    st.session_state["data"] = []
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 1

def get_question():
    model = genai.GenerativeModel("gemini-1.5-flash-002")
    with st.spinner("Le quiz est en cours de création"):
        response = model.generate_content(f"Crée un QCM d'une question de niveau {level} et de matière {subject}, avec 4 réponses pour une réponse correcte. La réponse doit etre comme un container JSON : question , choices , correct_answer , explanation ")
    st.write(response.text)
    jtopy=json.dumps(response.text)
    data = json.loads(jtopy)
    return data

if st.button("Commencer le quiz"):
    st.session_state["data"] = get_question()
    quiz_data = st.session_state["data"]
    st.subheader(f"Question {st.session_state["question_count"]} : {quiz_data[0:5]}")

