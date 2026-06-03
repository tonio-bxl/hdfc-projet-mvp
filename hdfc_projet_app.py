import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

# Connexion Supabase
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# ====================== HEADER ======================
col1, col2 = st.columns([1.2, 5])
with col1:
    st.image("logo-HDFC.png", width=200)
with col2:
    st.markdown("<h1 style='margin: 0; font-size: 26px;'>Centralisation des Projets</h1>", unsafe_allow_html=True)
st.divider()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.image("logo-HDFC.png", width=140)
    st.header("HD Full Concept")
    role = st.selectbox("Votre rôle", ["Administrateur", "Technicien", "Programmeur C4", "Direction"])
    st.caption(f"Connecté en tant que : **{role}**")
    st.divider()
    page = st.radio("Navigation", [
        "📊 Tableau de bord",
        "📁 Fiche Chantier",
        "⚡ Encodage Rapide",
        "📅 Planning & Coordination"
    ])

# ====================== FONCTIONS ======================
def get_projects():
    response = supabase.table("projects").select("*").execute()
    return pd.DataFrame(response.data)

def get_events(project_id=None):
    query = supabase.table("events").select("*, projects(name)")
    if project_id:
        query = query.eq("project_id", project_id)
    response = query.order("timestamp", desc=True).execute()
    return response.data

def add_event(project_id, event_type, description, photo_b64=None):
    data = {
        "project_id": project_id,
        "user_id": 1,
        "event_type": event_type,
        "description": description,
        "est_resolu": False
    }
    supabase.table("events").insert(data).execute()

# ====================== PAGES ======================

if page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    df = get_projects()
    
    # Affichage avec barres de progression
    for _, proj in df.iterrows():
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.write(f"**{proj['name']}** — {proj['client_name']}")
        with col2:
            st.progress(float(proj['progress_pct']) / 100, text=f"{proj['progress_pct']}%")
        with col3:
            st.caption(proj['statut'])
        st.divider()

elif page == "📁 Fiche Chantier":
    st.subheader("Fiche Chantier détaillée")
    df = get_projects()
    selected = st.selectbox("Choisir un chantier", df["name"].tolist())
    projet = df[df["name"] == selected].iloc[0]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Client", projet["client_name"])
        st.metric("Type", projet["type_projet"])
    with col2:
        st.metric("Statut", projet["statut"])
        st.progress(float(projet["progress_pct"]) / 100, text=f"Avancement : {projet['progress_pct']}%")
    
    st.subheader("Événements")
    events = get_events(projet["id"])
    for ev in events:
        st.write(f"**{ev['event_type']}** — {ev['description']}")

elif page == "⚡ Encodage Rapide":
    st.subheader("⚡ Encodage Rapide sur Chantier")
    df = get_projects()
    with st.form("encode_form"):
        chantier = st.selectbox("Chantier", df["name"].tolist())
        projet_id = int(df[df["name"] == chantier]["id"].values[0])
        type_event = st.selectbox("Type", ["Problème", "Réussite", "Étape terminée", "Blocage technique C4"])
        description = st.text_area("Description")
        photo = st.file_uploader("Photo (optionnel)", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("📤 Enregistrer"):
            add_event(projet_id, type_event, description)
            st.success("Événement enregistré avec succès !")
            st.rerun()

elif page == "📅 Planning & Coordination":
    st.subheader("📅 Planning & Coordination")
    
    # Vue Gantt simplifiée
    st.write("**Vue Gantt simplifiée des chantiers**")
    df = get_projects()
    for _, p in df.iterrows():
        st.write(f"**{p['name']}**")
        st.progress(float(p['progress_pct']) / 100, text=f"{p['statut']} — {p['progress_pct']}%")
        st.caption("Équipe assignée : À implémenter")
        st.divider()

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
