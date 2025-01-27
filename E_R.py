import google.generativeai as genai
import streamlit as st
import time
import db_manager

st.title("EtudIAnt : Créateur de fiche de révision📝")

genai.configure(api_key=st.secrets["API_KEY"])

if "chat_add" not in st.session_state:
    st.session_state["chat_add"] = []
if "response_ai_revision" not in st.session_state:
    st.session_state["response_ai_revision"] = None
if "last_prompt" not in st.session_state:
    st.session_state["last_prompt"] = None

model = genai.GenerativeModel("gemini-1.5-flash-002")

st.subheader("Sur quoi veux-tu créer une fiche de révision ?")

level = st.selectbox("Sélectionne ton niveau : ", ["6ème","5ème","4ème","3ème","Seconde","Premiere","Terminale"], key="level")
subject = st.selectbox("Sélectionne la matière de ta fiche de révision:", ["Français", "Mathématiques", "Histoire-Géographie-EMC", "Sciences et Vie de la Terre", "Physique Chimie", "Anglais","Allemand", "Espagnol"], key="subject")
prompt = f"Crée une fiche de revision le plus précisement possible. La fiche de revision doit être au niveau :{level}. Adapte la fiche de révision en fonction du niveau. Cette fiche de revision est sur la matière: {subject}.En parlant en francais, jamais en anglais"
prompt_user = st.chat_input("ex : sur la seconde guerre mondiale.")

if prompt_user:
    if "created" not in st.session_state:
        if db_manager.can_user_make_request():
            st.session_state["last_prompt"] = prompt_user
            with st.spinner("L'EtudIAnt reflechit..."):
                response_ai = model.generate_content([prompt_user, prompt])
                response_ai_user = response_ai.text
                st.session_state["response_ai_revision"] = response_ai.text
                st.session_state["chat_add"].append({"role":"assistant", "content":response_ai_user})
                if response_ai_user:
                    time.sleep(2)
                    st.session_state["created"] = True
        st.error("Votre quotas de requêtes par jour est terminé, revenez demain pour utiliser l'EtudIAnt.")

if "created" in st.session_state:
    if prompt_user and prompt_user != st.session_state["last_prompt"]:
        history_chat = []
        if db_manager.can_user_make_request():
            prompt_chat = "Répond à cette question en francais. La fiche de revision est de niveau :" + level +"adapte tes reponses au niveau."+"La matière est :"+subject+"Adapte tes reponses à la matière" + "Adapte toi au programme scolaire de l'Education Nationale en France. Si ce n'est pas possible, ne le fais pas et n'en dit rien."
            st.session_state["chat_add"].append({"role":"user", "content":prompt_user})
            history_chat.append({"role":"model", "parts":st.session_state["response_ai_revision"]})
            chat = model.start_chat(history=history_chat)
            response_chat = chat.send_message([prompt_user, prompt_chat])
            st.session_state["chat_add"].append({"role":"assistant", "content":response_chat.text})
            history_chat.append({"role":"user", "parts":prompt_user})
            history_chat.append({"role":"model", "parts":response_chat.text})
            st.session_state["last_prompt"] = prompt_user

        
if "chat_add" in st.session_state:
    for message in st.session_state["chat_add"]:
        if message["role"] == "user":
            message_user = st.chat_message('user')
            message_user.write(f"**Vous** : {message['content']}")
        elif message["role"] == "assistant":
            message_ai = st.chat_message('assistant')
            message_ai.write(f"**IA** : {message['content']}")

        
    


