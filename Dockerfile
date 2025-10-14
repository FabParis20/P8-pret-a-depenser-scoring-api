# Dockerfile
# Image de base : Python 3.12 sur Linux (léger)
FROM python:3.12-slim 
# FROM = "Je pars de cette image" - Version allégée de Python

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer Poetry
RUN pip install --no-cache-dir poetry==2.0.0

# Configurer Poetry pour ne pas créer d'environnement virtuel
# (inutile dans un conteneur : le conteneur EST déjà isolé !)
RUN poetry config virtualenvs.create false

# Copier les fichiers de dépendances
COPY pyproject.toml poetry.lock ./

# Installer les dépendances de production uniquement
RUN poetry install --only main --no-interaction --no-ansi


# 📖 Explication des options

# `poetry install` : Lit le `pyproject.toml` et installe toutes les dépendances
# `--no-dev` : **N'installe PAS** les dépendances de développement (pytest, black, ruff...)
# **Pourquoi ?** En production, on n'a pas besoin des outils de test !
# Ça réduit la taille de l'image Docker
# --no-interaction` : Mode automatique, ne pose pas de questions
# --no-ansi` : Pas de couleurs dans les logs (plus lisible dans GitHub Actions)


# Copier le code de l'application
COPY api/ ./api/
COPY models/ ./models/
COPY data/ ./data/

# Exposer le port 8000
EXPOSE 8000
# (Documente que l'application utilise le port 8000)
# ⚠️ Important : Cette ligne ne fait rien toute seule ! Elle sert de documentation

# Commande pour lancer l'API au démarrage du conteneur
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Explications --host 0.0.0.0
# 8000 Crée le pont entre le PC et le conteneur
# Dit à l'API d'accepter les connexions qui passent ce pont