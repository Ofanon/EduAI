import streamlit as st
import google.generativeai as genai
import random

st.title("EtudIAnt : Simulation examen")


genai.configure(api_key=st.text_input("clé api"))


if "responses_questions" not in st.session_state:
    st.session_state["responses_questions"] = []

model = genai.GenerativeModel("gemini-1.5-flash-002")

level = st.selectbox('Sélectionne ton niveau : ', ["3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox("Sélectionne l'épreuve que tu souhaites faire :", ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"])   

exam_number_questions = random.randint(12, 16)

if st.button("Commencer l'examen"):
    for i, question in len(exam_number_questions):
        prompt = f"Crée une {i + 1}ère question pour une épreuve de {subject} de niveau {level}. Genere seulement une question, rien d'autre."
        question = model.generate_content(prompt)
        st.write(question.text)
        response = st.text_area("Entre ta réponse :")
        st.session_state["responses_questions"].append({"question" : question.text, "response":response})
        
