import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date
import plotly.express as px

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

# ============================================================
# CONNEXION SUPABASE
# ============================================================
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

# ============================================================
# SESSION STATE
# ============================================================
if 'current_page' not in st.session_state:
    st.session_state.current_page = "📊 Tableau de bord"
if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None

# ============================================================
# HEADER
# ============================================================
col1, col2 = st.columns([1.2, 5])
with col1:
    st.image("logo-HDFC.png", width=200)
with col2:
    st.markdown("<h1 style='margin: 0; font-size: 26px;'>Centralisation des Projets</h1>", unsafe_allow_html=True)
st.divider()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("logo-HDFC.png", width=140)
    st.header("HD Full Concept")
    role = st.selectbox("Votre rôle", ["Administrateur", "Technicien", "Programmeur C4", "Direction"])
    st.caption(f"Connecté en tant que : **{role}**")
    st.divider()

    pages = [
        "📊 Tableau de bord",
        "📁 Fiche Chantier",
        "📅 Planning & Agenda",
        "⚡ Encodage Rapide",
        "📋 Bibliothèque Tâches"
    ]
    if role == "Administrateur":
        pages.append("➕ Créer un chantier")

    try:
        current_index = pages.index(st.session_state.current_page)
    except:
        current_index = 0

    page = st.radio("Navigation", pages, index=current_index)

    if page != st.session_state.current_page:
        st.session_state.current_page = page
        st.rerun()

# ============================================================
# FONCTIONS
# ============================================================
def get_projects():
    response = supabase.table("projects").select("*").execute()
    return pd.DataFrame(response.data)

def create_project(data):
    supabase.table("projects").insert(data).execute()

def show_todo_list():
    with st.expander("📋 To-Do List (clique pour ouvrir/fermer)", expanded=False):
        st.markdown("""
        - [x] Gantt corrigé
        - [ ] Améliorations fiche chantier
        - [ ] Upload photos et documents
        - [ ] Gestion fine des rôles
        """)

# ============================================================
# COULEURS HARMONISÉES
# ============================================================
status_colors = {
    "Offre à faire": "#94a3b8",
    "Devis envoyé": "#f59e0b",
    "Devis signé / Commande confirmée": "#10b981",
    "En préparation": "#3b82f6",
    "En cours": "#ef4444",
    "En pause": "#6b7280",
    "Terminé": "#22c55e"
}

# ============================================================
# PAGE : TABLEAU DE BORD
# ============================================================
if st.session_state.current_page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    df = get_projects()
    
    col_tri, col_ordre = st.columns(2)
    with col_tri:
        tri_par = st.selectbox("Trier par", ["Nom du projet", "Date de début", "Date d'échéance", "Avancement", "Statut"])
    with col_ordre:
        ordre = st.radio("Ordre", ["Décroissant", "Croissant"], horizontal=True)
    
    ascending = (ordre == "Croissant")
    
    if tri_par == "Nom du projet":
        df = df.sort_values("name", ascending=ascending)
    elif tri_par == "Date de début":
        df['date_debut'] = pd.to_datetime(df['date_debut'], errors='coerce')
        df = df.sort_values("date_debut", ascending=ascending, na_position='last')
    elif tri_par == "Date d'échéance":
        df['date_fin_estimee'] = pd.to_datetime(df['date_fin_estimee'], errors='coerce')
        df = df.sort_values("date_fin_estimee", ascending=ascending, na_position='last')
    elif tri_par == "Avancement":
        df = df.sort_values("progress_pct", ascending=ascending)
    elif tri_par == "Statut":
        df = df.sort_values("statut", ascending=ascending)
    
    for _, proj in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([4, 1.2, 1.2, 1.2, 1.2])
        with col1:
            if st.button(f"📂 {proj['name']}", key=f"open_{proj['id']}"):
                st.session_state.current_project_id = proj['id']
                st.session_state.current_page = "📁 Fiche Chantier"
                st.rerun()
        with col2:
            st.progress(float(proj.get('progress_pct', 0)) / 100, text=f"{proj.get('progress_pct', 0)}%")
        with col3:
            st.caption(f"▶️ {proj.get('date_debut', 'N/A')}")
        with col4:
            st.caption(f"📅 {proj.get('date_fin_estimee', 'N/A')}")
        with col5:
            st.caption(proj['statut'])
        st.divider()
    
    show_todo_list()

# ============================================================
# PAGE : FICHE CHANTIER (version compacte)
# ============================================================
elif st.session_state.current_page == "📁 Fiche Chantier":
    st.markdown("""
        <style>
        .stMarkdown, .stMetric, .stSelectbox, .stButton, .stTextInput { font-size: 13px !important; }
        h1, h2, h3 { font-size: 20px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    df = get_projects()
    project_options = {row['name']: row['id'] for _, row in df.iterrows()}
    
    if st.session_state.current_project_id:
        current_name = df[df['id'] == st.session_state.current_project_id]['name'].values[0]
    else:
        current_name = list(project_options.keys())[0]
        st.session_state.current_project_id = project_options[current_name]
    
    # Ligne supérieure : Changer de chantier + Type + Progression
    col1, col2, col3 = st.columns([3, 2, 1.5])
    with col1:
        selected_name = st.selectbox(
            "Changer de chantier",
            options=list(project_options.keys()),
            index=list(project_options.keys()).index(current_name)
        )
    with col2:
        projet_temp = df[df['id'] == project_options[selected_name]].iloc[0]
        st.metric("Type", projet_temp.get("type_projet", "—"))
    with col3:
        st.metric("Avancement", f"{projet_temp.get('progress_pct', 0)}%")
    
    if project_options[selected_name] != st.session_state.current_project_id:
        st.session_state.current_project_id = project_options[selected_name]
        st.rerun()
    
    projet = df[df['id'] == st.session_state.current_project_id].iloc[0]
    
    st.subheader(projet["name"])
    
    # Infos très compactes
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Client", projet.get("client_name", "—"))
    with col_b:
        st.metric("Statut", projet.get("statut", "—"))
    with col_c:
        st.metric("Début", projet.get('date_debut', '—'))
    with col_d:
        st.metric("Échéance", projet.get('date_fin_estimee', '—'))
    
    st.progress(float(projet.get('progress_pct', 0)) / 100, text=f"Progression globale : {projet.get('progress_pct', 0)}%")
    
    st.divider()
    st.info("Ici on affichera bientôt les tâches, événements et photos du chantier.")
    show_todo_list()

# ============================================================
# PAGE : PLANNING & AGENDA
# ============================================================
elif st.session_state.current_page == "📅 Planning & Agenda":
    st.subheader("📅 Planning & Agenda Global")
    
    periode = st.selectbox(
        "Période à afficher",
        ["1 Semaine", "2 Semaines", "1 Mois", "3 Mois", "6 Mois"],
        index=3
    )
    
    df = get_projects()
    
    if periode in ["1 Semaine", "2 Semaines", "1 Mois"]:
        from streamlit_calendar import calendar
        events = []
        for _, proj in df.iterrows():
            if pd.notna(proj.get('date_fin_estimee')):
                start = proj.get('date_debut', '2026-06-01')
                color = status_colors.get(proj['statut'], "#64748b")
                events.append({
                    "title": proj['name'][:50],
                    "start": str(start),
                    "end": str(proj['date_fin_estimee']),
                    "backgroundColor": color,
                })
        
        initial_view = "timeGridWeek" if periode in ["1 Semaine", "2 Semaines"] else "dayGridMonth"
        
        calendar_options = {
            "editable": False,
            "selectable": True,
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,timeGridWeek,timeGridDay"},
            "initialView": initial_view,
            "height": 720,
            "locale": "fr",
        }
        calendar(events=events, options=calendar_options)
        
        st.write("**Légende des statuts :**")
        cols = st.columns(len(status_colors))
        for i, (statut, color) in enumerate(status_colors.items()):
            with cols[i]:
                st.markdown(f"<span style='color:{color}; font-size:18px;'>■</span> {statut}", unsafe_allow_html=True)
    
    else:
        st.write(f"**Vue Timeline - {periode}**")
        gantt_data = []
        for _, p in df.iterrows():
            if pd.notna(p.get('date_fin_estimee')):
                gantt_data.append({
                    "Task": p["name"][:40],
                    "Start": p.get('date_debut', '2026-06-01'),
                    "Finish": p['date_fin_estimee'],
                    "Progress": p.get('progress_pct', 0),
                    "Status": p['statut']
                })
        
        if gantt_data:
            gantt_df = pd.DataFrame(gantt_data)
            priority_map = {
                "En cours": 0,
                "En préparation": 1,
                "Devis signé / Commande confirmée": 2,
                "Devis envoyé": 3,
                "Offre à faire": 4,
                "En pause": 5,
                "Terminé": 6
            }
            gantt_df['priority'] = gantt_df['Status'].map(priority_map)
            gantt_df = gantt_df.sort_values(by=['priority', 'Start'])
            
            task_order = gantt_df["Task"].tolist()
            
            fig = px.timeline(
                gantt_df,
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Status",
                title=f"Vue Gantt - {periode}",
                hover_data=["Progress"],
                color_discrete_map=status_colors
            )
            
            fig.update_yaxes(categoryorder="array", categoryarray=task_order, autorange="reversed")
            fig.update_layout(height=750, showlegend=True, margin=dict(l=350))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune date d'échéance disponible.")
    
    show_todo_list()

# ============================================================
# AUTRES PAGES
# ============================================================
else:
    st.info(f"Page **{st.session_state.current_page}** en cours de développement.")
    show_todo_list()

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
