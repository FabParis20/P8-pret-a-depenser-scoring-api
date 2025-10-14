# tests/test_api.py
"""
Tests automatisés pour l'API de scoring
Projet MLOps - Prêt à dépenser
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

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
    Test 2 : Vérifie qu'une prédiction fonctionne avec un client valide
    """
    # TODO MIGRATION : Remplacer par un client_id de X_sub.pkl (ex: "160736")
    client_id = "100001" # Client dummy valide
    response = client.get(f"/predict/{client_id}")
    
    # Vérifier le code de statut
    assert response.status_code == 200
    
    # Vérifier la structure de la réponse
    data = response.json()
    assert "client_id" in data
    assert "score" in data
    assert "decision" in data
    
    # Vérifier les types et valeurs
    assert data["client_id"] == client_id
    assert isinstance(data["score"], float)
    assert 0 <= data["score"] <= 1  # Score entre 0 et 1
    assert data["decision"] in ["Crédit accepté", "Crédit refusé"]

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
    Test bonus : Vérifie que le même client retourne toujours le même score
    """
    # TODO MIGRATION : Remplacer par un ID de X_sub.pkl (ex: "160736")
    client_id = "100001"
    
    # Faire 2 prédictions
    response1 = client.get(f"/predict/{client_id}")
    response2 = client.get(f"/predict/{client_id}")
    
    # Vérifier que les scores sont identiques
    score1 = response1.json()["score"]
    score2 = response2.json()["score"]
    assert score1 == score2