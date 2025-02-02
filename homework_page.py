import PIL.Image
import google.generativeai as genai
import PIL
import streamlit as st
import user_manager as db

st.title("EtudIAnt : 📚 Aide au devoirs")
genai.configure(api_key=st.secrets["API_KEY"])

model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")

with st.spinner("La page est en cours de chargement..."):
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        st.session_state["response_ai"] = None
        st.session_state["uploaded_file"] = None
        st.session_state["st_image"] = None
        st.session_state["image_pil"] = None
        st.session_state["message"] = []
        st.session_state["started"] = False

if st.session_state.started is not True:
    st.write("**Prix : ⭐ 1 étoile**")
    uploaded_file = st.file_uploader("📥 Télécharger une image", type=["png", "jpeg", "jpg", "bmp"])
    st.session_state["uploaded_file"] = uploaded_file
    placeholder_button = st.empty()

if "image_analyzed" in st.session_state:
    if st.button("✨ Résoudre un autre devoir"):
        del st.session_state.chat_history
        del st.session_state.image_analyzed
        uploaded_file = None
        st.rerun()

if uploaded_file:
    if placeholder_button.button(" ✨ Résoudre le devoir"):
        image = PIL.Image.open(uploaded_file)
        image.resize((512, 512))
        st.session_state["st_image"] = image
        if db.can_user_make_request():
            if "image_analyzed" not in st.session_state:
                st.image(st.session_state.st_image, use_container_width=True)
                prompt = "Répond à cette exercice le plus précisement possible. En parlant en francais, jamais en anglais"
                with st.spinner("L'EtudIAnt reflechit..."):
                    response_ai = model.generate_content([prompt, image])
                    st.session_state["response_ai"] = response_ai.text
                st.session_state["chat_history"].append({"role":"assistant","content":response_ai.text})
                st.session_state.image_analyzed = True
                db.consume_request()
                db.update_experience_points(points=20)
                st.rerun()
        else:
            st.session_state["chat_history"].append({"role": "assistant", "content" : "Votre quotas de requêtes par jour est terminé, revenez demain pour utiliser l'EtudIAnt."})

if "image_analyzed" in st.session_state:
    placeholder_button.empty()
    history = []
    user_input = st.chat_input("ex : je n'ai pas compris ta réponse dans l'exercice B")
    st.image(st.session_state.st_image, use_container_width=True)
    if user_input:
        if db.can_user_make_request():
            st.session_state["chat_history"].append({"role":"user","content":user_input})
            history.append({"role":"model", "parts":st.session_state.response_ai})
            chat = model.start_chat(history = history)
            response = chat.send_message(user_input)
            db.consume_request()
            db.update_experience_points(points=30)
            st.session_state["chat_history"].append({"role":"assistant","content":response.text})
            history.append({"role":"user", "parts":user_input})
            history.append({"role":"model", "parts":response.text})
        else:
                st.error("Votre quotas de requêtes par jour est terminé, revenez demain pour utiliser l'EtudIAnt.")
if "chat_history" in st.session_state:
    for message in st.session_state["chat_history"]:
            if message["role"] == "user": 
                with st.chat_message('user'):
                    st.write(f"**Vous** : {message['content']}")
            elif message["role"] == "assistant":
                with st.chat_message('assistant'):
                    st.markdown(f"**IA** : {message['content']}")
