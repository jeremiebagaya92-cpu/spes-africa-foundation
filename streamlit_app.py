import streamlit as st
from datetime import datetime
import json, os, random
from PIL import Image

st.set_page_config(page_title="SPES Africa Groupe", page_icon="💬", layout="centered")
os.makedirs("uploads", exist_ok=True)
os.makedirs("avatars", exist_ok=True)

FICHIER_CHAT = "chat.json"
FICHIER_INFOS = "infos.json"

def charger(f):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as x: return json.load(x)
        except: return []
    return []
def sauver(f,d):
    with open(f,"w",encoding="utf-8") as x: json.dump(d,x,ensure_ascii=False)

couleurs = ["#e542a3","#1f7aec","#ffbc38","#06d6a0","#ff7f50"]

# --- LOGO ONG ---
st.image("https://cdn-icons-png.flaticon.com/512/2345/2345532.png", width=80)
st.title("SPES Africa Foundation")
st.caption("27 en ligne - Groupe privé des membres")

# --- CONNEXION AVEC PHOTO OBLIGATOIRE ---
if "nom" not in st.session_state:
    st.divider()
    st.subheader("🔐 Rejoindre le groupe")
    nom = st.text_input("Ton nom complet")
    photo = st.file_uploader("Ta photo de profil *obligatoire", type=["jpg","png","jpeg"])
    code = st.text_input("Code du groupe", type="password")
    
    if st.button("Rejoindre le groupe", use_container_width=True):
        if not nom or not photo or not code:
            st.error("Mets nom + photo + code")
        elif code not in ["SPES2026","SPESADMIN2026"]:
            st.error("Code faux")
        else:
            # Compresser et sauver avatar pour économiser espace
            img = Image.open(photo)
            img = img.resize((200,200))
            path = f"avatars/{nom}.jpg"
            img.save(path, "JPEG", quality=70)
            
            st.session_state.nom = nom
            st.session_state.avatar = path
            st.session_state.is_admin = (code=="SPESADMIN2026")
            st.session_state.couleur = random.choice(couleurs)
            
            # Message "a rejoint"
            msgs = charger(FICHIER_CHAT)
            msgs.append({
                "nom": "SYSTEME",
                "texte": f"~ {nom} a rejoint le groupe",
                "heure": datetime.now().strftime("%H:%M"),
                "couleur": "#8696a0",
                "type": "system"
            })
            sauver(FICHIER_CHAT, msgs)
            st.rerun()
    st.stop()

# Sidebar profil
with st.sidebar:
    if os.path.exists(st.session_state.avatar):
        st.image(st.session_state.avatar, width=120)
    st.write(f"**{st.session_state.nom}**")
    if st.session_state.is_admin: st.success("👑 ADMIN")
    # Afficher espace utilisé
    total = sum(os.path.getsize(f"uploads/{f}") for f in os.listdir("uploads") if os.path.exists(f"uploads/{f}"))/1024/1024 if os.listdir("uploads") else 0
    st.caption(f"Espace utilisé: {total:.1f} MB")
    if st.button("Quitter"):
        del st.session_state.nom
        st.rerun()

# --- ONGLETS ---
tab_chat, tab_infos = st.tabs(["💬 Groupe (comme ta photo)", "📢 Infos Épinglées"])

with tab_chat:
    messages = charger(FICHIER_CHAT)
    
    # AFFICHAGE AVEC PHOTO DE PROFIL
    for m in messages[-100:]:
        if m.get("type")=="system":
            st.markdown(f"<center style='color:#8696a0; font-size:12px; background:#182229; padding:5px; border-radius:8px; margin:5px'>{m['texte']}</center>", unsafe_allow_html=True)
            continue
            
        col_img, col_msg = st.columns([1, 9])
        avatar_path = f"avatars/{m['nom']}.jpg"
        if os.path.exists(avatar_path):
            col_img.image(avatar_path, width=45)
        else:
            col_img.write("👤")
        
        with col_msg:
            couleur = m.get("couleur","#1f7aec")
            with st.container(border=True):
                st.markdown(f"<span style='color:{couleur}; font-weight:bold'>~ {m['nom']}</span> <span style='color:#8696a0; font-size:11px; float:right'>{m['heure']}</span>", unsafe_allow_html=True)
                if m.get("texte"):
                    st.write(m["texte"])
                if m.get("fichier"):
                    fp = m["fichier"]
                    if os.path.exists(fp):
                        if fp.lower().endswith((".jpg",".png",".jpeg")):
                            st.image(fp, width=280)
                        elif fp.lower().endswith((".mp3",".wav",".m4a",".ogg")):
                            st.audio(fp)
                        else:
                            with open(fp,"rb") as f:
                                st.download_button(f"📥 {os.path.basename(fp)}", f, file_name=os.path.basename(fp), key=fp+m['heure']+str(random.random()))
    
    st.divider()
    st.write("**Envoyer :**")
    txt = st.text_input("Message", placeholder="Message", label_visibility="collapsed")
    
    c1,c2,c3 = st.columns(3)
    with c1:
        img_file = st.file_uploader("📷 Photo", type=["jpg","png","jpeg"], label_visibility="collapsed", key="img")
    with c2:
        audio_file = st.file_uploader("🎤 Audio", type=["mp3","wav","m4a","ogg"], label_visibility="collapsed", key="aud")
    with c3:
        doc_file = st.file_uploader("📎 Fichier", type=["pdf","docx","mp4"], label_visibility="collapsed", key="doc")
    
    # Enregistrement vocal direct comme WhatsApp
    audio_enregistre = st.audio_input("Enregistrer un vocal 🎙️")
    
    if st.button("➤ Envoyer", use_container_width=True):
        fpath = None
        fichier_a_sauver = img_file or audio_file or doc_file or audio_enregistre
        
        if fichier_a_sauver:
            # Compresser image pour économiser espace
            if img_file:
                img = Image.open(img_file)
                img.thumbnail((800,800))
                fpath = f"uploads/{datetime.now().strftime('%H%M%S')}_{img_file.name}.jpg"
                img.save(fpath, "JPEG", quality=60)
            else:
                ext = fichier_a_sauver.name if hasattr(fichier_a_sauver,'name') else "vocal.wav"
                if audio_enregistre: ext = "vocal.wav"
                fpath = f"uploads/{datetime.now().strftime('%H%M%S')}_{ext}"
                with open(fpath,"wb") as f: f.write(fichier_a_sauver.getbuffer())
        
        if txt or fpath:
            messages.append({
                "nom": st.session_state.nom,
                "texte": txt,
                "fichier": fpath,
                "heure": datetime.now().strftime("%H:%M"),
                "couleur": st.session_state.get("couleur","#1f7aec")
            })
            sauver(FICHIER_CHAT, messages)
            st.rerun()

with tab_infos:
    st.markdown("### 📌 Iko épinglé")
    infos = charger(FICHIER_INFOS)
    for info in reversed(infos):
        st.success(f"**{info['titre']}** - {info['auteur']} {info['heure']}\n\n{info['texte']}")
        if info.get("fichier") and os.path.exists(info["fichier"]):
            st.image(info["fichier"], width=350)
    
    if st.session_state.is_admin:
        st.divider()
        st.subheader("👑 Publier info officielle (Admin seulement)")
        ti = st.text_input("Titre", placeholder="Voici l'horaire")
        te = st.text_area("Contenu")
        fi = st.file_uploader("Photo info", type=["jpg","png"], key="info2")
        if st.button("Épingler 📌"):
            fp=None
            if fi:
                img = Image.open(fi)
                img.thumbnail((800,800))
                fp=f"uploads/INFO_{fi.name}.jpg"
                img.save(fp,"JPEG",quality=70)
            infos.append({"titre":ti,"texte":te,"fichier":fp,"auteur":st.session_state.nom,"heure":datetime.now().strftime("%d/%m %H:%M")})
            sauver(FICHIER_INFOS, infos)
            st.rerun()
