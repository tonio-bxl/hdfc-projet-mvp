import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

# Connexion Supabase
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Initialisation session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Tableau de bord"
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None

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
    
    # Navigation manuelle
    new_page = st.radio("Navigation", [
        "📊 Tableau de bord",
        "📁 Fiche Chantier",
        "⚡ Encodage Rapide",
        "📅 Planning & Agenda",
        "📋 Bibliothèque Tâches"
    ], key="sidebar_nav")
    
    if new_page != st.session_state.current_page:
        st.session_state.current_page = new_page
        st.rerun()

# ====================== FONCTIONS ======================
def get_projects():
    response = supabase.table("projects").select("*").execute()
    return pd.DataFrame(response.data)

def get_task_templates():
    response = supabase.table("task_templates").select("*").execute()
    return pd.DataFrame(response.data)

def add_task_to_project(project_id, template_id):
    template = supabase.table("task_templates").select("*").eq("id", template_id).execute().data[0]
    data = {
        "project_id": project_id,
        "name": template["name"],
        "description": template["description"],
        "statut": "À faire",
        "progress_pct": 0,
        "assigned_to": template.get("typical_assigned_to", "Non assigné")
    }
    supabase.table("tasks").insert(data).execute()

# ====================== PAGES ======================

if st.session_state.current_page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    df = get_projects()
    
    for _, proj in df.iterrows():
        col1, col2, col3 = st.columns([5, 2, 1.5])
        with col1:
            if st.button(f"📂 {proj['name']}", key=f"open_{proj['id']}"):
                st.session_state.current_project_id = proj['id']
                st.session_state.current_page = "📁 Fiche Chantier"
                st.rerun()
        with col2:
            st.progress(float(proj['progress_pct']) / 100, text=f"{proj['progress_pct']}%")
        with col3:
            st.caption(proj['statut'])
        st.divider()

elif st.session_state.current_page == "📁 Fiche Chantier":
    if st.session_state.current_project_id is None:
        st.warning("Aucun chantier sélectionné. Retournez au Tableau de bord.")
    else:
        df = get_projects()
        projet = df[df['id'] == st.session_state.current_project_id].iloc[0]
        
        st.subheader(projet["name"])
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Client", projet["client_name"])
            st.metric("Type", projet["type_projet"])
        with col2:
            st.metric("Statut", projet["statut"])
            st.progress(float(projet["progress_pct"]) / 100, text=f"Avancement : {projet['progress_pct']}%")
        
        st.divider()
        st.subheader("Ajouter une tâche depuis la bibliothèque")
        # (code d'ajout de tâche à venir dans la prochaine étape)

# Autres pages (simplifiées pour l'instant)
else:
    st.info(f"Page {st.session_state.current_page} en cours de développement.")

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
