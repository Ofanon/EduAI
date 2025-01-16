import google.generativeai as genai
import PIL.Image
import streamlit as st
import E_API_Key


st.title("EtudIAnt : Aide aux devoirs")

genai.configure(api_key=st.session_state["api_key"])

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"]=[]
if "response_ai" not in st.session_state:
    st.session_state["response_ai"] = None

uploaded_file = st.file_uploader("Télécharger une image", type=["png", "jpeg", "jpg", "bmp"])

if uploaded_file:

    image = PIL.Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    if "image_analyzed" not in st.session_state:
        st.write("Analyse en cours...")
        prompt = "Répond à cette exercice le plus précisement possible"
        response_ai = model.generate_content([prompt, image])
        response_ai_user = response_ai.text
        st.session_state["response_ai"] = response_ai_user
        st.session_state["chat_history"].append({"role":"assistant","content":response_ai.text})
        st.session_state["image_analyzed"] = True

if "image_analyzed" in st.session_state:
    user_input = st.chat_input("ex : je n'ai pas compris ta réponse dans l'exercice B")
    if user_input:
        history = []
        history.append({"role":"model", "parts":st.session_state["response_ai"]})
        st.session_state["chat_history"].append({"role":"user","content":user_input})
        chat = model.start_chat(history = history)
        response = chat.send_message(user_input)
        st.session_state["chat_history"].append({"role":"assistant","content":response.text})
        history.append({"role":"user", "parts":user_input})
        history.append({"role":"model", "parts":response.text})

if "chat_history" in st.session_state:
    for message in st.session_state["chat_history"]:
        if message["role"] == "user":
            st.chat_message(f"**Vous** : {message['content']}", avatar="user")
        elif message["role"] == "assistant":
            st.chat_message(f"**IA** : {message['content']}", avatar="assistant")
