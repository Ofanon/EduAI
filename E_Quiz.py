import streamlit as st
import google.generativeai as genai
import re
import json
from streamlit_lottie import st_lottie
import requests
import db_manager as db

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_quiz = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json")

st.title("EtudIAnt : Quiz interactif")

genai.configure(api_key=st.secrets["API_KEY"])

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

def get_questions(level, subject, prompt, difficulty):
        with st.spinner("La création du quiz est en cours...") :
            response_ai = model.generate_content(f"Crée un QCM de 10 questions de niveau {level} en {subject}, de sujet : {prompt}. De diffcultée : {difficulty} sur 10. Toutes les réponses doivent etre dans un container JSON avec : question_number , question , choices , correct_answer , explanation.")
        match = re.search(r'\[.*\]', response_ai.text, re.DOTALL)
        if match:
                json_text = match.group(0)
                data = json.loads(json_text)
                return data
        else:
            st.error("Erreur lors de la création des questions.")
            return []

with st.spinner("La page est en cours de chargement..."):
    if "started" not in st.session_state:
        st.session_state.level = None
        st.session_state.subject = None
        st.session_state.difficulty = None
        st.session_state.user_prompt = None
        st.session_state.current_question = None
        st.session_state.question_count = 1
        st.session_state.started = False
        st.session_state.data = None
        st.session_state.question = None
        st.session_state.choices = None
        st.session_state.correct_answer = None
        st.session_state.correct_answers = 0
        st.session_state.verified = False
        st.session_state.explanation = None
        st.session_state.note = None
        st.session_state.points = None


if "started" in st.session_state:

    if not st.session_state.started:
        col1, col2 = st.columns(2)
        st.session_state.can_start = False
        with col1:
            st.session_state.subject = st.selectbox('Sélectionne la matière du quiz :', ["Français", "Mathématiques", "Histoire","Géographie","EMC", "Sciences et Vie de la Terre", "Physique Chimie","Technologie", "Anglais","Allemand", "Espagnol"])
            st.session_state.user_prompt = st.text_input("Le sujet du quiz (optionel) :", placeholder="Ex : sur la révolution")
        with col2:
            st.session_state.level = st.selectbox('Sélectionne ton niveau : ', ["CP","6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
            st.session_state.difficulty = st.slider("Définis une difficultée pour ce quiz :", 0, 10)
        
        if st.button("Créer le quiz", disabled=st.session_state.can_start):
            if db.can_user_make_request():
                db.consume_request()
                st.session_state.can_start = True
                st.session_state.data = get_questions(level=st.session_state.level, subject=st.session_state.subject, prompt=st.session_state.user_prompt, difficulty=st.session_state.difficulty)
            else:
                st.error("Votre quota est épuisé, revenez demain pour utiliser l'EtudIAnt.")
        
        if "data" in st.session_state and st.session_state.data:
            st.session_state.current_question = st.session_state.data[st.session_state.question_count]
            st.session_state.question = st.session_state.current_question['question']
            st.session_state.choices = st.session_state.current_question['choices']
            st.session_state.correct_answer = st.session_state.current_question['correct_answer']
            st.session_state.explanation = st.session_state.current_question['explanation']
            st.session_state.started = True
            st.rerun()

    if st.session_state.started:
        if st.session_state.question_count < 10:
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
                    db.update_experience_points(points=20)
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
            st.session_state.note = (st.session_state.correct_answers / 10) * 20
            st.subheader(f"Bravo ! Le quiz en {st.session_state.subject} est terminé !")
            st.subheader(f"Votre note est de {st.session_state.note}/20 !")
            if st.session_state.points == None:
                st.session_state.points = st.session_state.note * 10
            st.success(f"Vous avez gagné {st.session_state.points} points d'experience !")
            st.balloons()
            if st.button("Refaire un autre quiz"):
                del st.session_state.started
                st.session_state.can_start = False


