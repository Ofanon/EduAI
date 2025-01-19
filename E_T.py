import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
from fpdf import FPDF

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clée API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")

if "analyze_image_finished" not in st.session_state:
    st.session_state["analyze_image_finished"] = False

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

st.title("EtudIAnt : Créateur de contrôles")

uploaded_files = st.file_uploader("Télécharge les photos de tes cours.", type=["png", "jpg", "jpeg", "bmp"], accept_multiple_files=True)

def display_images(files):
    images = []
    for file in files:
        image = Image.open(file)
        st.image(image, caption=file.name, use_container_width=True)
        images.append(image)
    return images

place_holder_button = st.empty()
if uploaded_files:
    if place_holder_button.button("Créer un contrôle sur ce cours"):
        if "api_key" in st.session_state:
            images = display_images(uploaded_files)
            if not st.session_state["analyze_image_finished"]:
                prompt = "Voici un groupe d'images d'un cours. Crée un contrôle basé sur ces images. \
                        Le contrôle doit contenir différents types de questions (QCM, questions ouvertes, etc.)."

                with st.spinner("L'EtudIAnt reflechit..."):
                    place_holder_button.empty()
                    response = model.generate_content([prompt]+ images)
                    st.write(response.text)

                file_name = "controle_genere.txt"
                with open(file_name, "w") as f:
                    f.write(response.text)

                with open(file_name, "r") as f:
                    st.download_button(
                        label="Télécharger le contrôle",
                        data=f,
                        file_name=file_name,
                        mime="text/plain"
                    )
