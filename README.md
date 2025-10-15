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

### Phase 3 : Pipeline CI/CD (GitHub Actions)

**Objectif** : Automatiser les tests et la construction Docker à chaque modification du code

**Pipeline configuré** :
- ✅ Déclenchement automatique sur push vers `main`
- ✅ Job 1 : Tests automatisés
- ✅ Job 2 : Build Docker (si tests OK)
- ✅ Notifications en cas d'échec
- ✅ Badge de statut dans le README

**Workflow CI/CD** :
```yaml
Push sur main → Job Tests → Job Build Docker → ✅ Success
                     ↓
                    ❌ Échec → STOP + Notification
```

**Job 1 : Tests automatisés**
- Installation Python 3.12 + Poetry
- Installation des dépendances (mode dev)
- Exécution de pytest avec couverture
- Durée : ~2 minutes

**Job 2 : Build Docker**
- Construction de l'image Docker
- Vérification que l'image existe
- Durée : ~3 minutes
- **Condition** : S'exécute uniquement si les tests passent (`needs: test`)

**Points de contrôle** :
- ✅ Tests unitaires : 4 tests validés (94% coverage)
- ✅ Build Docker : Image construite sans erreur
- ✅ Logs détaillés : Consultables dans l'onglet Actions de GitHub

**Dépôt GitHub (badge)** : [![CI Pipeline](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/actions/workflows/ci.yml/badge.svg)](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/actions/workflows/ci.yml)

**Bonnes pratiques appliquées** :
- ✅ Séparation des responsabilités (2 jobs distincts)
- ✅ Dépendance entre jobs (`needs: test`)
- ✅ Utilisation d'actions officielles (`actions/checkout@v4`, `actions/setup-python@v5`)
- ✅ Installation Poetry via script officiel
- ✅ Réutilisation du Dockerfile existant (DRY principle)

**Accès au pipeline** : [Actions](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/actions)

