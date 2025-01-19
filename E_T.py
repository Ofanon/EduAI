import streamlit as st
import google.generativeai as genai
import time
from PIL import Image
import io
import base64

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clée API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")
if "analyze_image_finished" not in st.session_state:
    st.session_state["analyze_image_finished"] = False

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

def convert_image_to_base64(image):

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    
    return base64.b64encode(buffer.read()).decode('utf-8')

st.title("EtudIAnt : Créateur de contrôles")

uploaded_files = st.file_uploader("Télécharge les photos de tes cours.", type=["png", "jpg", "jpeg", "bmp"], accept_multiple_files=True)



if st.button("Créer un contrôle sur ce cours"):
    if "api_key" in st.session_state:

        images_data = []

        for file in uploaded_files:
            image = Image.open(file)
            st.image(image, use_container_width=True)
            images_data.append(image)


        if not st.session_state["analyze_image_finished"]:
            prompt = "Voici un groupe d'images d'un cours. Crée un contrôle basé sur ces images. \
                      Le contrôle doit contenir différents types de questions (QCM, questions ouvertes, etc.)."
            
            with st.spinner("L'EtudIAnt reflechit..."):
                response = model.generate_content([
                    images_data,
                    [prompt]
                ])
                st.write(response.text)
            

