import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
from fpdf import FPDF
import requests
import data.db_manager as db_manager

genai.configure(api_key=st.secrets["API_KEY"])

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

if "started" not in st.session_state:
    st.session_state["analyze_image_finished"] = False
    st.session_state["chat_control"] = []
    st.session_state.started = False

st.title("EtudIAnt : Créateur de contrôles")

if st.session_state.started == False:
    level = st.selectbox('Sélectionne ton niveau : ', ["6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"])
    subject = st.selectbox('Sélectionne la matière de ta fiche de révision:', ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"])   
    difficulty = st.slider("Définis la difficultée du contrôle de 1 à 10 :", 1, 10)
    prompt = f"Voici un groupe d'images d'un cours de niveau {level}. Crée un contrôle de difficulté : {difficulty} sur 10. Comme au college ou lycée dessus en adaptant la difficultée en fonction du niveau er de la matière : {subject}. Répond en parlant francais, jamais en anglais. Ne fais pas ton introduction dans la réponse, fais directement le contrôle"
    uploaded_files = st.file_uploader("Télécharge les photos de tes cours.", type=["png", "jpg", "jpeg", "bmp"], accept_multiple_files=True)

def display_images(files):
    images = []
    for file in files:
        image_pil = Image.open(file)
        image_pil.resize((256, 256))
        st.image(image_pil, caption=file.name, use_container_width=True)
        images.append(image_pil)
    return images

place_holder_button = st.empty()

if uploaded_files:
    if place_holder_button.button("Créer un contrôle sur ce cours"):
        if db_manager.can_user_make_request():
            images = display_images(uploaded_files)
            if not st.session_state["analyze_image_finished"]:
                with st.spinner("L'EtudIAnt reflechit..."):
                    place_holder_button.empty()
                    response = model.generate_content([prompt]+ images)
                st.session_state["chat_control"].append({"role": "assistant", "content": response.text})
                st.session_state.started = True
        else:
            st.error("Votre quotas de requêtes par jour est terminé, revenez demain pour utiliser l'EtudIAnt.")

if "analyze_image_finished" in st.session_state:
    for message in st.session_state["chat_control"]:
        if message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(f"**IA** : {message['content']}")

