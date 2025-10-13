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

# Création de l'application FastAPI
app = FastAPI(
    title="API Scoring Crédit",
    description="API de prédiction de scoring pour les demandes de crédit",
    version="0.1.0-dummy"
)

# Chargement de la base clients fictive au démarrage (une seule fois !)
CLIENTS_FILE = Path(__file__).parent / "clients_dummy.json"

with open(CLIENTS_FILE, "r") as f:
    clients_db = json.load(f)

print(f"✅ Base clients chargée : {len(clients_db)} clients disponibles")

# Modèle de sortie de la prédiction
class PredictionOut(BaseModel):
    client_id: str
    score: float  # Probabilité entre 0 et 1
    decision: str  # "Crédit accepté" ou "Crédit refusé"

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
    
    return PredictionOut(
        client_id=client_id,
        score=score,
        decision=decision
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