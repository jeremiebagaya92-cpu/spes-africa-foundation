import streamlit as st
from datetime import datetime
import json, os, random

st.set_page_config(page_title="SPES Africa", page_icon="💬", layout="centered")
os.makedirs("uploads", exist_ok=True)
os.makedirs("avatars", exist_ok=True)

CHAT = "chat.json"
MEMBRES = "membres.json"
INFOS = "infos.json"
LOGO = "logo_ong.jpg"

def charger(f):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as j: return json.load(j)
        except: return []
    return []
def sauver(f,d):
    with open(f,"w",encoding="utf-8") as j: json.dump(d,j,ensure_ascii=False)

# --- BIENVENUE ---
if os.path.exists(LOGO):
    st.image(LOGO, width=200)
else:
    st.image("https://cdn-icons-png.flaticon.com/512/2345/2345532.png", width=90)

st.markdown("<h2 style='text-align:center'>Bienvenue chez<br>SPES Africa Foundation</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center'>Groupe WhatsApp privé des membres</p>", unsafe_allow_html=True)
st.divider()

# --- FORMULAIRE WHATSAPP ---
if "nom" not in st.session_state:
    st.subheader("🔐 Entrer dans le groupe")
    
    nom = st.text_input("Nom *")
    postnom = st.text_input("Post-nom *")
    prenom = st.text_input("Prénom *")
    fonction = st.text_input("Fonction / Poste *", placeholder="Ex: Comptable")
    
    st.write("Ta photo de profil *")
    # 2 façons pour que ça marche toujours
    photo_file = st.file_uploader("Choisis dans ta Galerie", type=["jpg","jpeg","png"], key="galerie")
    photo_cam = st.camera_input("Ou prends une photo directe")
    
    code = st.text_input("Code ONG *", type="password", placeholder="Code secret donné par l'admin")

    if st.button("Rejoindre le groupe 💬", type="primary", use_container_width=True):
        la_photo = photo_file or photo_cam
        
        if not nom or not postnom or not prenom or not fonction:
            st.error("Remplis Nom, Post-nom, Prénom, Fonction")
        elif la_photo is None:
            st.error("❌ Mets ta photo : clique sur 'Choisis dans ta Galerie' ou prends une photo")
        elif not code:
            st.error("Mets le Code ONG")
        elif code not in ["SPES2026", "SPESADMIN2026"]:
            st.error("Code incorrect")
        else:
            nom_complet = f"{nom} {postnom} {prenom}"
            chemin = f"avatars/{nom}_{prenom}.jpg"
            with open(chemin, "wb") as f:
                f.write(la_photo.getbuffer())
            
            # Sauver membre
            membres = charger(MEMBRES)
            membres.append({"nom_complet":nom_complet, "fonction":fonction, "date":datetime.now().strftime("%d/%m/%Y")})
            sauver(MEMBRES, membres)
            
            st.session_state.nom = nom_complet
            st.session_state.fonction = fonction
            st.session_state.avatar = chemin
            st.session_state.is_admin = (code == "SPESADMIN2026")
            st.rerun()
    st.stop()

# --- APRÈS CONNEXION - COMME WHATSAPP ---
with st.sidebar:
    st.image(st.session_state.avatar, width=100)
    st.write(f"**{st.session_state.nom}**")
    st.caption(st.session_state.fonction)
    if st.session_state.is_admin:
        st.success("👑 ADMIN")
        up_logo = st.file_uploader("Changer logo ONG", type=["jpg","png"], key="logo")
        if up_logo:
            with open(LOGO, "wb") as f: f.write(up_logo.getbuffer())
            st.rerun()
    if st.button("Quitter"):
        del st.session_state.nom
        st.rerun()

# Style WhatsApp
st.markdown("""
<style>
.bulle {background:#202c33; padding:8px 12px; border-radius:0px 8px 8px 8px; margin:6px 0; color:white; max-width:85%}
.bulle-moi {background:#005c4b; margin-left:auto; border-radius:8px 0px 8px 8px}
</style>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬 Discussion", "📢 Infos Officielles"])

with tab1:
    messages = charger(CHAT)
    for m in messages[-100:]:
        avatar = f"avatars/{m['nom'].split()[0]}_{m['nom'].split()[-1]}.jpg"
        # fallback
        if not os.path.exists(avatar):
            avatar = f"avatars/{m['nom'].replace(' ','_')}.jpg"
            if not os.path.exists(avatar):
                avatar = st.session_state.avatar
        
        col1, col2 = st.columns([1,9])
        if os.path.exists(avatar):
            col1.image(avatar, width=38)
        else:
            col1.write("👤")
        
        with col2:
            is_me = m["nom"] == st.session_state.nom
            css = "bulle bulle-moi" if is_me else "bulle"
            html = f'<div class="{css}"><b style="color:#53bdeb; font-size:13px">{m["nom"]}</b><br>{m.get("texte","")}'
            if m.get("fichier") and os.path.exists(m["fichier"]):
                fp = m["fichier"]
                if fp.endswith((".jpg",".png",".jpeg")):
                    html += f'<br><img src="" />'  # on affichera en dessous
                html += f'<div style="font-size:11px; color:#8696a0; text-align:right">{m["heure"]}</div></div>'
            st.markdown(html, unsafe_allow_html=True)
            if m.get("fichier") and os.path.exists(m["fichier"]):
                fp = m["fichier"]
                if fp.lower().endswith((".jpg",".jpeg",".png")):
                    st.image(fp, width=250)
                elif fp.lower().endswith((".mp3",".wav",".m4a",".ogg","wav")):
                    st.audio(fp)
                else:
                    with open(fp, "rb") as f:
                        st.download_button(f"📎 {os.path.basename(fp)}", f, key=fp+m["heure"]+str(random.random()))

    st.divider()
    st.write("**Envoyer comme WhatsApp :**")
    texte = st.text_input("Message", placeholder="Message", label_visibility="collapsed", key="msg")
    
    c1, c2 = st.columns(2)
    with c1:
        fichier = st.file_uploader("📷 Photo / 📎 Fichier", type=["jpg","jpeg","png","pdf","docx","mp4"], key="f1", label_visibility="collapsed")
    with c2:
        audio = st.audio_input("🎙️ Vocal", label_visibility="collapsed")
    
    if st.button("➤ Envoyer", use_container_width=True):
        fpath = None
        up = fichier or audio
        if up:
            nom_f = getattr(up, 'name', 'vocal.wav')
            if audio: nom_f = f"vocal_{datetime.now().strftime('%H%M%S')}.wav"
            fpath = f"uploads/{datetime.now().strftime('%H%M%S')}_{nom_f}"
            with open(fpath, "wb") as f: f.write(up.getbuffer())
        
        if texte or fpath:
            messages.append({"nom":st.session_state.nom, "texte":texte, "fichier":fpath, "heure":datetime.now().strftime("%H:%M")})
            sauver(CHAT, messages)
            st.rerun()

with tab2:
    st.subheader("📌 Infos épinglées par la direction")
    for i in reversed(charger(INFOS)):
        st.success(f"**{i['titre']}** - {i['auteur']} {i['heure']}\n\n{i['texte']}")
        if i.get("fichier") and os.path.exists(i["fichier"]):
            st.image(i["fichier"], width=300)
    if st.session_state.is_admin:
        st.divider()
        t = st.text_input("Titre")
        c = st.text_area("Message officiel")
        fi = st.file_uploader("Photo", type=["jpg","png"], key="info")
        if st.button("Épingler"):
            fp = None
            if fi:
                fp = f"uploads/INFO_{fi.name}"
                with open(fp, "wb") as f: f.write(fi.getbuffer())
            infos = charger(INFOS)
            infos.append({"titre":t, "texte":c, "fichier":fp, "auteur":st.session_state.nom, "heure":datetime.now().strftime("%d/%m %H:%M")})
            sauver(INFOS, infos)
            st.rerun()
