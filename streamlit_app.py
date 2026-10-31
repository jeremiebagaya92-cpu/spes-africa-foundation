import streamlit as st

st.set_page_config(page_title="SPES Africa Foundation", page_icon="🌍")

st.title("🌍 SPES Africa Foundation")
st.write("Goma, RDC - Solidarite, Paix, Education")

menu = st.sidebar.selectbox("MENU", ["Accueil", "Membres", "Projets", "Contact"])

if menu == "Accueil":
    st.success("Bienvenue chez SPES Africa !")
    st.metric("Membres", "25")
    st.metric("Projets", "5")
    
elif menu == "Membres":
    st.header("Nos Membres")
    st.write("Ici tu mettras la liste de tes membres de Goma")
    
elif menu == "Projets":
    st.header("Nos Projets")
    st.write("Projets a Goma - Aide humanitaire, Education")
    
elif menu == "Contact":
    st.header("Contactez-nous")
    st.write("📍 Goma, Nord-Kivu, RDC")
    st.write("Mets ton email et telephone ici")
