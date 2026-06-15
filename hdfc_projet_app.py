import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key"]
supabase: Client = create_client(url, key)

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

# ====================== FONCTIONS ======================
def get_projects():
    response = supabase.table("projects").select("*").execute()
    return pd.DataFrame(response.data)

def create_project(data):
    supabase.table("projects").insert(data).execute()

# ====================== PAGES ======================

if st.session_state.current_page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    df = get_projects()
    
    for _, proj in df.iterrows():
        col1, col2, col3, col4 = st.columns([4.5, 1.5, 1.5, 1.5])
        with col1:
            if st.button(f"📂 {proj['name']}", key=f"open_{proj['id']}"):
                st.session_state.current_project_id = proj['id']
                st.session_state.current_page = "📁 Fiche Chantier"
                st.rerun()
        with col2:
            st.progress(float(proj['progress_pct']) / 100, text=f"{proj['progress_pct']}%")
        with col3:
            echeance = proj.get('date_fin_estimee', 'N/A')
            st.caption(f"📅 {echeance}")
        with col4:
            st.caption(proj['statut'])
        st.divider()

elif st.session_state.current_page == "📁 Fiche Chantier":
    st.markdown("""
        <style>
        .stMarkdown, .stMetric, .stSelectbox, .stButton {
            font-size: 14px !important;
        }
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

elif st.session_state.current_page == "➕ Créer un chantier":
    if role != "Administrateur":
        st.error("Accès réservé à l'Administrateur.")
    else:
        st.subheader("➕ Créer un nouveau chantier")
        
        with st.form("create_project_form"):
            nom_projet = st.text_input("Nom du projet *", placeholder="Ex: Villa Uccle - Home Cinéma + Acoustique")
            nom_client = st.text_input("Nom du client *")
            
            type_chantier = st.selectbox("Type de chantier *", [
                "Home Cinéma Control4",
                "Domotique résidentielle C4",
                "Intégration acoustique premium",
                "Salles de cinéma privées",
                "Signage & Visio professionnelle",
                "Audio multiroom",
                "Autre"
            ])
            
            adresse = st.text_input("Adresse complète *", placeholder="Rue + n° + boîte + code postal + ville")
            telephone = st.text_input("Téléphone *")
            email = st.text_input("Email *")
            
            col_statut, col_echeance = st.columns(2)
            with col_statut:
                statut = st.selectbox("Statut *", [
                    "Offre à faire",
                    "Devis envoyé",
                    "Devis signé / Commande confirmée",
                    "En préparation",
                    "En cours",
                    "En pause",
                    "Terminé"
                ])
            with col_echeance:
                date_echeance = st.date_input("Date d'échéance estimée *", value=date.today())
            
            ca_estime = st.number_input("CA estimé HTVA (€)", min_value=0, step=1000)
            is_c4 = st.checkbox("Projet Control4")
            
            notes = st.text_area("Notes / Description", height=100)
            
            submitted = st.form_submit_button("✅ Créer le chantier", type="primary")
            
            if submitted:
                if not nom_projet or not nom_client or not adresse or not telephone or not email:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    data = {
                        "name": nom_projet,
                        "client_name": nom_client,
                        "type_projet": type_chantier,
                        "adresse": adresse,
                        "statut": statut,
                        "date_fin_estimee": str(date_echeance),
                        "ca_estime_htva": ca_estime,
                        "is_c4": 1 if is_c4 else 0,
                        "notes": notes
                    }
                    create_project(data)
                    st.success("✅ Chantier créé avec succès !")
                    st.balloons()

else:
    st.info(f"Page **{st.session_state.current_page}** en cours de développement.")

st.divider()
st.caption("HD Full Concept SA — Prototype Supabase | Juin 2026")

# ====================== TO-DO LIST ======================
st.markdown("---")
st.markdown("### 📋 To-Do List (à faire ensuite)")

st.markdown("""
- [ ] Ajouter les tâches dans la fiche chantier (depuis la bibliothèque)
- [ ] Afficher l'historique des événements + photos dans la fiche
- [ ] Upload photos + documents dans la création et la fiche
- [ ] Note vocale + transcription IA (plus tard)
- [ ] Améliorer la vue Planning & Agenda
- [ ] Gestion des rôles (technicien ne voit que ses chantiers)
- [ ] Export PDF d'une fiche chantier
""")
