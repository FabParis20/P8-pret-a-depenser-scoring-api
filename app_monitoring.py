"""
Dashboard de monitoring - API Scoring Crédit
Projet MLOps - Prêt à dépenser
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Monitoring API Scoring",
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("📊 Dashboard de Monitoring - API Scoring Crédit")
st.markdown("---")

# Chemin vers le fichier de logs
LOGS_FILE = Path("data/prod/logs_production.csv")

# Fonction pour charger les données
@st.cache_data
def load_data():
    """
    Charge les données de logs de production
    
    Returns:
        pd.DataFrame: Données des prédictions
    """
    if LOGS_FILE.exists():
        df = pd.read_csv(LOGS_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    else:
        return None

# Charger les données
df = load_data()

# Vérifier que les données existent
if df is None or df.empty:
    st.error("❌ Aucune donnée de production disponible.")
    st.info("💡 Lancez l'API et effectuez quelques prédictions pour générer des données.")
    st.stop()

# ============================================================
# PAGE 1 : VUE D'ENSEMBLE
# ============================================================

st.header("📈 Vue d'ensemble")

# Calcul des métriques
total_predictions = len(df)
nb_acceptes = len(df[df['decision'] == 'Crédit accepté'])
nb_refuses = len(df[df['decision'] == 'Crédit refusé'])
taux_acceptation = (nb_acceptes / total_predictions) * 100
score_moyen = df['score'].mean()
temps_reponse_moyen = df['response_time_ms'].mean()

# Affichage des KPIs en colonnes
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📊 Total de prédictions",
        value=f"{total_predictions}"
    )
    st.metric(
        label="⏱️ Temps de réponse moyen",
        value=f"{temps_reponse_moyen:.2f} ms"
    )

with col2:
    st.metric(
        label="✅ Crédits acceptés",
        value=f"{nb_acceptes}",
        delta=f"{taux_acceptation:.1f}%"
    )
    st.metric(
        label="📉 Score moyen",
        value=f"{score_moyen:.2f}"
    )

with col3:
    st.metric(
        label="❌ Crédits refusés",
        value=f"{nb_refuses}",
        delta=f"{100-taux_acceptation:.1f}%"
    )

st.markdown("---")

# ============================================================
# PAGE 2 : DISTRIBUTION DES SCORES
# ============================================================

st.header("📊 Distribution des scores")

# Créer deux colonnes pour les graphiques
col1, col2 = st.columns(2)

with col1:
    # Histogramme des scores
    st.subheader("Distribution des scores de prédiction")
    
    fig_hist = px.histogram(
        df,
        x='score',
        nbins=20,
        title="Répartition des scores",
        labels={'score': 'Score de prédiction', 'count': 'Nombre de prédictions'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig_hist.update_layout(
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    # Graphique en camembert (pie chart) des décisions
    st.subheader("Répartition des décisions")
    
    decisions_count = df['decision'].value_counts()
    
    fig_pie = px.pie(
        values=decisions_count.values,
        names=decisions_count.index,
        title="Acceptation vs Refus",
        color_discrete_sequence=['#2ecc71', '#e74c3c']
    )
    
    fig_pie

# ============================================================
# INFORMATIONS
# ============================================================

st.header("ℹ️ Informations")

# Afficher un échantillon des dernières prédictions
st.subheader("Dernières prédictions (10 plus récentes)")

dernières_predictions = df.sort_values('timestamp', ascending=False).head(10)

st.dataframe(
    dernières_predictions[['timestamp', 'client_id', 'score', 'decision', 'response_time_ms']],
    use_container_width=True,
    hide_index=True
)
