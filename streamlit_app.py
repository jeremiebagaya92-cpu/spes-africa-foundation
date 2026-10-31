import streamlit as st
from datetime import datetime
import json, os, time

st.set_page_config(page_title="SPES Africa", page_icon="💬", layout="centered")

os.makedirs("uploads", exist_ok=True)
os.makedirs("avatars", exist_ok=True)

CHAT = "chat.json"
MEMBRES = "membres.json"
BANNIS = "bannis.json"
LOGO = "logo_ong.jpg"

def charger(f):
    if os.path.exists(f):
        try:
            with open(f,"r",encoding="utf-8") as j: return json.load(j)
        except: return []
    return []
def sauver(f,d):
    with open(f,"w",encoding="utf-8") as j: json.dump(d,j,ensure_ascii=False, indent=2)

# --- CSS TELEGRAM ---
st.markdown("""
<style>
.stApp {background:#0e1621}
header {background:#212121 !important}
.wa-header {background:#212121; padding:10px 15px; display:flex; align-items:center; gap:10px; border-radius:10px 10px 0 0; border-bottom:1px solid #333}
.wa-header img {width:42px; height:42px; border-radius:50%; object-fit:cover}
.titre {color:white; font-weight:bold}
.online {color:#0ac630; font-size:13px}
#chat-box {background:#0e1621; padding:10px; border-radius:0 0 10px 10px}
.bulle {background:#182533; padding:8px 12px; border-radius:18px 18px 18px 4px; margin:8px 0; max-width:80%; display:flex; gap:8px; color:white}
.bulle-moi {background:#2b5278; margin-left:auto; border-radius:18px 18px 4px 18px; flex-direction:row-reverse}
.bulle img {width:36px; height:36px; border-radius:50%; object-fit:cover}
.nom-telegram {color:#2b88d8; font-weight:bold; font-size:13px}
.heure {color:#7d8b99; font-size:11px; text-align:right; margin-top:3px}
.system {text-align:center; background:#182533; color:#7d8b99; font-size:12px; padding:6px 12px; border-radius:12px; margin:10px auto; max-width:80%}
.admin-bar {background:#1a1a1a; border:1px solid #2b88d8; padding:10px; border-radius:10px; margin:10px 0}
</style>
""", unsafe_allow_html=True)

# Header
c1,c2 = st.columns([1,6])
with c1:
    if os.path.exists(LOGO):
        st.image(LOGO, width=45)
    else:
        st.image("https://cdn-icons-png.flaticon.com/512/2345/2345532.png", width=45)
with c2:
    st.markdown("<div class='titre'>SPES Africa Foundation</div><div class='online'>Telegram privé - tu contrôles tout</div>", unsafe_allow_html=True)

st.divider()

# --- BANNI ? ---
if "nom" in st.session_state:
    bannis = charger(BANNIS)
    if any(b["nom"] == st.session_state.nom for b in bannis):
        st.error("🚫 Tu as été banni par l'admin")
        if st.button("Quitter"):
            del st.session_state.nom
            st.rerun()
        st.stop()

# --- FORMULAIRE ---
if "nom" not in st.session_state:
    st.markdown("<div style='background:#212121; padding:20px; border-radius:12px'>", unsafe_allow_html=True)
    st.subheader("🔐 Entrer dans le groupe Telegram")
    nom = st.text_input("Nom *", placeholder="")
    postnom = st.text_input("Post-nom *", placeholder="")
    prenom = st.text_input("Prénom *", placeholder="")
    fonction = st.text_input("Fonction *", placeholder="Ex: Comptable")
    tel = st.text_input("Téléphone *", placeholder="+243...")
    
    st.write("Photo de profil *")
    # 2 OPTIONS POUR QUE ÇA MARCHE TOUJOURS
    photo_galerie = st.file_uploader("📁 Choisir dans la galerie", type=["jpg","jpeg","png"], key="galerie")
    photo_camera = st.camera_input("📷 Ou prendre photo directe")
    
    # CODE CACHÉ - PAS DE SPES2026 VISIBLE
    code = st.text_input("Code secret ONG *", type="password", placeholder="••••••••")

    if st.button("Rejoindre le groupe 💬", type="primary", use_container_width=True):
        la_photo = photo_galerie or photo_camera
        if not nom or not postnom or not prenom or not fonction or not tel:
            st.error("Remplis : Nom, Post-nom, Prénom, Fonction, Téléphone")
        elif la_photo is None:
            st.error("❌ Choisis ta photo : Galerie ou Appareil photo")
        elif not code:
            st.error("Mets le code secret")
        elif code not in ["SPES2026", "SPESADMIN2026"]:
            st.error("Code incorrect - demande à l'admin")
        else:
            # Vérifie banni
            bannis = charger(BANNIS)
            nom_complet = f"{prenom} {nom}"
            if any(b["nom"] == nom_complet for b in bannis):
                st.error("Tu es banni")
            else:
                chemin = f"avatars/{nom}_{prenom}_{int(time.time())}.jpg"
                with open(chemin,"wb") as f:
                    f.write(la_photo.getbuffer())
                
                membres = charger(MEMBRES)
                if not any(m["nom"]==nom_complet for m in membres):
                    membres.append({"nom":nom_complet, "postnom":postnom, "fonction":fonction, "tel":tel, "avatar":chemin, "date":datetime.now().strftime("%d/%m/%Y %H:%M")})
                    sauver(MEMBRES, membres)
                
                chat = charger(CHAT)
                chat.append({"id":str(time.time()), "nom":"SYSTEME", "texte":f"👋 {nom_complet} ({fonction}) a rejoint", "heure":datetime.now().strftime("%H:%M"), "type":"system"})
                sauver(CHAT, chat)
                
                st.session_state.nom = nom_complet
                st.session_state.avatar = chemin
                st.session_state.fonction = fonction
                st.session_state.is_admin = (code=="SPESADMIN2026")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR + CONTROLE ADMIN ---
with st.sidebar:
    st.image(st.session_state.avatar, width=80)
    st.write(f"**{st.session_state.nom}**")
    st.caption(st.session_state.fonction)
    if st.session_state.is_admin:
        st.success("👑 ADMIN - Tu contrôles tout")
        f = st.file_uploader("Changer logo groupe", type=["jpg","png"], key="logo")
        if f:
            with open(LOGO,"wb") as ff: ff.write(f.getbuffer())
            st.rerun()
        
        st.markdown("### Panneau Contrôle")
        membres = charger(MEMBRES)
        st.write(f"Membres: {len(membres)}")
        for m in membres:
            col_a, col_b = st.columns([3,1])
            col_a.write(f"{m['nom']} - {m['tel']}")
            if col_b.button("🚫", key="ban_"+m["nom"]):
                bannis = charger(BANNIS)
                bannis.append({"nom":m["nom"], "par":st.session_state.nom, "date":datetime.now().strftime("%d/%m %H:%M")})
                sauver(BANNIS, bannis)
                st.rerun()
        
        # Export preuves
        if st.button("📥 Télécharger preuves (JSON)"):
            st.download_button("Télécharger", data=json.dumps({"membres":charger(MEMBRES), "chat":charger(CHAT), "bannis":charger(BANNIS)}, indent=2, ensure_ascii=False), file_name=f"SPES-preuves-{datetime.now().strftime('%Y-%m-%d')}.json")
        
        bannis = charger(BANNIS)
        if bannis:
            st.write("Bannis:", bannis)

    if st.button("Quitter groupe"):
        del st.session_state.nom
        st.rerun()

# --- CHAT TELEGRAM AUTO-REFRESH ---
@st.fragment(run_every=3)
def afficher_chat():
    chat = charger(CHAT)
    for m in chat[-100:]:
        if m.get("type")=="system":
            st.markdown(f"<div class='system'>{m['texte']}</div>", unsafe_allow_html=True)
            continue
        
        # Trouve avatar
        avatar_path = m.get("photo") or ""
        membres = charger(MEMBRES)
        for mm in membres:
            if mm["nom"] == m["nom"]:
                avatar_path = mm.get("avatar", "")
                break
        if not avatar_path or not os.path.exists(avatar_path):
            avatar_path = st.session_state.avatar if m["nom"]==st.session_state.nom else "https://cdn-icons-png.flaticon.com/512/1375/1375106.png"

        is_me = m["nom"] == st.session_state.nom
        classe = "bulle bulle-moi" if is_me else "bulle"
        
        # Boutons admin
        admin_btns = ""
        if st.session_state.is_admin and m.get("id"):
            admin_btns = f"<span style='font-size:10px'> | <span style='color:#ff5959; cursor:pointer'>ID:{m['id'][:6]}</span></span>"

        # Fichier
        extra = ""
        if m.get("fichier") and os.path.exists(m["fichier"]):
            fp = m["fichier"]
            if fp.lower().endswith((".jpg",".jpeg",".png")):
                extra = f""
            elif fp.lower().endswith((".mp3",".wav",".m4a",".ogg")):
                extra = f"<audio controls src='{fp}' style='width:200px'></audio>"
        
        st.markdown(f"""
        <div class="{classe}">
            <img src="" />
            <div style="flex:1">
                <div class="nom-telegram">{m['nom']} <small style="color:#aaa">{m.get('fonction','')}</small></div>
                <div style="font-size:14.5px">{m.get('texte','')}{extra}</div>
                <div class="heure">{m.get('heure','')} ✓✓ {admin_btns}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if m.get("fichier") and os.path.exists(m["fichier"]):
            fp = m["fichier"]
            if fp.lower().endswith((".jpg",".jpeg",".png")):
                st.image(fp, width=250)
            elif fp.lower().endswith((".mp3",".wav",".m4a",".ogg")):
                st.audio(fp)
            else:
                with open(fp,"rb") as ff:
                    st.download_button(f"📄 {os.path.basename(fp)}", ff, key=fp+m["heure"]+str(time.time()))

        if st.session_state.is_admin and m.get("id"):
            col1, col2 = st.columns([1,4])
            if col1.button("🗑️", key="del_"+m["id"]):
                chat_new = [x for x in charger(CHAT) if x.get("id") != m["id"]]
                sauver(CHAT, chat_new)
                st.rerun()

afficher_chat()

st.divider()

# Envoi
txt = st.text_input("Message", placeholder="Écrire un message...", label_visibility="collapsed", key="msg_input")
c1, c2, c3 = st.columns([1,1,3])
with c1:
    fichier = st.file_uploader("📎", type=["jpg","jpeg","png","pdf","docx","mp4","mp3","wav","m4a"], label_visibility="collapsed", key="file_up")
with c2:
    vocal = st.audio_input("🎤", label_visibility="collapsed")
with c3:
    envoyer = st.button("➤ Envoyer", use_container_width=True, type="primary")

if envoyer:
    fpath = None
    up = fichier or vocal
    if up:
        name = getattr(up,'name','vocal.wav')
        if vocal: name = f"vocal_{datetime.now().strftime('%H%M%S')}.wav"
        fpath = f"uploads/{datetime.now().strftime('%H%M%S')}_{name}"
        with open(fpath,"wb") as ff: ff.write(up.getbuffer())
    
    if txt or fpath:
        chat = charger(CHAT)
        chat.append({"id":str(time.time()), "nom":st.session_state.nom, "fonction":st.session_state.fonction, "texte":txt, "fichier":fpath, "heure":datetime.now().strftime("%H:%M"), "photo":st.session_state.avatar})
        sauver(CHAT, chat)
        st.rerun()
