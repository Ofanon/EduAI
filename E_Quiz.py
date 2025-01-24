import google.generativeai as genai
import streamlit as st
import json
import re

st.title("EtudIAnt : Quiz interactif")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clé API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")

placeholder_prompt = st.empty()

model = genai.GenerativeModel("gemini-1.5-flash-002")

if "started" not in st.session_state:
    if "api_key" in st.session_state:
        st.session_state.level = None
        st.session_state.subject = None
        st.session_state.prompt = None
        st.session_state.started = False
        st.session_state.data = {}
        st.session_state.question_count = 1
        st.session_state.last_question = None
        st.session_state.question = None
        st.session_state.choices = None
        st.session_state.can_verify = False
        st.session_state.verified = False
        st.session_state.correct_responses = 0
        st.session_state.correct_answer = None
        st.session_state.explanation = None
        st.session_state.next_question = False
        st.session_state.already_prompted = False
    else:
        st.error("Veuillez enregister votre clé API pour utiliser l'EtudIAnt.")

def get_question(level, subject, prompt):

    with st.spinner("Le quiz est en cours de création"):
        response_ai = model.generate_content([f"Crée un QCM d'une question de niveau {level} et de matière {subject} de sujet : {prompt}, ne fais pas la meme question que ça : {st.session_state.last_question}, en variant les sujets, avec 4 réponses pour une réponse correcte. La réponse doit etre comme un container JSON que json.loads peut utiliser : question_number, question , choices , correct_answer , explanation "])
        match = re.search(r'{.*}', response_ai.text, re.DOTALL)

        if match:

            json_text = match.group(0)
            data = json.loads(json_text)

            return data
    
if not st.session_state.started:
    user_input = st.text_input("Le sujet du quiz (optionel) :", placeholder="Ex : sur la révolution")
    st.session_state.level = st.selectbox('Sélectionne ton niveau : ', ["CP","6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
    st.session_state.subject = st.selectbox('Sélectionne la matière du quiz :', ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie","Technologie", "Anglais","Allemand", "Espagnol"])
    if user_input and st.session_state.already_prompted is False:
        st.session_state.prompt = user_input
        st.session_state.already_prompted = True

    if st.button("Créer un quiz"):
        st.session_state.data = get_question(level=st.session_state.level , subject=st.session_state.subject, prompt=st.session_state.prompt)
        st.session_state.question = st.session_state.data['question']
        st.session_state.last_question = st.session_state.question
        st.session_state.choices = st.session_state.data['choices']
        st.session_state.verified = False
        st.session_state.correct_answer = st.session_state.data['correct_answer']
        st.session_state.explanation = st.session_state.data['explanation']
        st.session_state.started = True
        st.rerun()

else:
    st.progress(st.session_state.question_count/10)

    st.subheader(f"Question {st.session_state.question_count} : {st.session_state.data['question']}")
    radio_disabled = st.session_state.verified
    user_response = st.radio("Sélectionne ta réponse : ", st.session_state.data['choices'], disabled=radio_disabled)
    verify_button_disabled = st.session_state.verified
    if st.button("Verifier", disabled=verify_button_disabled):

        st.session_state.verified = True
        st.rerun()

    if st.session_state.verified == True:

        if user_response == st.session_state.data['correct_answer']:

            st.success("Bien joué, tu as trouvé la bonne réponse !")
            st.session_state.correct_responses += 1

        else:
            st.error(f"Mauvaise réponse, la bonne réponse était : {st.session_state.data['correct_answer']}")

        st.write(st.session_state.data['explanation'])

    if st.session_state.verified == True:

        if st.session_state.question_count != 10:

            if st.button("Continuer"):

                st.session_state.data = get_question(level=st.session_state.level , subject=st.session_state.subject, prompt=st.session_state.prompt)
                st.session_state.question = st.session_state.data['question']
                st.session_state.last_question = st.session_state.data['question']
                st.write(f"Derniere question : {st.session_state.last_question}")
                st.session_state.choices = st.session_state.data['choices']
                st.session_state.correct_answer = st.session_state.data['correct_answer']
                st.session_state.verified = False
                st.session_state.question_count += 1
                st.rerun()

        else:
                
            st.title(f"Tu as fini le quiz en {st.session_state.subject} !")
            st.subheader(f"Ton score est de : {st.session_state.correct_responses * 2}/20 ")
    
    

        
        
    
    