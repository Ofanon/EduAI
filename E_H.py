import google.generativeai as genai
import PIL.Image
import streamlit as st
import time
st.title("EtudIAnt : Aide aux devoirs")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clée API non enregistrée, veuillez vous rendre dans l'onglet 'Configuration de la clée API' pour l'enregistrer.")

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"]=[]
if "response_ai" not in st.session_state:
    st.session_state["response_ai"] = None
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "st_image" not in st.session_state:
    st.session_state["st_image"] = None
if "image_pil" not in st.session_state:
    st.session_state["image_pil"] = None

def response_typing(message_typing, key):
    placeholder_message = st.empty()
    for i in range(len(message_typing)):
        placeholder_message.markdown(message_typing[:i+1], key=key)
        time.sleep(0.05)

uploaded_file = st.file_uploader("Télécharger une image", type=["png", "jpeg", "jpg", "bmp"])
st.session_state["uploaded_file"] = uploaded_file
placeholder_button = st.empty()

if uploaded_file:
    if "api_key" in st.session_state:
        if placeholder_button.button("Résoudre le devoir"):
            image = PIL.Image.open(uploaded_file)
            st.session_state["st_image"] = image
            if "image_analyzed" not in st.session_state:
                prompt = "Répond à cette exercice le plus précisement possible. En parlant en francais, jamais en anglais"
                with st.spinner("L'EtudIAnt reflechit..."):
                    response_ai = model.generate_content([prompt, image])
                    response_ai_user = response_ai.text
                    st.session_state["response_ai"] = response_ai_user
                    st.session_state["chat_history"].append({"role":"assistant","content":response_ai.text})
                    st.session_state["image_analyzed"] = True
    else:
        st.error("Veuillez enregistrer votre clé API pour utiliser l'EtudIAnt.")

if "image_analyzed" in st.session_state:
    placeholder_button.empty()
    history = []
    user_input = st.chat_input("ex : je n'ai pas compris ta réponse dans l'exercice B")
    st.image(st.session_state["st_image"], use_container_width=True)
    if user_input:
        st.session_state["chat_history"].append({"role":"user","content":user_input})
        history.append({"role":"model", "parts":st.session_state["response_ai"]})
        chat = model.start_chat(history = history)
        response = chat.send_message(user_input)
        st.session_state["chat_history"].append({"role":"assistant","content":response.text})
        history.append({"role":"user", "parts":user_input})
        history.append({"role":"model", "parts":response.text})

if "chat_history" in st.session_state:
    for message in st.session_state["chat_history"]:
        if message["role"] == "user": 
            with st.chat_message('user'):
                st.write(f"**Vous** : {message['content']}")
        elif message["role"] == "assistant":
            with st.chat_message('assistant'):
                response_typing(f"**IA** : {message['content']}", key=len(message['content']))
