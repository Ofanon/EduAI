import streamlit as st
from streamlit_lottie import st_lottie
import db_manager as db
import sqlite3
import streamlit as st
import db_manager
import streamlit as st
import db_manager

import streamlit as st

st.title("Bienvenue sur EtudIAnt 🚀")

# 📌 JavaScript pour stocker le `user_id` dans le navigateur (localStorage)
st.markdown("""
<script>
    function getOrCreateUserId() {
        let userId = localStorage.getItem("user_id");
        if (!userId) {
            userId = crypto.randomUUID();  // ✅ Générer un UUID unique
            localStorage.setItem("user_id", userId);
        }
        return userId;
    }
    const userId = getOrCreateUserId();
    document.write(`<p style="font-size:18px">✅ Votre user_id : <strong>${userId}</strong></p>`);
</script>
""", unsafe_allow_html=True)


with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

