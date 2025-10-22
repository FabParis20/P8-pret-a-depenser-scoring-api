# P8 - Confirmez vos compétences MLOps
## Déploiement et monitoring d'un modèle de scoring

**Étudiant** : Fabrice Vanspeybrock  
**Formation** : MLOps  
**Date de début** : 08/10/2025  
**Dépôt GitHub** : https://github.com/FabParis20/P8-pret-a-depenser-scoring-api

**Dépôt GitHub (badge)** : [![CI Pipeline](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/actions/workflows/ci.yml/badge.svg)](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/actions/workflows/ci.yml)

---

## 📋 Table des matières

- [⚡ Quick Start](#⚡-quick-start)
  - [🔧 Installation](#🔧-installation)
  - [🚀 Utilisation (API Locale)](#🚀-utilisation-api-locale)
  - [🐳 Déploiement (Docker)](#🐳-déploiement-docker)
  - [📊 Monitoring](#📊-monitoring)
  - [⚡ Optimisations](#⚡-optimisations)
  - [🧪 Tests](#🧪-tests)
- [📋 Vue d'ensemble du projet](#📋-vue-densemble-du-projet)
- [📐 Architecture](#📐-architecture)
- [🧪 Historique de développement](#🧪-historique-de-développement)
  - [Phase 1 : API Dummy (Validation architecture - approche incrémentale)](#phase-1--api-dummy-validation-architecture---approche-incrémentale)
  - [Phase 2 : Conteneurisation Docker](#phase-2--conteneurisation-docker)
  - [Phase 3 : Pipeline CI/CD (GitHub Actions)](#phase-3--pipeline-cicd-github-actions)
  - [Phase 4 : Préparation des données de production](#phase-4--préparation-des-données-de-production)
  - [Phase 5 : Migration vers modèle production](#phase-5--migration-vers-modèle-production)
  - [Phase 6 : Optimisations performance](#phase-6--optimisations-performance)
  - [Phase 7 : Déploiement Docker Hub](#phase-7--déploiement-docker-hub)
  - [Phase 8 : Monitoring en production](#phase-8--monitoring-en-production)



## ⚡ Quick Start

Cette section détaille comment installer, utiliser, déployer et monitorer l'API de scoring de crédit.

### 🔧 Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone [https://github.com/FabParis20/P8-pret-a-depenser-scoring-api.git](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api.git)
    cd P8-pret-a-depenser-scoring-api
    ```
2.  **Installer les dépendances** (avec [Poetry](https://python-poetry.org/)) :
    ```bash
    poetry install
    ```

### 🚀 Utilisation (API Locale)

1.  **Lancer le serveur API** (avec Uvicorn) :
    L'API sera disponible sur `http://localhost:8000`.
    ```bash
    poetry run uvicorn api.main:app --reload
    ```
2.  **Consulter la documentation (Swagger) :**
    Ouvrir dans le navigateur : [http://localhost:8000/docs](http://localhost:8000/docs)

3.  **Exemple requête `curl` (Production v2) :**
    Test avec un client de production (ID `273460`).
    ```bash
    curl -X 'GET' 'http://localhost:8000/v2/predict/273460' -H 'accept: application/json'
    ```

4.  **Exemple requête `curl` (Dummy v1) :**
    Test avec un client dummy (ID `100001`).
    ```bash
    curl -X 'GET' 'http://localhost:8000/predict/100001' -H 'accept: application/json'
    ```

### 🐳 Déploiement (Docker)

L'API est également disponible en tant qu'image Docker publique sur Docker Hub.

1.  **Tirer (pull) l'image :**
    ```bash
    docker pull fabparis20/api-scoring-credit:latest
    ```
2.  **Lancer (run) le conteneur :**
    L'API sera accessible sur `http://localhost:8000`.
    ```bash
    docker run -p 8000:8000 fabparis20/api-scoring-credit:latest
    ```

### 📊 Monitoring

Le dashboard Streamlit permet de visualiser les logs et le data drift.
**Prérequis :** L'API (Docker ou locale) doit être en cours d'exécution.

1.  **Lancer le dashboard :**
    ```bash
    streamlit run app_monitoring.py
    ```
2.  **Accès aux rapports :**
    * Le dashboard s'ouvre dans votre navigateur.
    * Le dernier rapport de drift statique est disponible : [docs/drift_report_production.html](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/drift_report_production.html)

### ⚡ Optimisations

Optimisation via pré-chargement du modèle (FastAPI lifespan) pour éviter le rechargement à chaque requête.
* **Temps moyen (v1 - naive)** : 366.37 ms
* **Temps moyen (v2 - optimisé)** : 169.50 ms
* **Gain de performance** : **53.7%** (facteur 2.2x)
* **Rapport de benchmark** : [`docs/benchmark_results.txt`](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/benchmark_results.txt)
* **Rapport de profiling** : [`docs/profiling_results.txt`](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/profiling_results.txt)

### 🧪 Tests

Les tests unitaires et d'intégration sont gérés via `pytest` et `pytest-cov` pour la couverture.

1.  **Lancer la suite de tests** (depuis la racine du projet) :
    ```bash
    poetry run pytest
    ```
2.  **Générer le rapport de couverture :**
    ```bash
    poetry run pytest --cov=api
    ```
3.  **Tests implémentés** (dans `tests/test_api.py`) :
    * `test_api_startup` : Vérifie la route racine (`/`).
    * `test_predict_valid_client` : Vérifie l'endpoint dummy (v1) avec un client valide.
    * `test_predict_invalid_client` : Vérifie l'erreur 404 (v1).
    * `test_predict_reproducibility` : Vérifie la reproductibilité du score (v1).
    * `test_v2_predict_valid_client` : Vérifie l'endpoint production (v2) avec un client valide.
    * `test_v2_predict_threshold_logic` : Vérifie l'application du seuil métier (0.10).
    * `test_v2_predict_invalid_client` : Vérifie l'erreur 404 (v2).
    * `test_health_endpoint` : Vérifie l'endpoint de santé (`/health`).

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

---

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

---

### Phase 4 : Préparation des données de production

**Objectif** : Extraire des échantillons stratifiés depuis le Projet 6 pour la migration vers le modèle réel

**Données préparées** :
- ✅ **X_test_sample.pkl** : 2000 clients (10 MB) pour prédictions API
- ✅ **X_train_sample.pkl** : 2000 clients (10 MB) pour référence drift
- ✅ **813 features** par client (alignées avec le modèle champion)
- ✅ **Distribution stratifiée** : 93% acceptés / 7% refusés
- ✅ **Indices conservés** : Reproductibilité garantie via `test_indices.npy`

**Méthode d'extraction** :
- Source : `train_ready.parquet` (356k clients du Projet 6)
- Split : Réutilisation des indices de test originaux (20% du dataset)
- Échantillonnage : `StratifiedShuffleSplit` avec `random_state=54`
- Validation : Taille < 50 MB pour compatibilité GitHub

**Structure des données** :
```
data/
├── prod/
│   ├── X_test_sample.pkl      # Données pour prédictions
│   └── y_test_sample.pkl      # Labels de validation
└── train/
    ├── X_train_sample.pkl     # Référence pour drift
    └── y_train_sample.pkl     # Labels de référence
```

**Traçabilité** :
- Notebook d'extraction : `prep_data_sample.ipynb` (Projet 6)
- Hash des colonnes : Vérifié identique au Projet 6
- Reproductibilité : Mêmes lignes que lors de l'entraînement du modèle champion

---

### Phase 5 : Migration vers modèle production

**Objectif** : Remplacer le modèle dummy par le modèle XGBoost champion entraîné en Projet 6

**Modèle intégré** :
- ✅ **Fichier** : `models/model.pkl` (2.5 MB)
- ✅ **Type** : Pipeline sklearn (ColumnTransformer + XGBoost)
- ✅ **Preprocessing** : Automatique dans le pipeline
- ✅ **Features** : 813 colonnes (alignées avec X_test_sample)
- ✅ **Seuil métier** : 0.10 (optimisé Projet 6, pas 0.50 sklearn)

**Nouvel endpoint production** :
- ✅ Route : `/v2/predict/{client_id}`
- ✅ Méthode : GET
- ✅ Chargement modèle : Au démarrage API (lifespan FastAPI)
- ✅ Logique de décision :
  - Score >= 0.10 → **Crédit refusé**
  - Score < 0.10 → **Crédit accepté**

**Tests de validation** :
- ✅ 8 tests automatisés (pytest)
- ✅ Couverture : Tests modèle réel + endpoint v2
- ✅ Clients de test : 10 clients réels (5 acceptés, 5 refusés)

**Clients de démonstration** :
| Type | Client ID | Score | Décision |
|------|-----------|-------|----------|
| ✅ Accepté | 273460 | 0.0395 | Crédit accepté |
| ✅ Accepté | 268316 | 0.0257 | Crédit accepté |
| 🚫 Refusé | 321537 | 0.1375 | Crédit refusé |
| 🚫 Refusé | 402448 | 0.1793 | Crédit refusé |

**Documentation complète** : [demo_clients.md](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/demo_clients.md)

**Migration réussie** : Tag Git `v1.0.0`

---

### Phase 6 : Optimisations performance

**Objectif** : Identifier et corriger les goulots d'étranglement pour améliorer le temps de réponse API

**Méthodologie appliquée** :
1. Benchmark baseline (version naive)
2. Profiling cProfile (identification goulots)
3. Optimisation ciblée
4. Mesure de l'impact

**Optimisation principale : Préchargement modèle**
- **Problème identifié** : Rechargement modèle (2.5 MB) à chaque requête
- **Solution implémentée** : Lifespan FastAPI (chargement unique au démarrage)
- **Impact mesuré** :
  - Temps moyen : **366ms → 169ms**
  - Gain performance : **53.7%** (facteur 2.2x)
  - Stabilité : Écart-type réduit de 90% (192ms → 19ms)

**Profiling cProfile** :
- ✅ Goulot principal identifié : `joblib.load()` = 72% du temps total
- ✅ Confirmation scientifique de l'optimisation prioritaire
- ✅ Résultats détaillés : [profiling_results.txt](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/profiling_results.txt)

**Benchmark complet** :
- ✅ 50 itérations par version (naive vs optimisée)
- ✅ Métriques P95, P99, écart-type mesurées
- ✅ Résultats détaillés : [benchmark_results.txt](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/benchmark_results.txt)

**Stratégies non retenues (justifiées)** :
- ❌ **ONNX Runtime** : Gain estimé 10-20% insuffisant (temps actuel < 300ms acceptable UX)
- ❌ **Quantification** : Scoring crédit = décisions sensibles, perte précision inacceptable
- ❌ **GPU** : Modèle trop petit (2.5 MB), overhead transfert > gain calcul

**Documentation complète** : [OPTIMISATIONS.md](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/OPTIMISATIONS.md)

**Tags Git** : `v1.2.1` (optimisations validées)

---

### Phase 7 : Déploiement Docker Hub

**Objectif** : Automatiser la publication de l'image Docker sur Docker Hub via le pipeline CI/CD

**Configuration implémentée** :
- ✅ Repository Docker Hub : `fabparis20/api-scoring-credit`
- ✅ Secrets GitHub configurés : `DOCKER_USERNAME` + `DOCKER_PASSWORD`
- ✅ Push automatique sur branche `main` uniquement
- ✅ Tag image : `latest`

**Pipeline CI/CD étendu** :
```
Push sur main → Tests → Build Docker → Push Docker Hub → ✅ Image publique
                  ↓
                 ❌ Échec → STOP
```

**Workflow mis à jour** :
1. Job Tests : Pytest avec couverture
2. Job Build : Construction image Docker
3. Job Push : Publication Docker Hub (condition : `if: github.ref == 'refs/heads/main'`)

**Image disponible publiquement** :
```bash
docker pull fabparis20/api-scoring-credit:latest
```

**Avantages déploiement** :
- ✅ Déploiement automatisé (zéro intervention manuelle)
- ✅ Image toujours à jour avec la branche main
- ✅ Reproductibilité garantie
- ✅ Prêt pour déploiement cloud (AWS ECS, GCP Cloud Run, Azure Container Instances)

**Accès Docker Hub** : [fabparis20/api-scoring-credit](https://hub.docker.com/r/fabparis20/api-scoring-credit)

**Tags Git** : `v1.3.0` (déploiement automatisé validé)

---

### Phase 8 : Monitoring en production

**Objectif** : Surveiller le modèle en production (data drift, logs, performance)

**Analyse Data Drift (Evidently AI)** :
- ✅ Méthodologie : Comparaison 50 features critiques (top importance XGBoost)
- ✅ Référence : X_train_sample (2000 clients)
- ✅ Production : X_test_sample (2000 clients)
- ✅ Résultat : Pas de drift significatif (normal : train/test même source)
- ✅ Surveillance production : Analyse mensuelle planifiée

**Livrables drift** :
- Notebook d'analyse : [analyse_drift.ipynb](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/notebooks/analyse_drift.ipynb)
- Rapport HTML interactif : [drift_report_production.html](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/drift_report_production.html)

**Logs de production** :
- ✅ Fichier : `data/prod/logs_production.csv`
- ✅ Structure : timestamp, client_id, score, decision, response_time_ms
- ✅ Stratégie : CSV pour POC, migration PostgreSQL si > 100k prédictions/mois
- ✅ Screenshot : [stockage_logs_csv.png](https://github.com/FabParis20/P8-pret-a-depenser-scoring-api/blob/main/docs/screenshots/stockage_logs_csv.png)

**Dashboard Streamlit** :
- ✅ Démo interactive (test API en temps réel)
- ✅ Vue d'ensemble (KPIs, métriques)
- ✅ Distribution des scores
- ✅ Analyse Data Drift (rapport Evidently intégré)
- ✅ Performance API (latence, temps de réponse)

**Lancement dashboard** :
```bash
streamlit run app_monitoring.py
```

**Tags Git** : `v1.2.0` (monitoring complet validé)