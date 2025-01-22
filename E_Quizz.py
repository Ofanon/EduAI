import streamlit as st
import google.generativeai as genai
import random

st.title("EtudIAnt : Simulation examen")


genai.configure(api_key=st.text_input("clé api"))


if "responses_questions" not in st.session_state:
    st.session_state["responses_questions"] = []

if "questions" not in st.session_state:
    st.session_state["questions"] = []

model = genai.GenerativeModel("gemini-1.5-flash-002")

level = st.selectbox('Sélectionne ton niveau : ', ["3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox("Sélectionne l'épreuve que tu souhaites faire :", ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"])   

exam_number_questions = random.randint(12, 16)
st.write(exam_number_questions)

if st.button("Commencer l'examen"):
    if "finish_exam" not in st.session_state:
        with st.spinner("L'EtudIAnt reflechit..."):
            for i in range(exam_number_questions):
                prompt = f"Crée une {i + 1}ère question pour une épreuve de {subject} de niveau {level}. Genere seulement une question, rien d'autre. Rajoute un emoji ou un symbole."
                question = model.generate_content(prompt)
                st.session_state["questions"].append({question})

            for i in st.session_state["questions"]:
                st.subheader(question.text)
                response = st.text_area("Entre ta réponse :", key=i)
                st.session_state["responses_questions"].append({"question" : question.text, "response":response})

    if st.button("Terminer l'examen"):
        st.session_state["finish_exam"] = True
        for response_verif in st.session_state["response_questions"], i in range(st.session_state["response_questions"]):
            verification = model.generate_content(f"Voici la question  : {response_verif["question"]}, et la réponse de l'élève : {response_verif["response"]}. Verifie la réponse et corrige la en expliquant si c'est faux.")
            st.title(f"Correction de l'examen de {subject}.")
            st.subheader(f"Response {i} :")
            st.write(verification.text)