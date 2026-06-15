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
        "⚡ Encodage Rapide",
        "📅 Planning & Agenda",
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
        - [ ] Ajouter les tâches dans la fiche chantier (depuis la bibliothèque)
        - [ ] Afficher l'historique des événements + photos dans la fiche
        - [ ] Upload photos + documents dans la création et la fiche
        - [ ] Note vocale + transcription IA
        - [ ] Gestion fine des rôles
        - [ ] Export PDF d'une fiche chantier
        """)

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
            st.progress(float(proj['progress_pct']) / 100, text=f"{proj['progress_pct']}%")
        with col3:
            debut = proj.get('date_debut', 'N/A')
            st.caption(f"▶️ {debut}")
        with col4:
            echeance = proj.get('date_fin_estimee', 'N/A')
            st.caption(f"📅 {echeance}")
        with col5:
            st.caption(proj['statut'])
        st.divider()
    
    show_todo_list()

# ============================================================
# PAGE : FICHE CHANTIER
# ============================================================
elif st.session_state.current_page == "📁 Fiche Chantier":
    st.markdown("""
        <style>
        .stMarkdown, .stMetric, .stSelectbox, .stButton { font-size: 14px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    df = get_projects()
    project_options = {row['name']: row['id'] for _, row in df.iterrows()}
    
    if st.session_state.current_project_id:
        current_name = df[df['id'] == st.session_state.current_project_id]['name'].values[0]
    else:
        current_name = list(project_options.keys())[0]
        st.session_state.current_project_id = project_options[current_name]
    
    selected_name = st.selectbox(
        "Changer de chantier",
        options=list(project_options.keys()),
        index=list(project_options.keys()).index(current_name)
    )
    
    if project_options[selected_name] != st.session_state.current_project_id:
        st.session_state.current_project_id = project_options[selected_name]
        st.rerun()
    
    projet = df[df['id'] == st.session_state.current_project_id].iloc[0]
    
    st.subheader(projet["name"])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Client", projet["client_name"])
        st.metric("Type", projet["type_projet"])
    with col2:
        st.metric("Statut", projet["statut"])
        st.progress(float(projet["progress_pct"]) / 100, text=f"{projet['progress_pct']}%")
    with col3:
        echeance = projet.get('date_fin_estimee', 'Non définie')
        st.metric("📅 Date d'échéance", echeance)
    
    st.divider()
    st.info("Ici on affichera bientôt les tâches, événements et photos du chantier.")
    show_todo_list()

# ============================================================
# PAGE : PLANNING & AGENDA (HYBRIDE)
# ============================================================
elif st.session_state.current_page == "📅 Planning & Agenda":
    st.subheader("📅 Planning & Agenda Global")
    
    periode = st.selectbox(
        "Période à afficher",
        ["1 Semaine", "2 Semaines", "1 Mois", "3 Mois", "6 Mois"],
        index=2
    )
    
    df = get_projects()
    
    if periode in ["1 Semaine", "2 Semaines", "1 Mois"]:
        # Vue Calendrier
        from streamlit_calendar import calendar
        events = []
        for _, proj in df.iterrows():
            if pd.notna(proj.get('date_fin_estimee')):
                start = proj.get('date_debut', '2026-06-01')
                events.append({
                    "title": proj['name'][:50],
                    "start": str(start),
                    "end": str(proj['date_fin_estimee']),
                    "backgroundColor": "#3b82f6" if proj['statut'] == "En cours" else "#10b981",
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
        
    else:
        # Vue Gantt pour 3 et 6 mois
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
            fig = px.timeline(
                pd.DataFrame(gantt_data),
                x_start="Start",
                x_end="Finish",
                y="Task",
                color="Status",
                title=f"Vue Gantt - {periode}",
                hover_data=["Progress"]
            )
            fig.update_layout(height=650, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune date d'échéance disponible.")
    
    show_todo_list()

# ============================================================
# PAGE : CRÉER UN CHANTIER
# ============================================================
elif st.session_state.current_page == "➕ Créer un chantier":
    if role != "Administrateur":
        st.error("Accès réservé à l'Administrateur.")
    else:
        st.subheader("➕ Créer un nouveau chantier")
        with st.form("create_project_form"):
            nom_projet = st.text_input("Nom du projet *")
            nom_client = st.text_input("Nom du client *")
            type_chantier = st.selectbox("Type de chantier *", ["Home Cinéma Control4", "Domotique résidentielle C4", "Intégration acoustique premium", "Salles de cinéma privées", "Signage & Visio professionnelle", "Audio multiroom", "Autre"])
            
            st.markdown("**Adresse**")
            col_rue, col_num = st.columns([3, 1])
            with col_rue: rue = st.text_input("Rue *")
            with col_num: numero = st.text_input("Numéro *")
            complement = st.text_input("Complément d'adresse")
            col_cp, col_ville, col_pays = st.columns([1.5, 2, 1.5])
            with col_cp: code_postal = st.text_input("Code postal *")
            with col_ville: ville = st.text_input("Ville *")
            with col_pays: pays = st.text_input("Pays", value="Belgique")
            
            telephone = st.text_input("Téléphone *")
            email = st.text_input("Email *")
            
            col_statut, col_echeance = st.columns(2)
            with col_statut:
                statut = st.selectbox("Statut *", ["Offre à faire", "Devis envoyé", "Devis signé / Commande confirmée", "En préparation", "En cours", "En pause", "Terminé"])
            with col_echeance:
                date_echeance = st.date_input("Date d'échéance estimée *", value=date.today())
            
            ca_estime = st.number_input("CA estimé HTVA (€)", min_value=0, step=1000)
            is_c4 = st.checkbox("Projet Control4")
            notes = st.text_area("Notes / Description", height=100)
            
            submitted = st.form_submit_button("✅ Créer le chantier", type="primary")
            
            if submitted:
                if not all([nom_projet, nom_client, rue, numero, code_postal, ville, telephone, email]):
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    adresse_complete = f"{rue} {numero}"
                    if complement: adresse_complete += f", {complement}"
                    adresse_complete += f", {code_postal} {ville}, {pays}"
                    
                    data = {
                        "name": nom_projet,
                        "client_name": nom_client,
                        "type_projet": type_chantier,
                        "adresse": adresse_complete,
                        "statut": statut,
                        "date_fin_estimee": str(date_echeance),
                        "ca_estime_htva": ca_estime,
                        "is_c4": 1 if is_c4 else 0,
                        "notes": notes
                    }
                    create_project(data)
                    st.success("✅ Chantier créé avec succès !")
                    st.balloons()
    show_todo_list()

# ============================================================
# AUTRES PAGES
# ============================================================
else:
    st.info(f"Page **{st.session_state.current_page}** en cours de développement.")
    show_todo_list()

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
