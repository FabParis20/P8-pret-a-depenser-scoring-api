# P8 - Confirmez vos compétences MLOps
## Déploiement et monitoring d'un modèle de scoring

**Étudiant** : Fabrice Vanspeybrock  
**Formation** : MLOps  
**Date de début** : 08/10/2025  
**Dépôt GitHub** : https://github.com/FabParis20/P8-pret-a-depenser-scoring-api

---

## 📋 Vue d'ensemble du projet

Ce projet consiste à déployer en production un modèle de scoring de crédit via une API, avec monitoring et CI/CD automatisé.

**Objectifs principaux :**
- Créer une API FastAPI fonctionnelle
- Conteneuriser avec Docker
- Mettre en place un pipeline CI/CD
- Monitorer le modèle en production (Data Drift)
- Optimiser les performances

---

## 📐 Architecture

La documentation complète de l'architecture du projet est disponible dans [`docs/architecture/`](docs/architecture/) avec 5 diagrammes :

1. **Vue d'ensemble** - Contexte
2. **Architecture technique** - Architecture statique
3. **Flux de prédiction** - Flux de prédiction
4. **Pipeline CI/CD** - Pipeline CI/CD
5. **Monitoring** - Monitoring Data Drift

---

## 🧪 Historique de développement

### Phase 1 : API Dummy (Validation architecture - approche incrémentale)

**Objectif** : Valider la structure de l'API avant intégration du modèle réel

**Fonctionnalités implémentées** :
- ✅ Endpoint `/predict/{client_id}` fonctionnel
- ✅ Modèle dummy avec distribution 90/10 (bon/mauvais payeur)
- ✅ Gestion erreurs 404
- ✅ Validation automatique FastAPI + Pydantic
- ✅ Route de santé : / pour vérifier l'état de l'API
- ✅ Reproductibilité des prédictions (même client_id = même score)

**Tests automatisés**
**Couverture: 94%**
**4 tests validés :**
- ✅ Démarrage de l'API
- ✅ Prédiction avec client valide
- ✅ Gestion erreur 404 (client inexistant)
- ✅ Reproductibilité des prédictions

**Données de test**
- Base clients dummy : 10 clients fictifs avec 4 features
- Client IDs : 100001 à 100010
- Seuil de décision : 0.5 (sera ajusté à 0.10 en production conformément au seuil optimisé lors du Projet 6)

**Screenshots disponibles** : [`docs/screenshots/phase_dummy/`](docs/screenshots/phase_dummy/)

**Migration vers modèle production** : [Date de migration]

### Phase 2 : Conteneurisation Docker

**Objectif** : Empaqueter l'API dans un conteneur Docker pour garantir la portabilité

**Image Docker** :
- ✅ Base : `python:3.12-slim` (image légère)
- ✅ Gestion des dépendances : Poetry 2.0
- ✅ Installation : Dépendances de production uniquement (`--only main`)
- ✅ Exposition : Port 8000
- ✅ Configuration : `--host 0.0.0.0` pour accessibilité externe

**Structure du conteneur** :
```
/app/
├── api/              # Code de l'API
├── models/           # Modèles ML
├── data/             # Données de production
└── pyproject.toml    # Dépendances
```

**Commandes Docker** :
```bash
# Construire l'image
docker build -t api-scoring .

# Lancer le conteneur
docker run -p 8000:8000 api-scoring

# Accéder à l'API
# - Route racine : http://localhost:8000
# - Documentation : http://localhost:8000/docs
```

**Bonnes pratiques appliquées** :
- ✅ Installation Poetry sans environnement virtuel (inutile dans un conteneur)
- ✅ Copie uniquement des fichiers nécessaires (pas de `tests/`, `notebooks/`)
- ✅ Installation des dépendances de production uniquement
- ✅ Configuration réseau adaptée à Docker (`0.0.0.0`)

---

## 🚀 Démarrage rapide

### Prérequis
- Python 3.11+
- Poetry 2.0+
- Docker Desktop (pour la conteneurisation)

### Installation locale (sans Docker)
```bash
# Cloner le dépôt
git clone https://github.com/FabParis20/P8-pret-a-depenser-scoring-api.git
cd P8-pret-a-depenser-scoring-api

# Installer les dépendances
poetry install

# Lancer l'API
poetry run uvicorn api.main:app --reload

# Accéder à l'API : http://localhost:8000/docs
```

### Installation avec Docker (recommandé)
```bash
# Construire l'image
docker build -t api-scoring .

# Lancer le conteneur
docker run -p 8000:8000 api-scoring

# Accéder à l'API : http://localhost:8000/docs
```

### Tests
```bash
# Lancer les tests
poetry run pytest tests/test_api.py -v

# Avec couverture de code
poetry run pytest tests/test_api.py -v --cov=api --cov-report=term-missing
```

---