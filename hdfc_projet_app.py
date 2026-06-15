import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date, datetime
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

def get_tasks(project_id):
    response = supabase.table("tasks").select("*").eq("project_id", project_id).execute()
    return pd.DataFrame(response.data)

def add_task(project_id, task_data):
    data = {"project_id": project_id, **task_data}
    supabase.table("tasks").insert(data).execute()

def list_project_photos(project_id):
    try:
        files = supabase.storage.from_("project-photos").list(f"{project_id}/")
        urls = []
        for file in files:
            if file.get('name'):
                url = supabase.storage.from_("project-photos").get_public_url(f"{project_id}/{file['name']}")
                urls.append(url)
        return urls
    except Exception as e:
        st.error(f"Erreur listing photos : {e}")
        return []

def upload_photo(project_id, uploaded_file):
    if not uploaded_file or not project_id:
        return None
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_name = f"{project_id}/{timestamp}_{uploaded_file.name}"
    try:
        supabase.storage.from_("project-photos").upload(
            path=file_name,
            file=uploaded_file.getvalue(),
            file_options={"content-type": uploaded_file.type or "image/jpeg"}
        )
        return supabase.storage.from_("project-photos").get_public_url(file_name)
    except Exception as e:
        st.error(f"❌ ERREUR UPLOAD DÉTAILLÉE : {str(e)}")
        st.code(str(e))  # affiche l'erreur complète Supabase
        return None

def get_task_library():
    response = supabase.table("task_library").select("*").order("category").execute()
    return pd.DataFrame(response.data)

def add_task_to_project(project_id, task_data):
    data = {"project_id": project_id, **task_data}
    supabase.table("tasks").insert(data).execute()

def show_todo_list():
    with st.expander("📋 To-Do List (clique pour ouvrir/fermer)", expanded=False):
        st.markdown("""
        - [x] Gantt corrigé
        - [x] Fiche chantier compacte
        - [x] Upload + affichage photos par chantier (debug amélioré)
        - [ ] Pouvoir encoder une nouvelle tâche / catégorie / sous-catégorie dans la DB
        - [ ] Bibliothèque de tâches avancée
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
# PAGE : TABLEAU DE BORD (inchangé)
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
# PAGE : FICHE CHANTIER (upload photos corrigé)
# ============================================================
elif st.session_state.current_page == "📁 Fiche Chantier":
    st.markdown("""
        <style>
        .stMetric label { font-size: 13.5px !important; }
        .stMetric div[data-testid="stMetricValue"] { font-size: 17px !important; font-weight: 600; }
        .stSelectbox { font-size: 14px !important; }
        h1, h2, h3 { font-size: 22px !important; }
        </style>
    """, unsafe_allow_html=True)
   
    df = get_projects()
    project_options = {row['name']: row['id'] for _, row in df.iterrows()}
   
    if st.session_state.current_project_id:
        current_name = df[df['id'] == st.session_state.current_project_id]['name'].values[0]
    else:
        current_name = list(project_options.keys())[0]
        st.session_state.current_project_id = project_options[current_name]
   
    col_select, col_type, col_prog = st.columns([3.5, 2.5, 3])
    with col_select:
        selected_name = st.selectbox("Changer de chantier", options=list(project_options.keys()), index=list(project_options.keys()).index(current_name))
    with col_type:
        projet_temp = df[df['id'] == project_options[selected_name]].iloc[0]
        st.metric("Type", projet_temp.get("type_projet", "—"))
    with col_prog:
        pct = projet_temp.get('progress_pct', 0)
        st.metric("Avancement", f"{pct}%")
        st.progress(float(pct) / 100)
   
    if project_options[selected_name] != st.session_state.current_project_id:
        st.session_state.current_project_id = project_options[selected_name]
        st.rerun()
   
    projet = df[df['id'] == st.session_state.current_project_id].iloc[0]
    st.subheader(projet["name"])
   
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a: st.metric("Client", projet.get("client_name", "—"))
    with col_b: st.metric("Statut", projet.get("statut", "—"))
    with col_c: st.metric("Début", projet.get('date_debut', '—'))
    with col_d: st.metric("Échéance", projet.get('date_fin_estimee', '—'))
   
    st.divider()
   
    # === UPLOAD PHOTOS (version debug) ===
    st.subheader("📸 Photos du chantier")
   
    uploaded_file = st.file_uploader(
        "Ajouter une photo", 
        type=["png", "jpg", "jpeg"], 
        key=f"photo_{st.session_state.current_project_id}"
    )
    
    col_btn, col_refresh = st.columns([1, 2])
    with col_btn:
        if uploaded_file and st.button("📤 Upload photo", type="primary"):
            url = upload_photo(st.session_state.current_project_id, uploaded_file)
            if url:
                st.success("✅ Photo uploadée avec succès !")
                st.rerun()
    
    with col_refresh:
        if st.button("🔄 Rafraîchir les photos"):
            st.rerun()
   
    # Affichage des photos
    photos = list_project_photos(st.session_state.current_project_id)
    if photos:
        st.write(f"{len(photos)} photo(s) :")
        cols = st.columns(3)
        for i, url in enumerate(photos):
            with cols[i % 3]:
                st.image(url, use_column_width=True)
    else:
        st.info("Aucune photo pour ce chantier pour le moment.")
   
    st.divider()
    show_todo_list()

# ============================================================
# PAGE : PLANNING & AGENDA (inchangé)
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
# PAGE : BIBLIOTHÈQUE TÂCHES
# ============================================================
elif st.session_state.current_page == "📋 Bibliothèque Tâches":
    st.subheader("📋 Bibliothèque de Tâches")
    
    df_lib = get_task_library()
    
    if df_lib.empty:
        st.warning("Aucune tâche trouvée dans la bibliothèque.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            categories = ["Toutes"] + sorted(df_lib['category'].unique().tolist())
            selected_cat = st.selectbox("Catégorie", categories)
        
        if selected_cat != "Toutes":
            filtered = df_lib[df_lib['category'] == selected_cat]
        else:
            filtered = df_lib.copy()
        
        with col2:
            subcats = ["Toutes"] + sorted(filtered['subcategory'].dropna().unique().tolist())
            selected_subcat = st.selectbox("Sous-catégorie", subcats)
        
        if selected_subcat != "Toutes":
            filtered = filtered[filtered['subcategory'] == selected_subcat]
        
        st.write(f"**{len(filtered)} tâche(s)**")
        
        for _, task in filtered.iterrows():
            with st.expander(f"**{task['name']}**"):
                st.write(task.get('description', ''))
                if st.button("➕ Ajouter au chantier actuel", key=f"add_{task['id']}"):
                    if st.session_state.current_project_id:
                        task_data = {
                            "name": task['name'],
                            "description": task.get('description'),
                            "category": task['category'],
                            "subcategory": task.get('subcategory'),
                            "status": "À faire",
                            "estimated_hours": 2.0
                        }
                        add_task_to_project(st.session_state.current_project_id, task_data)
                        st.success(f"Tâche ajoutée !")
                        st.rerun()
                    else:
                        st.warning("Sélectionne d'abord un chantier.")
    
    st.divider()
    show_todo_list()

# ============================================================
# AUTRES PAGES
# ============================================================
else:
    st.info(f"Page **{st.session_state.current_page}** en cours de développement.")
    show_todo_list()

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")
