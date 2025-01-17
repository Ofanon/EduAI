import google.generativeai as genai
import streamlit as st
import time

st.title("EtudIAnt : fiche de révision")

if "api_key" in st.session_state:
    genai.configure(api_key=st.session_state["api_key"])

if "chat_add" not in st.session_state:
    st.session_state["chat_add"] = []

else:
    st.error("Clée API non enregistrée, veuillez vous rendre dans l'onglet 'Configuration de la clée API' pour l'enregistrer.")

model = genai.GenerativeModel("gemini-1.5-flash-002")

st.subheader("Sur quoi veux-tu créer une fiche de révision ?")
prompt = "Crée une fiche de revision le plus précisement possible, en parlant en francais, jamais en anglais"
prompt_user = st.chat_input("ex : sur la seconde guerre mondiale")

if "created" not in st.session_state:
    if prompt_user:
        time.sleep(3)
        with st.spinner("L'EtudIAnt reflechit..."):
            response = model.generate_content([prompt_user, prompt])
            st.session_state["chat_add"].append["role":"assistant", "content":response.text]
            st.session_state["created"] = True
history = []

if "created" in st.session_state:
    if prompt_user:
        history.append[{"role":"model", "parts":response.text}]
        chat = model.start_chat(history=history)
        response = chat.send_message([prompt_user])
        st.session_state["chat_add"].append["role":"user", "content":prompt_user]
        st.session_state["chat_add"].append["role":"assistant", "content":response.text]
        history.append({"role":"user", "parts":prompt_user})
        history.append({"role":"model", "parts":response.text})

if "chat_add" in st.session_state:
    for message in st.session_state["chat_add"]:
        if message['role'] == "user":
            message_user = st.chat_message('user')
            message_user.write(f"**Vous** : {message['content']}")
        elif message['role'] == "assistant":
            message_ai = st.chat_message('user')
            message_ai.write(f"**Vous** : {message['content']}")
        
    


