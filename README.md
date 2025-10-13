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

**Ce qui a été testé** :
- ✅ Endpoint `/predict/{client_id}` fonctionnel
- ✅ Modèle dummy avec distribution 90/10 (bon/mauvais payeur)
- ✅ Gestion erreurs 404
- ✅ Validation automatique FastAPI
- ✅ Reproductibilité des prédictions (même client_id = même score)

**Screenshots disponibles** : [`docs/screenshots/phase_dummy/`](docs/screenshots/phase_dummy/)

**Migration vers modèle production** : [Date de migration]
