import streamlit as st
import google.generativeai as genai
import re
import json

st.title("EtudIAnt : Quiz interactif")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clé API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

def get_questions(level, subject, prompt):
        with st.spinner("L'EtudIAnt réfléchit..."):
            response_ai = model.generate_content(f"Crée un QCM de 10 questions de niveau {level} en {subject} et de sujet : {prompt}. Toutes les réponses doivent etre dans un container JSON avec : question_number , question , choices , correct_answer , explanation.")
        match = re.search(r'\[.*\]', response_ai.text, re.DOTALL)
        if match:
                json_text = match.group(0)
                data = json.loads(json_text)
                return data
        else:
            st.error("Erreur lors de la création des questions.")
            return []

if "started" not in st.session_state:
      st.session_state.level = None
      st.session_state.subject = None
      st.session_state.user_prompt = None
      st.session_state.current_question = 0
      st.session_state.question_count = 1
      st.session_state.started = False
      st.session_state.data = {}
      st.session_state.question = None
      st.session_state.choices = None
      st.session_state.correct_answer = None
      st.session_state.correct_answers = 0
      st.session_state.verified = False
      st.session_state.explanation = None
      st.rerun()

else :

    if not st.session_state.started:
        st.session_state.user_prompt = st.text_input("Le sujet du quiz (optionel) :", placeholder="Ex : sur la révolution")
        st.session_state.level = st.selectbox('Sélectionne ton niveau : ', ["CP","6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
        st.session_state.subject = st.selectbox('Sélectionne la matière du quiz :', ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie","Technologie", "Anglais","Allemand", "Espagnol"])
        
        if st.button("Créer le quiz"):
            if "api_key" in st.session_state:
                st.session_state.data = get_questions(level=st.session_state.level, subject=st.session_state.subject, prompt=st.session_state.user_prompt)
            else:
                st.error("Veuillez enregistrer votre clé API pour utiliser l'EtudIAnt.")
        
        if st.session_state.data:
            st.session_state.current_question = st.session_state.data[st.session_state.question_count]
            st.session_state.question = st.session_state.current_question['question']
            st.session_state.choices = st.session_state.current_question['choices']
            st.session_state.correct_answer = st.session_state.current_question['correct_answer']
            st.session_state.explanation = st.session_state.current_question['explanation']
            st.session_state.correct_answers = 0
            st.session_state.started = True
            st.rerun()

    if st.session_state.started:
        if st.session_state.question_count < 9:
            st.progress(st.session_state.question_count/10)

            disable_radio = st.session_state.verified
            disable_verify = st.session_state.verified
            st.subheader(st.session_state.question)
            user_repsponse = st.radio("Sélectionne ta réponse :", st.session_state.choices, disabled=disable_radio)

            if st.button("Verifier", disabled=disable_verify):
                st.session_state.verified = True
                st.rerun()

            if st.session_state.verified == True:

                if user_repsponse == st.session_state.correct_answer:
                    st.success("Bien joué, tu as trouvé la bonne réponse !")
                    st.session_state.correct_answers += 1

                else:

                    st.error(f"Raté, la bonne réponse était : {st.session_state.correct_answer}")
                st.write(st.session_state.explanation)

            if st.session_state.verified == True:
                if st.button("Continuer"):
                    st.session_state.verified = False
                    st.session_state.question_count += 1
                    st.session_state.current_question = st.session_state.data[st.session_state.question_count] 
                    st.session_state.question = st.session_state.current_question['question']
                    st.session_state.choices = st.session_state.current_question['choices']
                    st.session_state.correct_answer = st.session_state.current_question['correct_answer']
                    st.session_state.explanation = st.session_state.current_question['explanation']
                    st.rerun()
        else:
            st.subheader(f"Bravo ! Le quiz en {st.session_state.subject} est terminé !")
            st.write(f"Votre note est de {st.session_state.correct_answers}/20 !")
            if st.button("Refaire un autre quiz"):
                del st.session_state.started


