import streamlit as st
import google.generativeai as genai
import json

st.title("EtudIAnt : Quiz interactif")

# Configuration de l'API
if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clé API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")

# Initialisation du modèle
model = genai.GenerativeModel("gemini-1.5-flash-002")

# Sélection du niveau et de la matière
level = st.selectbox('Sélectionne ton niveau : ', ["3ème", "Seconde", "Premiere", "Terminale"])
subject = st.selectbox("Sélectionne la matière du quiz :", 
                        ["Français", "Mathématiques", "Histoire-Géographie-EMC", 
                         "Sciences et Vie de la Terre", "Physique Chimie", 
                         "Anglais", "Allemand", "Espagnol"])

# Fonction pour récupérer une question
def get_question():
    prompt = (
        f"Créer un quiz de niveau {level}, dans la matière {subject}, avec 4 choix de réponses, "
        "dont une correcte. Formate la réponse comme un container JSON contenant : "
        "question, choices, correct_answer, explanation. Parle en français."
    )
    response_ai = model.generate_content([prompt])
    
    # Assurez-vous que la réponse est un JSON valide
    try:
        data = json.loads(response_ai[0]["text"])
        return data
    except (json.JSONDecodeError, KeyError):
        st.error("Erreur lors de la génération de la question. Réessayez.")
        return None

# Initialisation des variables de session
if "form_count" not in st.session_state:
    st.session_state["form_count"] = 0
if "data" not in st.session_state:
    st.session_state["data"] = None

# Bouton pour créer un quiz
if st.button("Créer un quiz"):
    quiz_data = get_question()
    if quiz_data:
        st.session_state["data"] = quiz_data
        st.session_state["form_count"] += 1

# Affichage de la question si disponible
if st.session_state["data"]:
    quiz_data = st.session_state["data"]
    st.markdown(f"**Question :** {quiz_data['question']}")
    
    # Formulaire pour répondre au quiz
    form = st.form(key=f"quiz_form_{st.session_state['form_count']}")
    user_choice = form.radio("Trouve la bonne réponse :", quiz_data['choices'])
    submitted = form.form_submit_button("Vérifier")

    if submitted:
        if user_choice == quiz_data["correct_answer"]:
            st.success("Bonne réponse !")
        else:
            st.error("Pas la bonne réponse, tu feras mieux la prochaine fois !")
            st.markdown(f"**Explication :** {quiz_data['explanation']}")

        # Réinitialisation pour la prochaine question
        next_question = st.button("Prochaine question")
        if next_question:
            with st.spinner("L'EtudIAnt réfléchit..."):
                new_data = get_question()
                if new_data:
                    st.session_state["data"] = new_data
                    st.session_state["form_count"] += 1

