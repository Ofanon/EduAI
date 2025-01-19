import google.generativeai as genai
import PIL.Image
import streamlit as st
import time
st.title("EtudIAnt : Aide aux devoirs")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clé API non enregistrée, veuillez vous rendre dans l'onglet 'Connexion à l'EtudIAnt' pour l'enregistrer.")

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"]=[]
if "response_ai" not in st.session_state:
    st.session_state["response_ai"] = None
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "image" not in st.session_state:
    st.session_state["image"] = None

uploaded_file = st.file_uploader("Télécharger une image", type=["png", "jpeg", "jpg", "bmp"])
st.session_state["uploaded_file"] = uploaded_file

def response_generator(message, chat_msg):
    displayed_text = ""
    for char in message:
        displayed_text += char
        chat_msg.markdown(f"**IA** : {displayed_text}")
        time.sleep(0.005)

if uploaded_file:
    if "api_key" in st.session_state:
        placeholder = st.empty()
        if placeholder.button("Résoudre le devoir"):
            image = PIL.Image.open(uploaded_file)
            image_st = st.image(image, use_container_width=True)
            st.session_state["image"] = image_st
            if "image_analyzed" not in st.session_state:
                prompt = "Répond à cette exercice le plus précisement possible. En parlant en francais, jamais en anglais"
                with st.spinner("L'EtudIAnt reflechit..."):
                    response_ai = model.generate_content([prompt, image])
                    response_ai_user = response_ai.text
                    st.session_state["response_ai"] = response_ai_user
                    st.session_state["chat_history"].append({"role":"assistant","content":response_ai.text})
                    st.session_state["image_analyzed"] = True
                    placeholder.empty()
    else:
        st.error("Veuillez enregister votre clé API pour utiliser l'EtudIAnt.")

if "image_analyzed" in st.session_state:
    if "api_key" in st.session_state:
        history = []
        user_input = st.chat_input("ex : je n'ai pas compris ta réponse dans l'exercice B")
        if user_input:
            st.session_state["chat_history"].append({"role":"user","content":user_input})
            history.append({"role":"model", "parts":st.session_state["response_ai"]})
            chat = model.start_chat(history = history)
            response = chat.send_message(user_input)
            st.session_state["chat_history"].append({"role":"assistant","content":response.text})
            history.append({"role":"user", "parts":user_input})
            history.append({"role":"model", "parts":response.text})
    else:
        st.error("Veuillez enregister votre clé API pour utiliser l'EtudIAnt.")

if "chat_history" in st.session_state:
    for i,message in enumerate(st.session_state["chat_history"]):
        if message["role"] == "user": 
            with st.chat_message('user'):
                st.write(f"**Vous** : {message['content']}")
        elif message["role"] == "assistant":
            if i == len(st.session_state["chat_history"]) - 1:
                with st.chat_message('assistant') as chat_msg:
                    response_generator(message['content'], chat_msg)
            
