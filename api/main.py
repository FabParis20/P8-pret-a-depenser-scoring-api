# api/main.py
"""
API de scoring de crédit - Version Dummy
Projet MLOps - Prêt à dépenser
"""

import json
import random
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
from datetime import datetime
from time import time
import pickle
import pandas as pd
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application
    - Avant yield : exécuté au STARTUP
    - Après yield : exécuté au SHUTDOWN
    """
    # === STARTUP : Chargement des assets ===
    print("\n" + "="*60)
    print("🚀 CHARGEMENT DES ASSETS DE PRODUCTION")
    print("="*60)
    
    # 1️⃣ Charger le modèle
    model_path = Path(__file__).parent.parent / "models" / "model.pkl"
    print(f"\n📦 Chargement du modèle depuis : {model_path}")
    start = time()
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    load_time = (time() - start) * 1000
    print(f"✅ Modèle chargé en {load_time:.2f} ms")
    print(f"   Type : {type(model).__name__}")
    print(f"   Features attendues : {model.n_features_in_}")
    
    # 2️⃣ Charger les données
    data_path = Path(__file__).parent.parent / "data" / "prod" / "X_test_sample.pkl"
    print(f"\n📊 Chargement des données depuis : {data_path}")
    start = time()
    
    X_test_sample = pd.read_pickle(data_path)
    
    load_time = (time() - start) * 1000
    print(f"✅ Données chargées en {load_time:.2f} ms")
    print(f"   Shape : {X_test_sample.shape}")
    print(f"   Index (premiers IDs) : {X_test_sample.index[:5].tolist()}")
    
    # 3️⃣ Vérification
    print(f"\n🔍 Vérification de compatibilité...")
    if model.n_features_in_ == X_test_sample.shape[1]:
        print(f"✅ Compatibilité OK : {model.n_features_in_} features")
    else:
        print(f"⚠️  Incompatibilité : modèle={model.n_features_in_}, données={X_test_sample.shape[1]}")
    
    # Stocker dans ml_models pour accès dans les routes
    ml_models["model"] = model
    ml_models["X_test_sample"] = X_test_sample
    
    print("\n" + "="*60)
    print("✅ CHARGEMENT TERMINÉ - API PRÊTE")
    print("="*60 + "\n")
    
    # === YIELD : L'API fonctionne ici ===
    yield
    
    # === SHUTDOWN : Nettoyage (optionnel) ===
    print("\n🛑 Arrêt de l'API - Nettoyage...")
    ml_models.clear()

# Création de l'application FastAPI
app = FastAPI(
    title="API Scoring Crédit",
    description="API de prédiction de scoring pour les demandes de crédit",
    version="0.1.0-dummy",
    lifespan=lifespan  # ← Ajouter cette ligne
)

# Dictionnaire pour stocker les assets de production
ml_models = {}

# Avec lifespan, on utilise un dictionnaire app.state
# Plus propre et recommandé par FastAPI

# Chargement de la base clients fictive au démarrage (une seule fois !)
CLIENTS_FILE = Path(__file__).parent / "clients_dummy.json"

with open(CLIENTS_FILE, "r") as f:
    clients_db = json.load(f)

print(f"✅ Base clients chargée : {len(clients_db)} clients disponibles")

# Fichier de logs pour la production
LOGS_FILE = Path(__file__).parent.parent / "data" / "prod" / "logs_production.csv"

# Créer le fichier avec en-têtes s'il n'existe pas
if not LOGS_FILE.exists():
    with open(LOGS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "client_id", 
            "score",
            "decision",
            "response_time_ms"
        ])
    print(f"✅ Fichier de logs créé : {LOGS_FILE}")
else:
    print(f"✅ Fichier de logs existant : {LOGS_FILE}")

# Modèle de sortie de la prédiction
class PredictionOut(BaseModel):
    client_id: int
    score: float  # Probabilité entre 0 et 1
    decision: str  # "Crédit accepté" ou "Crédit refusé"
    threshold: float  # Seuil appliqué
    timestamp: str  # Horodatage ISO format

# Modèle de prédiction dummy
def dummy_model_predict(client_id: str, features: dict) -> float:
    """
    Modèle dummy qui simule un dataset déséquilibré :
    - 90% : bon payeur (score > 0.70)
    - 10% : mauvais payeur (score < 0.70)
    
    Args:
        client_id: ID du client (utilisé comme seed pour reproductibilité)
        features: Dictionnaire avec les caractéristiques du client
        
    Returns:
        float: Score de prédiction entre 0 et 1
    """
    # Utiliser l'ID comme seed pour avoir toujours le même résultat pour un client
    random.seed(int(client_id))
    
    # 90% de chances d'être bon payeur
    if random.random() < 0.90:
        # Bon payeur : score entre 0.70 et 0.95
        score = random.uniform(0.70, 0.95)
    else:
        # Mauvais payeur : score entre 0.10 et 0.69
        score = random.uniform(0.10, 0.69)
    
    return round(score, 2)

# Seuil de décision (dummy, sera 0.10 en production)
THRESHOLD = 0.5

def log_prediction(client_id: str, score: float, decision: str, response_time: float):
    """
    Enregistre une prédiction dans le fichier de logs CSV
    
    Args:
        client_id: ID du client
        score: Score de prédiction
        decision: Décision prise
        response_time: Temps de réponse en millisecondes
    """
    with open(LOGS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),  # timestamp ISO format
            client_id,
            score,
            decision,
            round(response_time, 2)
        ])

@app.get("/predict/{client_id}", response_model=PredictionOut)
async def predict(client_id: str):
    """
    Prédiction de scoring pour un client donné
    
    Args:
        client_id: Identifiant du client (ex: "100001")
        
    Returns:
        PredictionOut: Score de prédiction et décision
        
    Raises:
        HTTPException 404: Si le client n'existe pas dans la base
    """
    # Démarrer le chronomètre
    start_time = time()
    
    # Vérification existence du client
    if client_id not in clients_db:
        raise HTTPException(
            status_code=404,
            detail=f"Client {client_id} introuvable dans la base de données"
        )
    
    # Récupération des features du client
    client_features = clients_db[client_id]
    
    # Prédiction avec le modèle dummy
    score = dummy_model_predict(client_id, client_features)
    
    # Décision selon le seuil
    if score >= THRESHOLD:
        decision = "Crédit refusé"
    else:
        decision = "Crédit accepté"
    
    # Calculer le temps de réponse en millisecondes
    response_time_ms = (time() - start_time) * 1000
    
    # Logger la prédiction
    log_prediction(client_id, score, decision, response_time_ms)
              
    return PredictionOut(
        client_id=int(client_id),
        score=score,
        decision=decision,
        threshold=THRESHOLD,  # ← AJOUT (0.5 pour dummy)
        timestamp=datetime.now().isoformat()  # ← AJOUT
    )

@app.get("/")
async def root():
    """
    Route racine - Vérification que l'API fonctionne
    """
    return {
        "message": "API Scoring Crédit - Version Dummy",
        "status": "operational",
        "clients_disponibles": len(clients_db)
    }

@app.get("/health")
async def health():
    """
    Endpoint de santé pour monitoring
    Vérifie que l'API est opérationnelle
    
    Returns:
        dict: Statut de l'API et des composants chargés
    """
    return {
        "status": "healthy",
        "model_loaded": "model" in ml_models,
        "data_loaded": "X_test_sample" in ml_models,
        "version": "1.0.0"
    }

@app.get("/v2/predict/{client_id}", response_model=PredictionOut)
async def predict_v2(client_id: int):
    """
    Prédiction de risque de crédit avec le modèle de production
    
    **Modèle champion : XGBoost** optimisé sur données Projet 6
    
    Args:
        client_id: Identifiant unique du client (SK_ID_CURR)
        
    Returns:
        PredictionOut: Score de risque, décision, seuil et timestamp
        
    Raises:
        HTTPException 404: Si le client n'existe pas dans les données
        
    Notes:
        - Seuil métier optimisé : 0.10 (vs 0.50 sklearn par défaut)
        - Score >= 0.10 → Crédit refusé (risque élevé)
        - Score < 0.10 → Crédit accepté (risque faible)
    """
    start_time = time()
    
    # Récupérer les assets depuis ml_models
    model = ml_models["model"]
    X_test_sample = ml_models["X_test_sample"]
    
    # Vérifier si le client existe
    if client_id not in X_test_sample.index:
        raise HTTPException(
            status_code=404,
            detail=f"Client {client_id} introuvable dans les données"
        )
    
    # Récupérer les features du client
    features = X_test_sample.loc[[client_id]]
    
    # Prédiction avec le modèle
    score = model.predict_proba(features)[0, 1]  # Probabilité classe 1
    score = round(score, 4)  # Arrondir à 4 décimales
    
    THRESHOLD_V2 = 0.10
    decision = "Crédit refusé" if score >= THRESHOLD_V2 else "Crédit accepté"
    
    response_time_ms = (time() - start_time) * 1000
    log_prediction(str(client_id), score, decision, response_time_ms)  # ← Garder str() ici pour le CSV
    
    return PredictionOut(
        client_id=client_id,
        score=score,
        decision=decision,
        threshold=THRESHOLD_V2,  # ← AJOUT
        timestamp=datetime.now().isoformat()  # ← AJOUT
    )