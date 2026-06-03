import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="HD Full Concept - Projets", layout="wide", page_icon="🔊")

# ====================== HEADER ======================
st.markdown("""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <div style="background-color: #1a1a2e; color: white; padding: 8px 16px; border-radius: 8px; font-weight: bold; font-size: 22px;">
            HD FULL CONCEPT
        </div>
        <div>
            <h1 style="margin: 0; font-size: 26px;">Centralisation des Projets</h1>
            <p style="margin: 0; color: #666;">Le Son, L'Image, Le Service</p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("HD Full Concept")
    
    role = st.selectbox(
        "Votre rôle",
        ["Administrateur", "Technicien", "Programmeur C4", "Direction"],
        index=0
    )
    
    st.caption(f"Connecté en tant que : **{role}**")
    st.divider()
    
    page = st.radio("Navigation", [
        "📊 Tableau de bord",
        "📁 Fiche Chantier",
        "⚡ Encodage Rapide",
        "📅 Planning & Coordination",
        "📈 Rapports"
    ])

# ====================== DONNÉES ======================
projects_data = [
    {"id": 1, "name": "Villa Uccle - Home Cinéma Premium", "client": "M. & Mme. Lambert", "type": "Home Cinéma Control4", "statut": "En cours", "progress": 72, "is_c4": True},
    {"id": 2, "name": "Appartement Ixelles - Domotique Full C4", "client": "Famille Dubois", "type": "Domotique C4", "statut": "En cours", "progress": 45, "is_c4": True},
    {"id": 3, "name": "Boutique HD - Signage & Visio", "client": "HD Full Concept", "type": "Signage professionnel", "statut": "En cours", "progress": 88, "is_c4": False},
    {"id": 4, "name": "Résidence Waterloo - Salles Cinéma", "client": "M. Van der Berg", "type": "Salles de cinéma privées", "statut": "En préparation", "progress": 15, "is_c4": True},
]

events_data = [
    {"projet": "Villa Uccle", "type": "Problème", "desc": "Câblage HDMI instable", "date": "28/05", "resolu": True},
    {"projet": "Villa Uccle", "type": "Blocage C4", "desc": "Pairing remote SR-260", "date": "28/05", "resolu": False},
    {"projet": "Ixelles", "type": "Étape terminée", "desc": "Découverte réseau C4", "date": "30/05", "resolu": True},
]

# ====================== PAGES ======================

if page == "📊 Tableau de bord":
    st.subheader("Vue d'ensemble des chantiers")
    
    df = pd.DataFrame(projects_data)
    st.dataframe(df[["name", "client", "type", "statut", "progress"]], use_container_width=True, hide_index=True)
    
    if role == "Administrateur":
        st.success("En tant qu'Administrateur, vous avez une vue complète sur tous les chantiers.")
    elif role == "Technicien":
        st.info("Vous ne voyez ici que les chantiers qui vous sont assignés (simulation).")

elif page == "📁 Fiche Chantier":
    st.subheader("Fiche Chantier détaillée")
    
    selected = st.selectbox("Choisir un chantier", [p["name"] for p in projects_data])
    projet = next(p for p in projects_data if p["name"] == selected)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Client", projet["client"])
        st.metric("Type", projet["type"])
    with col2:
        st.metric("Statut", projet["statut"])
        st.progress(projet["progress"] / 100, text=f"Avancement : {projet['progress']}%")
    
    st.markdown("### Événements du chantier")
    for ev in events_data:
        if ev["projet"] in selected:
            color = "🟢" if ev["resolu"] else "🔴"
            st.write(f"{color} **{ev['date']}** - {ev['type']} : {ev['desc']}")
    
    if role in ["Administrateur", "Programmeur C4"]:
        st.text_area("Ajouter une note / mise à jour technique")

elif page == "⚡ Encodage Rapide":
    st.subheader("⚡ Encodage Rapide (mobile friendly)")
    
    with st.form("encode_form"):
        chantier = st.selectbox("Chantier", [p["name"] for p in projects_data])
        type_event = st.selectbox("Type d'événement", ["Problème", "Réussite", "Étape terminée", "Blocage technique C4"])
        description = st.text_area("Description courte")
        
        if st.form_submit_button("📤 Envoyer l'information"):
            st.success(f"Information enregistrée sur le chantier : {chantier}")
            st.balloons()

elif page == "📅 Planning & Coordination":
    st.subheader("Planning & Coordination d'équipe")
    
    st.write("**Affectations de la semaine**")
    planning_data = [
        {"Date": "03/06", "Personne": "Jean Installer", "Chantier": "Villa Uccle", "Notes": "Technicien principal"},
        {"Date": "06/06", "Personne": "Marie C4", "Chantier": "Ixelles", "Notes": "Support technique C4"},
        {"Date": "06/06", "Personne": "Antoine Grandjean", "Chantier": "Boutique HD", "Notes": "Administrateur - Samedi"},
    ]
    st.dataframe(pd.DataFrame(planning_data), use_container_width=True, hide_index=True)
    
    if role == "Administrateur":
        st.success("Vous pouvez modifier le planning (fonctionnalité à développer).")

elif page == "📈 Rapports":
    st.subheader("Rapports & Débriefs")
    st.info("Fonctionnalité de génération de rapports hebdomadaires (à développer).")

# ====================== FOOTER ======================
st.divider()
st.caption("HD Full Concept SA — Prototype interne — Juin 2026")
