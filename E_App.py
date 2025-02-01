import streamlit as st
from streamlit_lottie import st_lottie
import db_manager as db
import sqlite3

# Injecter du JavaScript pour utiliser `localStorage`
st.markdown("""
<script>
    // Récupérer l'user_id depuis localStorage
    let user_id = localStorage.getItem("user_id");

    // Si l'ID n'est pas stocké localement, générer un nouvel ID côté serveur
    if (!user_id) {
        user_id = "{user_id}";
        localStorage.setItem("user_id", user_id);
    }

    // Vérifier si l'URL contient l'user_id, sinon l'ajouter
    const params = new URLSearchParams(window.location.search);
    if (!params.get("user_id")) {
        params.set("user_id", user_id);
        window.location.search = params.toString();
    }
</script>
""".replace("{user_id}", db.get_user_id()), unsafe_allow_html=True)

user_id = db.get_user_id()
st.session_state["user_id"] = user_id


st.write(db.get_user_id())
with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

