#!/usr/bin/env python3
"""
HD Full Concept SA - Application interne MVP : Centralisation des Projets
Prototype Streamlit complet et fonctionnel
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import base64
from io import BytesIO

DB_PATH = "hdfc_projects.db"

st.set_page_config(
    page_title="HD Full Concept | Centralisation Projets",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        client_name TEXT,
        type_projet TEXT,
        statut TEXT DEFAULT 'En cours',
        progress_pct REAL DEFAULT 0,
        date_debut TEXT,
        date_fin_estimee TEXT,
        adresse TEXT,
        notes TEXT,
        ca_estime_htva REAL,
        is_c4 INTEGER DEFAULT 0
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        user_id INTEGER,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT,
        description TEXT,
        photo_b64 TEXT,
        est_resolu INTEGER DEFAULT 0,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        user_id INTEGER,
        assignment_date TEXT,
        notes TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        seed_mock_data(conn)
    conn.close()

def seed_mock_data(conn):
    c = conn.cursor()
    
    users_data = [
        (1, "Antoine Grandjean", "Administrateur", "antoine.grandjean@gmail.com"),
        (2, "Jean Installer", "Technicien", "jean@hdfullconcept.be"),
        (3, "Marie C4-Programmer", "Programmeur C4", "marie@hdfullconcept.be"),
        (4, "Pierre Direction", "Direction", "pierre@hdfullconcept.be"),
        (5, "Sophie Commerciale", "Commercial", "sophie@hdfullconcept.be")
    ]
    c.executemany("INSERT INTO users (id, name, role, email) VALUES (?, ?, ?, ?)", users_data)
    
    projects_data = [
        (1, "Villa Uccle - Home Cinéma Premium + Acoustique", "M. & Mme. Lambert", 
         "Home Cinéma Control4 + Acoustique", "En cours", 72, "2026-04-10", "2026-07-15", 
         "Uccle, Bruxelles", "Projet haut de gamme. Apport marché acoustique.", 48500, 1),
        (2, "Appartement Ixelles - Domotique Full C4 + Multiroom", "Famille Dubois", 
         "Domotique résidentielle C4", "En cours", 45, "2026-05-20", "2026-08-10", 
         "Ixelles, Bruxelles", "Reprise écosystème C4 via Prestige.", 62000, 1),
        (3, "Boutique HD Full Concept - Signage Digital + Visio", "HD Full Concept (interne)", 
         "Signage & Visio professionnelle", "En cours", 88, "2026-03-01", "2026-06-30", 
         "Chaussée de Waterloo, Uccle", "Optimisation présence magasin. 2 personnes min le samedi.", 18500, 0),
        (4, "Résidence Waterloo - Salles de Cinéma Privée (x2)", "M. Van der Berg", 
         "Salles de cinéma privées", "En préparation", 15, "2026-06-15", "2026-09-30", 
         "Waterloo", "Nouveau marché à développer (potentiel important).", 125000, 1),
        (5, "Projet Test Acoustique - Apport Client Existant", "Client Test Acoustique", 
         "Intégration acoustique premium", "En cours", 60, "2026-05-01", "2026-07-05", 
         "Bruxelles", "Validation apport marché acoustique et clientèle existante.", 28000, 0)
    ]
    c.executemany("""INSERT INTO projects 
        (id, name, client_name, type_projet, statut, progress_pct, date_debut, date_fin_estimee, adresse, notes, ca_estime_htva, is_c4) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", projects_data)
    
    events_data = [
        (1, 1, 2, "2026-05-28 09:15", "Problème", "Câblage HDMI 2.1 instable sur zone salon. Client agacé.", None, 1),
        (2, 1, 3, "2026-05-28 14:30", "Blocage technique C4", "SR-260 remote pairing échec après firmware update.", None, 0),
        (3, 1, 1, "2026-05-29 10:00", "Réussite", "Test acoustique pièce principale validé à 100% par le client.", None, 1),
        (4, 2, 2, "2026-05-30 11:45", "Étape terminée", "Découverte réseau C4 terminée. 12 zones identifiées.", None, 1),
        (5, 3, 2, "2026-06-01 08:30", "Problème", "Écran signage 55\" ne s'allume pas après mise à jour firmware.", None, 0),
        (6, 4, 5, "2026-06-02 16:20", "Commentaire général", "RDV client demain 10h pour validation scope cinéma privée.", None, 1),
        (7, 1, 3, "2026-06-02 09:00", "Mise à jour C4", "Reprise écosystème via Prestige terminée. Licences activées.", None, 1)
    ]
    c.executemany("""INSERT INTO events 
        (project_id, user_id, timestamp, event_type, description, photo_b64, est_resolu) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""", events_data)
    
    assignments_data = [
        (1, 1, 2, "2026-06-03", "Mardi - Technicien principal"),
        (2, 1, 3, "2026-06-03", "Mardi - Programmeur C4"),
        (3, 3, 2, "2026-06-06", "Samedi - Couverture minimum 2 personnes requise"),
        (4, 3, 1, "2026-06-06", "Samedi - Administrateur (roulement)"),
        (5, 4, 5, "2026-06-04", "Mercredi - Suivi commercial"),
    ]
    c.executemany("""INSERT INTO assignments 
        (project_id, user_id, assignment_date, notes) 
        VALUES (?, ?, ?, ?)""", assignments_data)
    
    conn.commit()

def img_to_b64(uploaded_file):
    if uploaded_file is not None:
        try:
            return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        except:
            return None
    return None

def b64_to_img(b64_str):
    if b64_str:
        try:
            return BytesIO(base64.b64decode(b64_str))
        except:
            return None
    return None

def main():
    init_db()
    
    if "role" not in st.session_state:
        st.session_state.role = "Administrateur"
        st.session_state.user_id = 1
        st.session_state.user_name = "Antoine Grandjean"
        st.session_state.current_project_id = None
    
    with st.sidebar:
        st.header("HD Full Concept")
        st.caption("LE SON, L'IMAGE, LE SERVICE.")
        st.divider()
        
        selected_role = st.selectbox(
            "Mode démo (rôle)", 
            ["Administrateur", "Technicien", "Programmeur C4", "Direction", "Commercial"],
            index=["Administrateur", "Technicien", "Programmeur C4", "Direction", "Commercial"].index(st.session_state.role)
        )
        
        if selected_role != st.session_state.role:
            st.session_state.role = selected_role
            if selected_role == "Technicien":
                st.session_state.user_id = 2
                st.session_state.user_name = "Jean Installer"
            elif selected_role == "Programmeur C4":
                st.session_state.user_id = 3
                st.session_state.user_name = "Marie C4-Programmer"
            elif selected_role == "Direction":
                st.session_state.user_id = 4
                st.session_state.user_name = "Pierre Direction"
            elif selected_role == "Commercial":
                st.session_state.user_id = 5
                st.session_state.user_name = "Sophie Commerciale"
            else:
                st.session_state.user_id = 1
                st.session_state.user_name = "Antoine Grandjean"
            st.rerun()
        
        st.caption(f"Connecté : {st.session_state.user_name} ({st.session_state.role})")
        st.divider()
        
        page = st.radio("Navigation", [
            "📊 Tableau de bord",
            "📁 Fiche Chantier",
            "⚡ Encodage Rapide",
            "📅 Planning & Coordination",
            "📈 Rapports & Débriefs",
            "🔧 Module Control4",
            "⚙️ Administration"
        ])
    
    if page == "📊 Tableau de bord":
        st.title("📊 Tableau de bord - Projets HD Full Concept")
        
        conn = get_conn()
        projects = pd.read_sql("SELECT * FROM projects ORDER BY progress_pct DESC", conn)
        conn.close()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Chantiers actifs", len(projects[projects['statut'].isin(['En cours', 'En préparation'])]))
        col2.metric("Projets Control4", len(projects[projects['is_c4'] == 1]))
        col3.metric("Progression moyenne", f"{projects['progress_pct'].mean():.0f}%")
        col4.metric("Total CA estimé", f"{projects['ca_estime_htva'].sum():,.0f} €")
        
        st.subheader("Liste des chantiers")
        st.dataframe(projects[['name', 'client_name', 'type_projet', 'statut', 'progress_pct']], use_container_width=True, hide_index=True)
        
        if not projects.empty:
            selected = st.selectbox("Ouvrir la fiche d'un chantier", projects['name'].tolist())
            if st.button("📂 Ouvrir la fiche"):
                st.session_state.current_project_id = int(projects[projects['name'] == selected]['id'].values[0])
                st.rerun()
    
    elif page == "📁 Fiche Chantier":
        if st.session_state.current_project_id is None:
            st.warning("Aucun chantier sélectionné. Retour au Tableau de bord.")
            if st.button("← Retour au Tableau de bord"):
                st.rerun()
            return
        
        conn = get_conn()
        project = conn.execute("SELECT * FROM projects WHERE id = ?", (st.session_state.current_project_id,)).fetchone()
        conn.close()
        
        if not project:
            st.error("Chantier introuvable")
            return
        
        st.header(project['name'])
        st.caption(f"Client : {project['client_name']} | Type : {project['type_projet']}")
        
        tab1, tab2 = st.tabs(["📜 Historique des événements", "➕ Ajouter un événement"])
        
        with tab1:
            conn = get_conn()
            events = pd.read_sql("""
                SELECT e.*, u.name as user_name 
                FROM events e 
                JOIN users u ON e.user_id = u.id 
                WHERE e.project_id = ? 
                ORDER BY e.timestamp DESC
            """, conn, params=(st.session_state.current_project_id,))
            conn.close()
            
            if events.empty:
                st.info("Aucun événement pour ce chantier.")
            else:
                for _, ev in events.iterrows():
                    with st.expander(f"{ev['timestamp'][:16]} — {ev['event_type']} par {ev['user_name']}"):
                        st.write(ev['description'])
                        if ev['photo_b64']:
                            img = b64_to_img(ev['photo_b64'])
                            if img:
                                st.image(img, width=300)
        
        with tab2:
            with st.form("add_event"):
                event_type = st.selectbox("Type d'événement", 
                    ["Problème", "Réussite", "Étape terminée", "Blocage technique C4", "Mise à jour C4", "Commentaire général"])
                description = st.text_area("Description")
                photo = st.file_uploader("Photo (optionnelle)", type=["jpg", "png", "jpeg"])
                resolved = st.checkbox("Marquer comme résolu")
                
                if st.form_submit_button("Enregistrer l'événement"):
                    photo_b64 = img_to_b64(photo)
                    conn = get_conn()
                    conn.execute("""
                        INSERT INTO events (project_id, user_id, event_type, description, photo_b64, est_resolu)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (st.session_state.current_project_id, st.session_state.user_id, event_type, description, photo_b64, 1 if resolved else 0))
                    conn.commit()
                    conn.close()
                    st.success("Événement enregistré avec succès !")
                    st.rerun()
    
    elif page == "⚡ Encodage Rapide":
        st.title("⚡ Encodage Rapide sur Chantier")
        st.caption("Formulaire simple pour techniciens et programmeurs")
        
        conn = get_conn()
        projects = pd.read_sql("SELECT * FROM projects", conn)
        conn.close()
        
        with st.form("quick_form"):
            proj_name = st.selectbox("Chantier", projects['name'].tolist())
            proj_id = int(projects[projects['name'] == proj_name]['id'].values[0])
            
            event_type = st.selectbox("Type", ["Problème", "Réussite", "Étape terminée", "Blocage technique C4"])
            description = st.text_area("Description courte")
            photo = st.file_uploader("Photo", type=["jpg", "png"])
            
            if st.form_submit_button("📤 Envoyer"):
                photo_b64 = img_to_b64(photo)
                conn = get_conn()
                conn.execute("""
                    INSERT INTO events (project_id, user_id, event_type, description, photo_b64)
                    VALUES (?, ?, ?, ?, ?)
                """, (proj_id, st.session_state.user_id, event_type, description, photo_b64))
                conn.commit()
                conn.close()
                st.success("Information remontée avec succès !")
                st.balloons()
    
    elif page == "📅 Planning & Coordination":
        st.title("📅 Planning & Coordination")
        conn = get_conn()
        assignments = pd.read_sql("""
            SELECT a.assignment_date, p.name as projet, u.name as personne, a.notes
            FROM assignments a
            JOIN projects p ON a.project_id = p.id
            JOIN users u ON a.user_id = u.id
            ORDER BY a.assignment_date
        """, conn)
        conn.close()
        st.dataframe(assignments, use_container_width=True, hide_index=True)
    
    elif page == "📈 Rapports & Débriefs":
        st.title("📈 Rapports & Débriefs")
        st.info("Fonctionnalité de rapport automatique disponible dans la version complète. Tu peux l'étendre facilement.")
    
    elif page == "🔧 Module Control4":
        st.title("🔧 Module Control4 / IT")
        st.info("Module dédié aux projets Control4 avec suivi technique et base de connaissances (disponible dans la version complète).")
    
    elif page == "⚙️ Administration":
        if st.session_state.role != "Administrateur":
            st.error("Accès réservé à l'Administrateur")
            return
        st.title("⚙️ Administration")
        st.success("Section réservée à l'administrateur (vue complète, statistiques, etc.)")

if __name__ == "__main__":
    main()
