import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

# Connexion Supabase
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# ====================== SESSION STATE ======================
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

    # Navigation contrôlée par session_state
    pages = [
        "📊 Tableau de bord",
        "📁 Fiche Chantier",
        "⚡ Encodage Rapide",
        "📅 Planning & Agenda",
        "📋 Bibliothèque Tâches"
    ]
    
    # On force l'index selon la valeur actuelle de current_page
    try:
        current_index = pages.index(st.session_state.current_page)
    except:
        current_index = 0

    page = st.radio("Navigation", pages, index=current_index)

    # Si l'utilisateur change manuellement dans la sidebar
    if page != st.session_state.current_page:
        st.session_state.current_page = page
        st.rerun()

# ====================== FONCTIONS ======================
def get_projects():
    response = supabase.table("projects").select("*").execute()
    return pd.DataFrame(response.data)

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
        
        st.success("✅ Fiche chantier affichée")
        st.info("On ajoutera bientôt les tâches, événements et photos ici.")

else:
    st.info(f"Page **{st.session_state.current_page}** en cours de développement.")

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
