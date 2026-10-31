import streamlit as st
from datetime import datetime
import json, os, random

st.set_page_config(page_title="SPES Africa Foundation", page_icon="💙")
os.makedirs("uploads", exist_ok=True)
os.makedirs("avatars", exist_ok=True)

FICHIER_CHAT = "chat.json"
FICHIER_INFOS = "infos.json"
FICHIER_MEMBRES = "membres.json"
LOGO = "logo_ong.jpg"

def charger(f):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as x: return json.load(x)
        except: return []
    return []
def sauver(f,d):
    with open(f,"w",encoding="utf-8") as x: json.dump(d,x,ensure_ascii=False)

# --- ECRAN BIENVENUE AVEC LOGO ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists(LOGO):
        st.image(LOGO, width=200)
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/2345/2345532.png", width=150)

st.markdown("<h1 style='text-align:center; color:#0a4a7a;'>Bienvenue chez</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#0a4a7a;'>SPES Africa Foundation</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Solidarité, Paix, Education et Santé<br>Groupe privé des membres - Bukavu / Goma</p>", unsafe_allow_html=True)
st.divider()

# --- FORMULAIRE ---
if "nom" not in st.session_state:
    st.subheader("🔐 Inscription pour entrer")
    
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nom *")
        prenom = st.text_input("Prénom *")
        poste = st.text_input("Poste *", placeholder="Ex: Coordinateur")
    with c2:
        telephone = st.text_input("Téléphone *", placeholder="+243...")
        photo = st.file_uploader("Ta photo *", type=["jpg","jpeg","png","webp"])
        code = st.text_input("Code ONG *", type="password", placeholder="SPES2026")
    
    if st.button("Rejoindre le groupe 💬", use_container_width=True, type="primary"):
        if not nom or not prenom or not poste or not telephone or photo is None or not code:
            st.error("❌ Remplis tout : Nom, Prénom, Poste, Téléphone, Photo, Code")
        elif code not in ["SPES2026","SPESADMIN2026"]:
            st.error("Code faux")
        else:
            nom_complet = f"{nom} {prenom}"
            path = f"avatars/{nom_complet.replace(' ','_')}.jpg"
            with open(path, "wb") as f:
                f.write(photo.getbuffer())
            
            membres = charger(FICHIER_MEMBRES)
            membres.append({"nom_complet":nom_complet,"poste":poste,"telephone":telephone,"date":datetime.now().strftime("%d/%m/%Y")})
            sauver(FICHIER_MEMBRES, membres)
            
            st.session_state.nom = nom_complet
            st.session_state.poste = poste
            st.session_state.telephone = telephone
            st.session_state.avatar = path
            st.session_state.is_admin = (code=="SPESADMIN2026")
            
            msgs = charger(FICHIER_CHAT)
            msgs.append({"nom":"SYSTEME","texte":f"👋 {nom_complet} ({poste}) a rejoint","heure":datetime.now().strftime("%H:%M"),"type":"system"})
            sauver(FICHIER_CHAT, msgs)
            st.rerun()
    st.stop()

# --- APRES CONNEXION ---
with st.sidebar:
    if os.path.exists(st.session_state.avatar):
        st.image(st.session_state.avatar, width=100)
    st.write(f"**{st.session_state.nom}**")
    st.caption(st.session_state.poste)
    if st.session_state.is_admin:
        st.success("👑 ADMIN")
        logo_up = st.file_uploader("Changer le logo ONG ici", type=["jpg","png","jpeg"], key="logo")
        if logo_up:
            with open(LOGO, "wb") as f:
                f.write(logo_up.getbuffer())
            st.success("Logo changé ! Actualise")
            st.rerun()
    if st.button("Quitter"):
        del st.session_state.nom
        st.rerun()

tab_chat, tab_infos = st.tabs(["💬 Groupe", "📢 Infos Officielles"])

with tab_chat:
    for m in charger(FICHIER_CHAT)[-100:]:
        if m.get("type")=="system":
            st.markdown(f"<center style='color:gray; font-size:12px; background:#e8f4f8; padding:6px; border-radius:8px; margin:6px'>{m['texte']}</center>", unsafe_allow_html=True)
            continue
        c1,c2 = st.columns([1,9])
        ap = f"avatars/{m['nom'].replace(' ','_')}.jpg"
        if os.path.exists(ap): c1.image(ap, width=40)
        else: c1.write("👤")
        with c2:
            with st.container(border=True):
                st.markdown(f"**{m['nom']}** <small>{m['heure']}</small>", unsafe_allow_html=True)
                if m.get("texte"): st.write(m["texte"])
                if m.get("fichier") and os.path.exists(m["fichier"]):
                    fp=m["fichier"]
                    if fp.lower().endswith((".jpg",".png",".jpeg")): st.image(fp,width=300)
                    elif fp.lower().endswith((".mp3",".wav",".m4a",".ogg")): st.audio(fp)
                    else:
                        with open(fp,"rb") as f:
                            st.download_button(f"📥 {os.path.basename(fp)}",f,key=fp+m['heure']+str(random.random()))
    st.divider()
    txt = st.text_input("Message")
    file = st.file_uploader("📷 Photo, 🎤 Audio, 📎 Fichier", type=["jpg","png","jpeg","mp3","wav","m4a","pdf","docx","mp4"])
    vocal = st.audio_input("🎙️ Vocal")
    if st.button("Envoyer ➤", use_container_width=True):
        fpath=None
        up=file or vocal
        if up:
            name=getattr(up,'name','vocal.wav')
            if vocal: name=f"vocal_{datetime.now().strftime('%H%M%S')}.wav"
            fpath=f"uploads/{datetime.now().strftime('%H%M%S')}_{name}"
            with open(fpath,"wb") as f: f.write(up.getbuffer())
        if txt or fpath:
            msgs=charger(FICHIER_CHAT)
            msgs.append({"nom":st.session_state.nom,"texte":txt,"fichier":fpath,"heure":datetime.now().strftime("%H:%M")})
            sauver(FICHIER_CHAT, msgs)
            st.rerun()

with tab_infos:
    for info in reversed(charger(FICHIER_INFOS)):
        st.success(f"**{info['titre']}** - {info['auteur']} {info['heure']}\n\n{info['texte']}")
        if info.get("fichier") and os.path.exists(info["fichier"]): st.image(info["fichier"],width=350)
    if st.session_state.is_admin:
        st.divider()
        ti=st.text_input("Titre info")
        te=st.text_area("Message officiel")
        fi=st.file_uploader("Photo",type=["jpg","png"],key="info")
        if st.button("Épingler 📌"):
            fp=None
            if fi:
                fp=f"uploads/INFO_{fi.name}"
                with open(fp,"wb") as f: f.write(fi.getbuffer())
            infos=charger(FICHIER_INFOS)
            infos.append({"titre":ti,"texte":te,"fichier":fp,"auteur":st.session_state.nom,"heure":datetime.now().strftime("%d/%m %H:%M")})
            sauver(FICHIER_INFOS, infos)
            st.rerun()
