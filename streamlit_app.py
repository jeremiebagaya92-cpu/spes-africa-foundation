import streamlit as st
from datetime import datetime
import json, os

st.set_page_config(page_title="SPES Africa Groupe", page_icon="💬", layout="wide")

# Dossiers
os.makedirs("uploads", exist_ok=True)
os.makedirs("avatars", exist_ok=True)
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

# --- PHOTO ONG (tu changeras après) ---
st.image("https://cdn-icons-png.flaticon.com/512/2345/2345532.png", width=100)
st.title("SPES Africa Foundation - Groupe Privé")
st.caption("Solidarité, Paix, Education - Bukavu/Goma")

# --- LOGIN AVEC PHOTO OBLIGATOIRE ---
if "nom" not in st.session_state:
    st.subheader("🔐 Connexion membre")
    st.info("Chaque membre doit mettre sa photo pour entrer")
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Ton nom complet")
        code = st.text_input("Code ONG", type="password")
    with col2:
        photo_profil = st.file_uploader("Ta photo de profil (obligatoire)", type=["jpg","png","jpeg"])
    
    if st.button("Rejoindre le groupe"):
        if not nom or not photo_profil or not code:
            st.error("Remplis tout : Nom + Photo + Code")
        elif code not in ["SPES2026", "SPESADMIN2026"]:
            st.error("Code incorrect")
        else:
            # Sauver avatar
            avatar_path = f"avatars/{nom}.jpg"
            with open(avatar_path, "wb") as f:
                f.write(photo_profil.getbuffer())
            
            st.session_state.nom = nom
            st.session_state.avatar = avatar_path
            st.session_state.is_admin = (code == "SPESADMIN2026")
            st.rerun()
    st.stop()

# Sidebar profil
st.sidebar.image(st.session_state.avatar, width=150)
st.sidebar.write(f"**{st.session_state.nom}**")
if st.session_state.is_admin:
    st.sidebar.success("👑 ADMIN")
if st.sidebar.button("Quitter"):
    del st.session_state.nom
    st.rerun()

# --- TABS ---
tab_chat, tab_infos = st.tabs(["💬 Groupe de Discussion", "📢 Infos Officielles (Admin)"])

# TAB CHAT - COMME WHATSAPP
with tab_chat:
    messages = charger(FICHIER_CHAT)
    
    # Afficher messages
    for m in messages[-100:]:
        c1, c2 = st.columns([1, 10])
        avatar = f"avatars/{m['nom']}.jpg"
        if os.path.exists(avatar):
            c1.image(avatar, width=50)
        else:
            c1.write("👤")
        
        with c2:
            st.markdown(f"**{m['nom']}** - {m['heure']}")
            if m.get("texte"):
                st.write(m["texte"])
            if m.get("fichier"):
                fp = m["fichier"]
                if fp.endswith((".jpg",".png",".jpeg")):
                    st.image(fp, width=300)
                elif fp.endswith((".mp3",".wav",".m4a",".ogg")):
                    st.audio(fp)
                else:
                    with open(fp, "rb") as f:
                        st.download_button(f"📥 Télécharger {os.path.basename(fp)}", f, file_name=os.path.basename(fp), key=fp+str(m['heure']))
            st.divider()

    # Envoyer
    st.subheader("Envoyer")
    msg = st.text_area("Message")
    fichier = st.file_uploader("Photo, Audio ou Fichier", type=["jpg","png","jpeg","mp3","wav","m4a","pdf","docx","mp4"])
    
    if st.button("📤 Envoyer"):
        if not msg and not fichier:
            st.warning("Écris un message ou choisis un fichier")
        else:
            fichier_path = None
            if fichier:
                fichier_path = f"uploads/{datetime.now().strftime('%H%M%S')}_{fichier.name}"
                with open(fichier_path, "wb") as f:
                    f.write(fichier.getbuffer())
            
            messages.append({
                "nom": st.session_state.nom,
                "texte": msg,
                "fichier": fichier_path,
                "heure": datetime.now().strftime("%d/%m %H:%M")
            })
            sauver(FICHIER_CHAT, messages)
            st.rerun()

# TAB INFOS - SEUL ADMIN
with tab_infos:
    st.header("📢 Informations Importantes de la Direction")
    infos = charger(FICHIER_INFOS)
    
    for info in reversed(infos):
        st.success(f"**{info['titre']}** par {info['auteur']} - {info['heure']}\n\n{info['texte']}")
        if info.get("fichier"):
            st.image(info["fichier"]) if info["fichier"].endswith((".jpg",".png")) else st.write(f"Fichier: {info['fichier']}")
    
    if st.session_state.is_admin:
        st.divider()
        st.subheader("👑 Publier (Admin seulement)")
        t = st.text_input("Titre de l'annonce")
        c = st.text_area("Message officiel")
        f_info = st.file_uploader("Photo de l'info", type=["jpg","png"], key="info")
        if st.button("Publier l'info officielle"):
            fp = None
            if f_info:
                fp = f"uploads/info_{datetime.now().strftime('%H%M%S')}_{f_info.name}"
                with open(fp, "wb") as f:
                    f.write(f_info.getbuffer())
            infos.append({"titre": t, "texte": c, "fichier": fp, "auteur": st.session_state.nom, "heure": datetime.now().strftime("%d/%m %H:%M")})
            sauver(FICHIER_INFOS, infos)
            st.success("Info publiée !")
            st.rerun()
    else:
        st.info("Seul l'admin peut publier ici. Tu peux seulement lire.")
