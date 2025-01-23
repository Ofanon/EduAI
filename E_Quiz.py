import google.generativeai as genai
import streamlit as st
import json
import re
import time

genai.configure(api_key=st.text_input("La clé api"))

placeholder_prompt = st.empty()

level = st.selectbox('Sélectionne ton niveau : ', ["6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox('Sélectionne la matière de ta fiche de révision:', ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"])

prompt_user = placeholder_prompt.chat_input("ex : sur la révolution")

model = genai.GenerativeModel("gemini-1.5-flash-002")

if "data" not in st.session_state:
    st.session_state["data"] = {}
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 1
if "user_response" not in st.session_state:
    st.session_state["user_response"] = None
if "start" not in st.session_state:
    st.session_state["start"] = None

def get_question():
    response_ai = ()
    with st.spinner("Le quiz est en cours de création"):
        response_ai = model.generate_content([f"Crée un QCM d'une question de niveau {level} et de matière {subject} {st.session_state.user_response} , avec 4 réponses pour une réponse correcte. La réponse doit etre comme un container JSON que json.loads peut utiliser : question , choices , correct_answer , explanation "])
    try:
        match = re.search(r'{.*}', response_ai.text, re.DOTALL)
        if match:
            json_text = match.group(0)
            data = json.loads(json_text)
            
            return data
        else:
            st.error("Aucun JSON valide trouvé dans la réponse de l'IA.")
            return None
    except json.JSONDecodeError as e:
        st.error(f"Erreur lors du décodage JSON : {str(e)}")
        return None
    

def inizalize_QCM():
    st.session_state.data = get_question()
    st.session_state["start"] = True


placeholder_prompt = st.empty()
if prompt_user:
    st.session_state.user_response = prompt_user
    inizalize_QCM()

if st.session_state.start == True:
    st.subheader(f"Question {st.session_state.question_count} : {st.session_state.data['question']}")
    placeholder_prompt.empty()
    user_response = st.radio("Séléctionne ta réponse :", st.session_state.data['choices'])
    if st.button("Verifier"):
        if user_response == st.session_state.data['correct_answer']:
            st.success("Bien joué, tu as trouvé la bonne réponse !")
        else:
            st.error("Mauvaise réponse, tu feras mieux la prochaine fois !")
        st.write(st.session_state.data['explanation'])

if st.button("Continuer"):
    st.session_state["start"] = False
    inizalize_QCM()
    st.rerun()