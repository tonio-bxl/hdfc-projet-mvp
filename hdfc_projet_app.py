import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide")

DB_PATH = "hdfc_projects.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, name TEXT, role TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY, name TEXT, client_name TEXT, 
        type_projet TEXT, statut TEXT, progress_pct REAL, is_c4 INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY, project_id INTEGER, user_id INTEGER,
        timestamp TEXT, event_type TEXT, description TEXT, est_resolu INTEGER)''')
    
    conn.commit()
    
    # Seed simple et propre
    if c.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
        c.executemany("""INSERT INTO projects (name, client_name, type_projet, statut, progress_pct, is_c4) VALUES (?,?,?,?,?,?)""", [
            ("Villa Uccle - Home Cinéma Premium", "M. & Mme. Lambert", "Home Cinéma Control4", "En cours", 72, 1),
            ("Appartement Ixelles - Domotique C4", "Famille Dubois", "Domotique C4", "En cours", 45, 1),
            ("Boutique HD - Signage", "HD Full Concept", "Signage & Visio", "En cours", 88, 0),
            ("Résidence Waterloo - Cinéma Privé", "M. Van der Berg", "Salles de cinéma", "En préparation", 15, 1),
        ])
        
        c.executemany("""INSERT INTO users (name, role) VALUES (?,?)""", [
            ("Antoine Grandjean", "Administrateur"),
            ("Jean Installer", "Technicien"),
            ("Marie C4", "Programmeur C4"),
            ("Pierre Direction", "Direction"),
        ])
        
        c.executemany("""INSERT INTO events (project_id, user_id, timestamp, event_type, description, est_resolu) VALUES (?,?,?,?,?,?)""", [
            (1, 2, "2026-05-28 09:15", "Problème", "Câblage HDMI instable sur zone salon", 1),
            (1, 3, "2026-05-28 14:30", "Blocage technique C4", "Problème pairing remote SR-260", 0),
            (2, 2, "2026-05-30 11:45", "Étape terminée", "Découverte réseau C4 terminée", 1),
            (3, 2, "2026-06-01 08:30", "Problème", "Écran signage ne s'allume pas", 0),
        ])
        conn.commit()
    conn.close()

init_db()

st.title("HD Full Concept - Centralisation Projets (MVP)")

role = st.sidebar.selectbox("Rôle", ["Administrateur", "Technicien", "Programmeur C4", "Direction"])

st.success(f"Connecté en tant que : {role}")

conn = get_conn()
projects = pd.read_sql("SELECT * FROM projects", conn)
st.subheader("Chantiers")
st.dataframe(projects, use_container_width=True, hide_index=True)

st.subheader("Événements récents")
events = pd.read_sql("""
    SELECT e.timestamp, p.name as projet, e.event_type, e.description, e.est_resolu
    FROM events e
    JOIN projects p ON e.project_id = p.id
    ORDER BY e.timestamp DESC
""", conn)
st.dataframe(events, use_container_width=True, hide_index=True)
conn.close()

st.info("Application MVP corrigée et simplifiée pour Streamlit Cloud. Tu peux maintenant tester les différentes vues selon le rôle.")
