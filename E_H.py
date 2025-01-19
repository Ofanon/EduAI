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

def response_typing(message):
    displayed_text = ""
    chat_msg = st.chat_message('assistant')
    for i in message.split():
        displayed_text += i
        chat_msg.text(f"**IA** : {displayed_text}")
        time.sleep(0.01)

        

uploaded_file = st.file_uploader("Télécharger une image", type=["png", "jpeg", "jpg", "bmp"])
st.session_state["uploaded_file"] = uploaded_file

if uploaded_file:
    if "api_key" in st.session_state["api_key"]:
        image = PIL.Image.open(uploaded_file)
        st_image = st.image(image, use_container_width=True)
        st.session_state["st_image"] = st.image
        placeholder = st.empty()
        if "image_analyzed" not in st.session_state:
            if placeholder.button("Resoudre cet exercice"):
                prompt = "Répond à cette exercice le plus précisement possible. En parlant en francais, jamais en anglais"
                response_ai = model.generate_content([prompt, image])
                response_ai_user = response_ai.text
                st.session_state["response_ai"] = response_ai_user
                st.session_state["chat_history"].append({"role":"assistant","content":response_ai.text})
                placeholder.empty()
                st.session_state["image_analyzed"] = True

if "image_analyzed" in st.session_state:
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

if "chat_history" in st.session_state:
    for message in st.session_state["chat_history"]:
        if message["role"] == "user": 
            message_user = st.chat_message('user')
            message_user.write(f"**Vous** : {message['content']}")
        elif message["role"] == "assistant":
            response_typing(message['content'])
