import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

# ====================== CONNEXION SUPABASE ======================
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# ====================== HEADER ======================
col1, col2 = st.columns([1.2, 5])

with col1:
    st.image("logo-HDFC.png", width=200)

with col2:
    st.markdown("""
        <h1 style="margin: 0; font-size: 26px;">Centralisation des Projets</h1>
    """, unsafe_allow_html=True)

st.divider()

# ====================== SIDEBAR ======================
with st.sidebar:
    # Logo dans la sidebar
    st.image("logo-HDFC.png", width=160)
    st.header("HD Full Concept")
    
    role = st.selectbox(
        "Votre rôle",
        ["Administrateur", "Technicien", "Programmeur C4", "Direction"]
    )
    st.caption(f"Connecté en tant que : **{role}**")
    st.divider()
    
    page = st.radio("Navigation", [
        "📊 Tableau de bord",
        "📁 Fiche Chantier",
        "⚡ Encodage Rapide",
        "📅 Planning"
    ])

# ====================== FONCTIONS SUPABASE ======================
def get_projects():
    response = supabase.table("projects").select("*").execute()
    return response.data

def get_events(project_id=None):
    query = supabase.table("events").select("*, projects(name)")
    if project_id:
        query = query.eq("project_id", project_id)
    response = query.order("timestamp", desc=True).execute()
    return response.data

def add_event(project_id, event_type, description):
    data = {
        "project_id": project_id,
        "user_id": 1,  # À améliorer plus tard avec un vrai système d'utilisateur
        "event_type": event_type,
        "description": description,
        "est_resolu": False
    }
    supabase.table("events").insert(data).execute()

# ====================== PAGES ======================

if page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    projects = get_projects()
    if projects:
        df = pd.DataFrame(projects)
        st.dataframe(df[["name", "client_name", "type_projet", "statut", "progress_pct"]], use_container_width=True, hide_index=True)
    else:
        st.info("Aucun projet pour le moment.")

elif page == "📁 Fiche Chantier":
    st.subheader("Fiche Chantier")
    projects = get_projects()
    if projects:
        selected = st.selectbox("Choisir un chantier", [p["name"] for p in projects])
        projet = next(p for p in projects if p["name"] == selected)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Client", projet.get("client_name", "-"))
            st.metric("Type", projet.get("type_projet", "-"))
        with col2:
            st.metric("Statut", projet.get("statut", "-"))
            st.progress(float(projet.get("progress_pct", 0)) / 100)
        
        st.markdown("### Événements")
        events = get_events(projet["id"])
        for ev in events:
            st.write(f"**{ev['event_type']}** - {ev['description']}")
    else:
        st.warning("Aucun chantier disponible.")

elif page == "⚡ Encodage Rapide":
    st.subheader("Encodage Rapide")
    projects = get_projects()
    if projects:
        with st.form("encode"):
            chantier = st.selectbox("Chantier", [p["name"] for p in projects])
            projet_id = next(p["id"] for p in projects if p["name"] == chantier)
            type_event = st.selectbox("Type", ["Problème", "Réussite", "Étape terminée", "Blocage technique C4"])
            desc = st.text_area("Description")
            
            if st.form_submit_button("Envoyer"):
                add_event(projet_id, type_event, desc)
                st.success("Information enregistrée dans Supabase !")
                st.rerun()
    else:
        st.info("Aucun chantier disponible.")

elif page == "📅 Planning":
    st.subheader("Planning & Coordination")
    st.info("Vue Planning + Gantt à développer dans la prochaine version.")

st.divider()
st.caption("HD Full Concept SA — Prototype connecté à Supabase")
