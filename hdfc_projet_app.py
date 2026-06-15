import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

# Connexion Supabase
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# Initialisation session
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
    page = st.radio("Navigation", [
        "📊 Tableau de bord",
        "📁 Fiche Chantier",
        "⚡ Encodage Rapide",
        "📅 Planning & Agenda",
        "📋 Bibliothèque Tâches"
    ])

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

if page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    df = get_projects()
    
    for _, proj in df.iterrows():
        col1, col2, col3 = st.columns([5, 2, 1.5])
        with col1:
            if st.button(f"📂 {proj['name']}", key=f"open_{proj['id']}"):
                st.session_state.current_project_id = proj['id']
                st.rerun()   # Rafraîchit pour aller sur la fiche
        with col2:
            st.progress(float(proj['progress_pct']) / 100, text=f"{proj['progress_pct']}%")
        with col3:
            st.caption(proj['statut'])
        st.divider()

elif page == "📁 Fiche Chantier":
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
            st.progress(float(projet["progress_pct"]) / 100)
        
        st.divider()
        st.subheader("Ajouter une tâche depuis la bibliothèque")
        
        templates = get_task_templates()
        search = st.text_input("🔍 Rechercher une tâche", key="task_search")
        cat = st.selectbox("Catégorie", ["Toutes"] + sorted(templates["category"].unique().tolist()), key="task_cat")
        
        filtered = templates
        if search:
            filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
        if cat != "Toutes":
            filtered = filtered[filtered["category"] == cat]
        
        for _, t in filtered.iterrows():
            col_a, col_b = st.columns([6, 1])
            with col_a:
                st.write(f"**{t['name']}** ({t['category']})")
            with col_b:
                if st.button("Ajouter", key=f"add_{t['id']}"):
                    add_task_to_project(st.session_state.current_project_id, t['id'])
                    st.success(f"Tâche ajoutée : {t['name']}")
                    st.rerun()

elif page == "📋 Bibliothèque Tâches":
    st.subheader("📋 Bibliothèque de Tâches Réutilisables")
    templates = get_task_templates()
    search = st.text_input("🔍 Rechercher")
    category = st.selectbox("Catégorie", ["Toutes"] + sorted(templates["category"].unique().tolist()))
    
    filtered = templates
    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
    if category != "Toutes":
        filtered = filtered[filtered["category"] == category]
    
    st.dataframe(filtered[["category", "name", "description", "estimated_duration_days", "typical_assigned_to"]], 
                use_container_width=True, hide_index=True)

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
