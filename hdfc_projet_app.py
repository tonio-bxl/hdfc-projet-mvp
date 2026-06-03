import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
from datetime import datetime

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
        "📅 Planning & Agenda"
    ])

# ====================== FONCTIONS ======================
def get_projects():
    response = supabase.table("projects").select("*").execute()
    return pd.DataFrame(response.data)

def get_tasks(project_id=None):
    query = supabase.table("tasks").select("*, projects(name)")
    if project_id:
        query = query.eq("project_id", project_id)
    response = query.order("start_date").execute()
    return pd.DataFrame(response.data)

# ====================== PAGES ======================

if page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    df = get_projects()
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
        st.progress(float(projet["progress_pct"]) / 100)
    
    st.subheader("Tâches du projet")
    tasks = get_tasks(projet["id"])
    if not tasks.empty:
        st.dataframe(tasks[["name", "description", "statut", "progress_pct", "start_date", "end_date", "assigned_to", "external_intervenant"]], 
                    use_container_width=True, hide_index=True)
    else:
        st.info("Aucune tâche définie pour ce projet.")

elif page == "⚡ Encodage Rapide":
    st.subheader("⚡ Encodage Rapide sur Chantier")
    df = get_projects()
    with st.form("encode_form"):
        chantier = st.selectbox("Chantier", df["name"].tolist())
        projet_id = int(df[df["name"] == chantier]["id"].values[0])
        type_event = st.selectbox("Type", ["Problème", "Réussite", "Étape terminée", "Blocage technique C4"])
        description = st.text_area("Description")
        if st.form_submit_button("📤 Enregistrer"):
            supabase.table("events").insert({
                "project_id": projet_id, "user_id": 1, "event_type": type_event, "description": description
            }).execute()
            st.success("Événement enregistré !")
            st.rerun()

elif page == "📅 Planning & Agenda":
    st.subheader("📅 Planning & Agenda - Timeline & Dépendances")
    
    df = get_projects()
    view_mode = st.radio("Type de vue", ["Timeline Globale", "Tâches Détaillées"], horizontal=True)
    
    if view_mode == "Timeline Globale":
        st.write("**Timeline Globale des Projets**")
        gantt_data = []
        for _, p in df.iterrows():
            gantt_data.append({
                "Task": p["name"][:40],
                "Start": "2026-06-01",
                "Finish": "2026-09-15",
                "Progress": p["progress_pct"],
                "Status": p["statut"]
            })
        fig = px.timeline(pd.DataFrame(gantt_data), x_start="Start", x_end="Finish", y="Task", color="Status", title="Vue Gantt des Projets")
        fig.update_layout(height=700)
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Tâches Détaillées
        st.write("**Tâches par projet (avec dépendances & intervenants externes)**")
        for _, proj in df.iterrows():
            with st.expander(f"{proj['name']} — {proj['client_name']} ({proj['progress_pct']}%)"):
                tasks = get_tasks(proj["id"])
                if not tasks.empty:
                    st.dataframe(tasks[["name", "description", "statut", "progress_pct", "start_date", "end_date", "assigned_to", "external_intervenant"]], 
                               use_container_width=True, hide_index=True)
                else:
                    st.info("Aucune tâche pour ce projet.")

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
