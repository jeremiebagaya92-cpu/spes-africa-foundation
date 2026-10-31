import streamlit as st
from datetime import datetime
import json
import os

st.set_page_config(page_title="SPES Africa - Discussions", page_icon="💬")

# Fichiers pour sauvegarder
FICHIER_CHAT = "chat.json"
FICHIER_INFOS = "infos.json"

def charger(fichier):
    if os.path.exists(fichier):
        with open(fichier, "r") as f:
            return json.load(f)
    return []

def sauver(fichier, data):
    with open(fichier, "w") as f:
        json.dump(data, f)

# --- LOGIN SIMPLE ---
st.title("💬 SPES Africa Foundation")
st.write("Espace membres - Discussions")

if "nom" not in st.session_state:
    st.subheader("Connexion membre")
    nom = st.text_input("Ton nom")
    code = st.text_input("Code ONG", type="password")
    if st.button("Entrer"):
        if code == "SPES2026":  # Code secret pour les membres
            st.session_state.nom = nom
            st.rerun()
        else:
            st.error("Code incorrect. Demande le code à l'admin.")
    st.stop()

st.sidebar.write(f"Connecté: **{st.session_state.nom}**")
if st.sidebar.button("Déconnexion"):
    del st.session_state.nom
    st.rerun()

# --- 2 ONGLETS SEULEMENT ---
tab1, tab2 = st.tabs(["💬 Discussions", "📢 Infos Importantes"])

# TAB 1 : DISCUSSIONS
with tab1:
    st.header("Discussions des membres")
    messages = charger(FICHIER_CHAT)
    
    for m in messages[-50:]:  # 50 derniers messages
        st.write(f"**{m['nom']}** ({m['heure']}) : {m['texte']}")
    
    st.divider()
    nouveau = st.text_input("Ton message", key="msg")
    if st.button("Envoyer message"):
        if nouveau:
            messages.append({
                "nom": st.session_state.nom,
                "texte": nouveau,
                "heure": datetime.now().strftime("%d/%m %H:%M")
            })
            sauver(FICHIER_CHAT, messages)
            st.rerun()

# TAB 2 : INFOS IMPORTANTES
with tab2:
    st.header("📢 Informations importantes")
    infos = charger(FICHIER_INFOS)
    
    for info in reversed(infos):
        st.info(f"**{info['titre']}** - {info['heure']}\n\n{info['texte']}")
    
    st.divider()
    st.subheader("Publier une info importante")
    titre = st.text_input("Titre de l'info")
    texte = st.text_area("Contenu de l'info")
    if st.button("Publier l'info"):
        if titre and texte:
            infos.append({
                "titre": titre,
                "texte": texte,
                "auteur": st.session_state.nom,
                "heure": datetime.now().strftime("%d/%m %H:%M")
            })
            sauver(FICHIER_INFOS, infos)
            st.rerun()
