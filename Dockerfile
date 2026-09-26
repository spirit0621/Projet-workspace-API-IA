# Image de base Python 3.11 légère
FROM python:3.11-slim

# Évite l'écriture de fichiers .pyc et assure un affichage direct des logs dans la console Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation de ffmpeg pour l'audio et curl pour le healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python avec timeout de sécurité
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copie du code source modulaire
COPY src/ ./src/

# Configuration du PYTHONPATH pour les imports du package src
ENV PYTHONPATH=/app/src:/app

# Exposition du port HTTP
EXPOSE 8000

# Commande de démarrage du serveur FastAPI
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
