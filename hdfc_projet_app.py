import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px
from datetime import datetime, timedelta

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

elif page == "⚡ Encodage Rapide":
    st.subheader("⚡ Encodage Rapide")
    df = get_projects()
    with st.form("encode_form"):
        chantier = st.selectbox("Chantier", df["name"].tolist())
        projet_id = int(df[df["name"] == chantier]["id"].values[0])
        type_event = st.selectbox("Type", ["Problème", "Réussite", "Étape terminée", "Blocage technique C4"])
        description = st.text_area("Description")
        if st.form_submit_button("Enregistrer"):
            supabase.table("events").insert({
                "project_id": projet_id, "user_id": 1, "event_type": type_event, "description": description
            }).execute()
            st.success("Enregistré !")
            st.rerun()

elif page == "📅 Planning & Agenda":
    st.subheader("📅 Planning & Agenda")
    
    # Sélecteur de période
    col1, col2 = st.columns(2)
    with col1:
        view_mode = st.radio("Vue", ["Agenda Mensuel", "Gantt"], horizontal=True)
    with col2:
        current_month = st.date_input("Mois", datetime(2026, 6, 1), label_visibility="collapsed")
    
    if view_mode == "Gantt":
        df = get_projects()
        gantt_data = []
        for _, p in df.iterrows():
            gantt_data.append({
                "Task": p["name"][:40],
                "Start": "2026-06-01",
                "Finish": "2026-09-15",
                "Progress": p["progress_pct"],
                "Status": p["statut"]
            })
        fig = px.timeline(pd.DataFrame(gantt_data), x_start="Start", x_end="Finish", y="Task", color="Status")
        fig.update_layout(height=650)
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Agenda Mensuel
        st.write(f"**Agenda - {current_month.strftime('%B %Y')}**")
        st.info("Vue agenda mensuel simplifiée (à développer davantage avec vraies dates d'assignation).")
        
        # Simulation d'agenda
        agenda_data = [
            {"Date": "2026-06-03", "Projet": "Villa Uccle", "Activité": "Installation acoustique", "Personne": "Jean Installer"},
            {"Date": "2026-06-06", "Projet": "Boutique HD", "Activité": "Présence samedi (2 pers.)", "Personne": "Antoine + Marie"},
            {"Date": "2026-06-10", "Projet": "Ixelles", "Activité": "Programmation C4", "Personne": "Marie C4"},
            {"Date": "2026-06-15", "Projet": "Waterloo", "Activité": "RDV commercial", "Personne": "Sophie"},
        ]
        st.dataframe(pd.DataFrame(agenda_data), use_container_width=True, hide_index=True)

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")elif page == "📅 Planning & Coordination":
    st.subheader("📅 Planning & Coordination - Vue Gantt")
    
    df = get_projects()
    
    # Préparation des données pour Gantt
    gantt_data = []
    for _, p in df.iterrows():
        gantt_data.append({
            "Task": p["name"][:35] + "..." if len(p["name"]) > 35 else p["name"],
            "Start": "2026-06-01",
            "Finish": "2026-08-15",
            "Progress": p["progress_pct"],
            "Status": p["statut"]
        })
    
    gantt_df = pd.DataFrame(gantt_data)
    
    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Status",
        title="Vue Gantt des Projets HD Full Concept",
        labels={"Task": "Projet"}
    )
    
    fig.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Liste détaillée")
    st.dataframe(df[["name", "client_name", "type_projet", "statut", "progress_pct"]], use_container_width=True, hide_index=True)

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
