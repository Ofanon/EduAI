import streamlit as st
import user_manager as db

experience_points = db.get_experience_points()

st.title("🌟 Boutique de l'EtudIAnt 🌟")
st.subheader(f"💎 Vous avez **{experience_points}** points d'expérience.")

st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    with st.container(key=1):
        st.image("5_Stars.png", use_container_width=True)
        st.write("⭐ Acheter 5 étoiles")
        if st.button("🎁 **Prix** : 💎 **300** points d'expérience", key="buy_5"):
            success = db.purchase_requests(cost_in_experience=300, requests_to_add=5)
            if success is True:
                st.success("✨ 5 étoiles ajoutées !")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Pas assez de points.")

with col2:
    with st.container(key=2):
        st.image("10_Stars.png", use_container_width=True)
        st.write("⭐⭐ Acheter 10 étoiles")
        if st.button("🎁 **Prix** : 💎 **1000** points d'expérience", key="buy_10"):
            success = db.purchase_requests(cost_in_experience=1000, requests_to_add=10)
            if success is True:
                st.success("✨ 10 étoiles ajoutées !")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Pas assez de points.")

with col3:
    with st.container(key=3):
        st.image("20_Stars.png", use_container_width=True)
        st.write("⭐⭐⭐ Acheter 20 étoiles")
        if st.button("🎁 **Prix** : 💎 **3800** points d'expérience", key="buy_20"):
            success = db.purchase_requests(cost_in_experience=3800, requests_to_add=20)
            if success is True:
                st.success("✨ 20 étoiles ajoutées !")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Pas assez de points.")

st.markdown("---")

total_requests = db.get_requests_left()
st.write(f"🌟 **Étoiles restantes** : {total_requests}")
