import streamlit as st
import db_manager as db

st.title("Bienvenue sur EtudIAnt 🚀")

# 📌 JavaScript pour stocker le `device_id` dans le navigateur (localStorage)
st.markdown("""
<script>
    function getOrCreateDeviceId() {
        let deviceId = localStorage.getItem("device_id");
        if (!deviceId) {
            deviceId = crypto.randomUUID();  // ✅ Générer un UUID unique
            localStorage.setItem("device_id", deviceId);
        }
        return deviceId;
    }
    const deviceId = getOrCreateDeviceId();
    document.write(`<p style="font-size:18px">✅ Votre device_id : <strong>${deviceId}</strong></p>`);

    // Envoyer le device_id à Streamlit
    window.parent.postMessage({type: "device_id", value: deviceId}, "*");
</script>
""", unsafe_allow_html=True)

# ✅ Récupérer le `device_id` envoyé par le navigateur
device_id = st.session_state.get("device_id", None)

if device_id is None:
    device_id = st.experimental_get_query_params().get("device_id", [None])[0]

if device_id:
    st.session_state["device_id"] = device_id
    user_id = db.get_or_create_user_id(device_id)
    st.write(f"✅ Votre user_id : `{user_id}`")

with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

