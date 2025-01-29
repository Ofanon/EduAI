import streamlit as st
import google.generativeai as genai
import re
import json
import db_manager

st.title("EtudIAnt : Quiz interactif")

genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

def get_questions(level, subject, prompt):
    with st.spinner("L'EtudIAnt réfléchit..."):
        response_ai = model.generate_content(
            f"Crée un QCM de 10 questions de niveau {level} en {subject} et de sujet : {prompt}. "
            "Toutes les réponses doivent être dans un container JSON avec : question_number, question, choices, correct_answer, explanation."
        )
    match = re.search(r'\[.*\]', response_ai.text, re.DOTALL)
    if match:
        json_text = match.group(0)
        data = json.loads(json_text)
        return data
    else:
        st.error("Erreur lors de la création des questions.")
        return []

if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.level = None
    st.session_state.subject = None
    st.session_state.user_prompt = None
    st.session_state.data = {}
    st.session_state.question_count = 0
    st.session_state.correct_answers = 0

st.write(f"💰 Vous avez **{db_manager.get_experience_points()} XP**.")
st.write(f"📊 Requêtes disponibles : **{db_manager.can_user_make_request()}**")

if st.button("Acheter 5 requêtes pour 50 XP"):
    if db_manager.purchase_requests(cost_in_experience=50, requests_to_add=5):
        st.success("✅ 5 requêtes achetées avec succès !")
    else:
        st.error("❌ Pas assez de points d'expérience.")

if not st.session_state.started:
    st.session_state.level = st.selectbox("📚 Niveau :", ["CP", "6ème", "5ème", "4ème", "3ème", "Seconde", "Première", "Terminale"])
    st.session_state.subject = st.selectbox("📖 Matière :", ["Mathématiques", "Histoire", "Français", "Anglais", "SVT"])
    st.session_state.user_prompt = st.text_input("🎯 Sujet du quiz :", placeholder="Ex : Révolution Française")

    if st.button("🚀 Créer le quiz"):
        if db_manager.can_user_make_request():
            db_manager.consume_request()  # Consommer une requête
            st.session_state.data = get_questions(level=st.session_state.level, subject=st.session_state.subject, prompt=st.session_state.user_prompt)
            st.session_state.started = True
            st.session_state.question_count = 0
        else:
            st.error("❌ Vous avez atteint votre quota de requêtes pour aujourd'hui.")

if st.session_state.started:
    if st.session_state.question_count < 10:
        current_question = st.session_state.data[st.session_state.question_count]
        st.subheader(f"❓ Question {st.session_state.question_count + 1}: {current_question['question']}")
        user_response = st.radio("💡 Choisissez une réponse :", current_question['choices'])

        if st.button("✅ Vérifier"):
            if user_response == current_question['correct_answer']:
                st.success("🎉 Bonne réponse ! +10 XP")
                st.session_state.correct_answers += 1
                db_manager.update_experience_points(10)
            else:
                st.error(f"❌ Mauvaise réponse. La bonne réponse est : {current_question['correct_answer']}")
            st.write(current_question['explanation'])
            st.session_state.question_count += 1
    else:
        st.subheader("🏆 Quiz terminé !")
        st.write(f"🎯 Score : **{st.session_state.correct_answers}/10**")
        if st.button("🔄 Recommencer"):
            del st.session_state.started
            st.experimental_rerun()
