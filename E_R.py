import google.generativeai as genai
import streamlit as st
import time

st.title("EtudIAnt : fiche de révision")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])
else:
    st.error("Clée API non enregistrée, veuillez vous rendre dans l'onglet 'Configuration de la clée API' pour l'enregistrer.")

if "chat_add" not in st.session_state:
    st.session_state["chat_add"] = []
if "response_ai_revision" not in st.session_state:
    st.session_state["response_ai_revision"] = None

model = genai.GenerativeModel("gemini-1.5-flash-002")

st.subheader("Sur quoi veux-tu créer une fiche de révision ?")
prompt = "Crée une fiche de revision le plus précisement possible. En parlant francais, jamais en anglais"

if "created" not in st.session_state:
    prompt_user = st.chat_input("ex : sur la seconde guerre mondiale")
    if prompt_user:
        time.sleep(3)
        with st.spinner("L'EtudIAnt reflechit..."):
            response_ai = model.generate_content([prompt_user, prompt])
            response_ai_user = response_ai.text
        st.session_state["response_ai_revision"] = response_ai.text
        st.session_state["chat_add"].append({"role":"assistant", "content":response_ai_user})
        st.session_state["created"] = True


if "created" in st.session_state:
    history = []
    prompt_user = st.chat_input("ex : rajoute l'entre deux guerres")
    if prompt_user:
        prompt_chat = "Répond à cette question en francais."
        st.session_state["chat_add"].append({"role":"user", "content":prompt_user})
        history.append({"role":"model", "parts":st.session_state["response_ai_revision"]})
        chat = model.start_chat(history=history)
        response_chat = chat.send_message([prompt_user, prompt_chat])
        st.session_state["chat_add"].append({"role":"assistant", "content":response_chat.text})
        history.append({"role":"user", "parts":prompt_user})
        history.append({"role":"model", "parts":response_chat.text})
        
if "chat_add" in st.session_state:
    for message in st.session_state["chat_add"]:
        if message["role"] == "user":
            message_user = st.chat_message('user')
            message_user.write(f"**Vous** : {message['content']}")
        elif message["role"] == "assistant":
            message_ai = st.chat_message('assistant')
            message_ai.write(f"**AI** : {message['content']}")
        
    


