import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
from fpdf import FPDF

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clé API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

if "analyze_image_finished" not in st.session_state:
    st.session_state["analyze_image_finished"] = False
if "chat_control" not in st.session_state:
    st.session_state["chat_control"] = []

st.title("EtudIAnt : Créateur de contrôles")

level = st.selectbox('Sélectionne ton niveau : ', ["6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
subject = st.selectbox('Sélectionne la matière de ta fiche de révision:', ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"])   
difficulty = st.slider("Définis la difficultée du contrôle de 1 à 10 :", 1, 10)
prompt = f"Voici un groupe d'images d'un cours de niveau {level}. Crée un contrôle de difficulté : {difficulty} sur 10. Comme au college ou lycée dessus en adaptant la difficultée en fonction du niveau er de la matière : {subject}. Répond en parlant francais, jamais en anglais. Ne fais pas ton introduction dans la réponse, fais directement le contrôle"
uploaded_files = st.file_uploader("Télécharge les photos de tes cours.", type=["png", "jpg", "jpeg", "bmp"], accept_multiple_files=True)

def display_images(files):
    images = []
    for file in files:
        image_pil = Image.open(file)
        image_pil.resize((512, 512))
        st.image(image_pil, caption=file.name, use_container_width=True)
        images.append(image_pil)
    return images

place_holder_button = st.empty()
if uploaded_files:
    if "api_key" in st.session_state:
        if place_holder_button.button("Créer un contrôle sur ce cours"):
                images = display_images(uploaded_files)
                if not st.session_state["analyze_image_finished"]:
                    with st.spinner("L'EtudIAnt reflechit..."):
                        place_holder_button.empty()
                        response = model.generate_content([prompt]+ images)
                    st.session_state["chat_control"].append({"role": "assistant", "content": response.text})
    else:
        st.error("Veuillez enregistrer votre clé API pour utiliser l'EtudIAnt.")

if "analyze_image_finished" in st.session_state:
    for message in st.session_state["chat_control"]:
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown('<div class="response-container">', unsafe_allow_html=True)
                st.write(f"**IA** : {message['content']}")

st.markdown(
    """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
    #capture-button { 
        padding: 10px; 
        background-color: #4CAF50; 
        color: white; 
        border: none; 
        cursor: pointer; 
        font-size: 16px; 
        border-radius: 5px; 
        margin-top: 10px; 
    }
    #capture-button:hover { background-color: #45a049; }
    </style>
    <button id="capture-button">📸 Capturer la réponse</button>
    <script>
    document.getElementById('capture-button').onclick = function() {
        const responseElement = document.querySelector('.response-container');
        html2canvas(responseElement).then(canvas => {
            const link = document.createElement('a');
            link.download = 'response.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    };
    </script>
    """,
    unsafe_allow_html=True
)