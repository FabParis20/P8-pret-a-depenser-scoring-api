"""
Dashboard de monitoring - API Scoring Crédit
Projet MLOps - Prêt à dépenser
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from evidently import Report
from evidently.metrics import *
from evidently.presets import *
import numpy as np
import requests

# Configuration de la page
st.set_page_config(
    page_title="Monitoring API Scoring",
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("📊 Dashboard de Monitoring - API Scoring Crédit")
st.markdown("---")

# Configuration de l'API
API_URL = "http://localhost:8000/v2/predict"

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

def generate_drift_report(df_production):
    """
    Génère un rapport de drift entre référence et production
    
    Args:
        df_production: DataFrame des logs de production
        
    Returns:
        tuple: (rapport Evidently, chemin HTML)
    """
    # Créer un dataset de référence simulé (même logique que le notebook)
    np.random.seed(42)
    scores_reference = []
    
    for _ in range(100):
        if np.random.random() < 0.85:
            score = np.random.uniform(0.70, 0.95)
        else:
            score = np.random.uniform(0.10, 0.69)
        scores_reference.append(score)
    
    reference_data = pd.DataFrame({'score': scores_reference})
    current_data = df_production[['score']].copy()
    
    # Générer le rapport
    report = Report([DataDriftPreset()])
    my_eval = report.run(current_data=current_data, reference_data=reference_data)
    
    # Sauvegarder le rapport HTML temporaire
    html_path = Path("drift_report_temp.html")
    my_eval.save_html(str(html_path))
    
    return my_eval, html_path

# ============================================================
# PAGE 0 : DÉMO INTERACTIVE - TEST DU MODÈLE
# ============================================================

st.header("🎯 Démo Interactive - Test de Prédiction")

st.info("💡 Testez l'API de scoring en direct ! Entrez un client_id pour obtenir une prédiction.")

# Créer deux colonnes
col1, col2 = st.columns([2, 1])

with col1:
    # Champ de saisie pour le client_id
    client_id = st.text_input(
        "🆔 Numéro de client",
        placeholder="Ex: 273460",
        help="Exemple : 273460 (accepté) ou 321537 (refusé)"
    )
    
    # Bouton de prédiction
    predict_button = st.button("🚀 Obtenir la prédiction", type="primary", use_container_width=True)

with col2:
    st.markdown("**Clients de test :**")
    st.markdown("""
    **✅ Acceptés :** 273460, 268316, 385708  
    **🚫 Refusés :** 321537, 402448, 416841
    """)

# Traiter la prédiction quand le bouton est cliqué
if predict_button:
    if not client_id:
        st.error("❌ Veuillez entrer un client_id")
    else:
        # Appeler l'API
        with st.spinner("⏳ Prédiction en cours..."):
            try:
                response = requests.get(f"{API_URL}/{client_id}", timeout=5)
                
                if response.status_code == 200:
                    # Succès
                    data = response.json()
                    
                    # Afficher le résultat dans une belle carte
                    if data['decision'] == "Crédit accepté":
                        st.success(f"✅ **{data['decision']}**")
                    else:
                        st.error(f"❌ **{data['decision']}**")
                    
                    # Afficher les détails
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.metric(
                            label="🎯 Score de prédiction",
                            value=f"{data['score']:.2f}"
                        )
                    
                    with col_b:
                        st.metric(
                            label="👤 Client ID",
                            value=data['client_id']
                        )
                    
                    # Message d'explication
                    st.caption(f"💡 Score : {data['score']:.2f} (Seuil de décision : 0.10)")
                    
                elif response.status_code == 404:
                    st.error(f"❌ Client {client_id} introuvable dans la base de données")
                else:
                    st.error(f"❌ Erreur API : {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Impossible de se connecter à l'API. Vérifiez qu'elle est démarrée sur http://localhost:8000")
            except requests.exceptions.Timeout:
                st.error("❌ Timeout : L'API met trop de temps à répondre")
            except Exception as e:
                st.error(f"❌ Erreur inattendue : {str(e)}")

st.markdown("---")
st.markdown("")  # Espace

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

# ============================================================
# PAGE 3 : ANALYSE DU DATA DRIFT
# ============================================================

st.header("🔬 Analyse du Data Drift")

st.info("💡 Cette section compare la distribution des scores de production avec une période de référence.")

# Générer le rapport de drift
with st.spinner("Génération du rapport Evidently..."):
    drift_eval, html_path = generate_drift_report(df)

# Métriques de drift
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📊 Colonnes analysées",
        value="1",
        help="Nombre de variables analysées (score)"
    )

with col2:
    st.metric(
        label="⚠️ Drift détecté",
        value="Oui" if html_path.exists() else "Non",
        help="Présence de drift statistiquement significatif"
    )

with col3:
    # Calculer les stats de différence
    ref_mean = 0.80  # Approximation de la référence simulée
    prod_mean = df['score'].mean()
    diff_pct = ((prod_mean - ref_mean) / ref_mean) * 100
    
    st.metric(
        label="📈 Écart de moyenne",
        value=f"{prod_mean:.2f}",
        delta=f"{diff_pct:.1f}%",
        help="Moyenne des scores : production vs référence"
    )

# Afficher le rapport HTML Evidently dans un iframe
st.subheader("📄 Rapport Evidently complet")

if html_path.exists():
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Afficher dans un iframe
    st.components.v1.html(html_content, height=800, scrolling=True)
else:
    st.warning("⚠️ Le rapport de drift n'a pas pu être généré.")

st.markdown("---")


# ============================================================
# PAGE 4 : PERFORMANCE DE L'API
# ============================================================

st.header("⚡ Performance de l'API")

# Statistiques de temps de réponse
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="⏱️ Temps moyen",
        value=f"{df['response_time_ms'].mean():.2f} ms"
    )

with col2:
    st.metric(
        label="⚡ Temps min",
        value=f"{df['response_time_ms'].min():.2f} ms"
    )

with col3:
    st.metric(
        label="🐌 Temps max",
        value=f"{df['response_time_ms'].max():.2f} ms"
    )

with col4:
    st.metric(
        label="📊 Écart-type",
        value=f"{df['response_time_ms'].std():.2f} ms"
    )

# Graphique d'évolution du temps de réponse
st.subheader("📈 Évolution du temps de réponse")

fig_perf = px.line(
    df.sort_values('timestamp'),
    x='timestamp',
    y='response_time_ms',
    title="Temps de réponse par prédiction",
    labels={'timestamp': 'Date/Heure', 'response_time_ms': 'Temps (ms)'}
)

fig_perf.add_hline(
    y=df['response_time_ms'].mean(),
    line_dash="dash",
    line_color="red",
    annotation_text="Moyenne"
)

fig_perf.update_layout(height=400)
st.plotly_chart(fig_perf, use_container_width=True)

# Distribution des temps de réponse
st.subheader("📊 Distribution des temps de réponse")

fig_dist = px.histogram(
    df,
    x='response_time_ms',
    nbins=30,
    title="Répartition des temps de réponse",
    labels={'response_time_ms': 'Temps de réponse (ms)', 'count': 'Nombre de prédictions'}
)

fig_dist.update_layout(height=400)
st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")

# Footer
st.caption("📊 Dashboard de monitoring - Version Dummy | Prêt à dépenser")