import streamlit as st
import google.generativeai as genai
import time
from PIL import Image

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clée API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

st.title("EtudIAnt : Créateur de contrôles")

if "analyze_image_finished" not in st.session_state:
    st.session_state["analyze_image_finished"] = False

uploaded_file = st.file_uploader("Télécharge les photos de tes cours.", type=["png", "jpg", "jpeg", "bmp"], accept_multiple_files=True)

if st.button("Créer un contrôle sur ce cours"):
    if "api_key" in st.session_state:
        for file in uploaded_file:
            image = Image.open(file)
            st.image(image, use_column_width=True)

