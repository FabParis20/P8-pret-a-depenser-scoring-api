# tests/test_api.py
"""
Tests automatisés pour l'API de scoring
Projet MLOps - Prêt à dépenser
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app, ml_models
import pandas as pd
import pickle
from pathlib import Path

@pytest.fixture(scope="module", autouse=True)
def load_production_assets():
    """
    Fixture qui charge le modèle et les données AVANT tous les tests
    Exécutée automatiquement (autouse=True) une seule fois (scope="module")
    """
    # Chemins vers les assets
    project_root = Path(__file__).parent.parent
    model_path = project_root / "models" / "model.pkl"
    data_path = project_root / "data" / "prod" / "X_test_sample.pkl"
    
    # Charger le modèle
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    # Charger les données
    X_test_sample = pd.read_pickle(data_path)
    
    # Remplir ml_models (comme le fait lifespan)
    ml_models["model"] = model
    ml_models["X_test_sample"] = X_test_sample
    
    print(f"\n✅ Assets chargés pour les tests : model + {X_test_sample.shape[0]} clients")
    
    # yield permet d'exécuter du code après tous les tests (cleanup)
    yield
    
    # Nettoyage après les tests
    ml_models.clear()

# Création du client de test (simule les requêtes HTTP)
client = TestClient(app)

# Vérification que l'API démarre correctement
def test_api_startup():
    """
    Test 1 : Vérifie que l'API démarre et répond sur la route racine
    """
    response = client.get("/")
    
    # Vérifier le code de statut
    assert response.status_code == 200
    
    # Vérifier le contenu de la réponse
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["status"] == "operational"
    assert data["clients_disponibles"] > 0  # ✅ Plus flexible

# Test 2 - Prédiction avec données valides
def test_predict_valid_client():
    """
    Test 2 : Vérifie qu'une prédiction fonctionne avec un client valide (dummy)
    """
    client_id = "100001"  # Client dummy valide
    response = client.get(f"/predict/{client_id}")
    
    # Vérifier le code de statut
    assert response.status_code == 200
    
    # Vérifier la structure de la réponse
    data = response.json()
    assert "client_id" in data
    assert "score" in data
    assert "decision" in data
    assert "threshold" in data  # ← AJOUT (JSON enrichi)
    assert "timestamp" in data  # ← AJOUT
    
    # Vérifier les types et valeurs
    assert data["client_id"] == int(client_id)  # ← CORRECTION : conversion en int
    assert isinstance(data["score"], float)
    assert 0 <= data["score"] <= 1
    assert data["decision"] in ["Crédit accepté", "Crédit refusé"]
    assert data["threshold"] == 0.5  # Seuil dummy

# Test 3 - Gestion des erreurs
def test_predict_invalid_client():
    """
    Test 3 : Vérifie que l'API retourne une erreur 404 pour un client inexistant
    """
    client_id = "999999"  # Client qui n'existe pas
    response = client.get(f"/predict/{client_id}")
    
    # Vérifier le code d'erreur
    assert response.status_code == 404
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data
    assert "introuvable" in data["detail"].lower()

# Test reproductibilité
def test_predict_reproducibility():
    """
    Test 4 : Vérifie que le même client retourne toujours le même score (dummy)
    """
    client_id = "100001"
    
    # Faire 2 prédictions
    response1 = client.get(f"/predict/{client_id}")
    response2 = client.get(f"/predict/{client_id}")
    
    # Vérifier que les scores sont identiques
    score1 = response1.json()["score"]
    score2 = response2.json()["score"]
    assert score1 == score2

# ============================================================
# TESTS ENDPOINT V2 (PRODUCTION)
# ============================================================

def test_v2_predict_valid_client():
    """
    Test v2.1 : Vérifie qu'une prédiction fonctionne avec le modèle production
    """
    # Client accepté attendu (score < 0.10)
    client_id = 273460
    response = client.get(f"/v2/predict/{client_id}")
    
    # Vérifier le code de statut
    assert response.status_code == 200
    
    # Vérifier la structure
    data = response.json()
    assert "client_id" in data
    assert "score" in data
    assert "decision" in data
    assert "threshold" in data
    assert "timestamp" in data
    
    # Vérifier les valeurs
    assert data["client_id"] == client_id
    assert isinstance(data["score"], float)
    assert 0 <= data["score"] <= 1
    assert data["threshold"] == 0.10  # Seuil production
    assert data["decision"] in ["Crédit accepté", "Crédit refusé"]


def test_v2_predict_threshold_logic():
    """
    Test v2.2 : Vérifie que le threshold 0.10 est correctement appliqué
    """
    # Client refusé attendu (score >= 0.10)
    client_id_refuse = 321537
    response = client.get(f"/v2/predict/{client_id_refuse}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Si score >= 0.10, la décision doit être "Crédit refusé"
    if data["score"] >= 0.10:
        assert data["decision"] == "Crédit refusé"
    else:
        assert data["decision"] == "Crédit accepté"


def test_v2_predict_invalid_client():
    """
    Test v2.3 : Vérifie la gestion d'erreur pour client inexistant
    """
    client_id = 999999  # N'existe pas dans X_test_sample
    response = client.get(f"/v2/predict/{client_id}")
    
    # Vérifier le code d'erreur 404
    assert response.status_code == 404
    
    # Vérifier le message d'erreur
    data = response.json()
    assert "detail" in data
    assert "introuvable" in data["detail"].lower()


def test_health_endpoint():
    """
    Test v2.4 : Vérifie que l'endpoint /health fonctionne
    """
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    assert "data_loaded" in data
    assert data["model_loaded"] is True
    assert data["data_loaded"] is True