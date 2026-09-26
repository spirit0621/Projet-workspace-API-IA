# 🤖 Google Workspace & Gemini Hub : API REST & Assistant CLI

Une solution centralisée, modulaire et prête pour la production pour automatiser et piloter l'ensemble de votre écosystème **Google Workspace** (Drive, Docs, Sheets, Slides, Calendar, Tasks, Forms) et l'**Intelligence Artificielle Gemini** depuis n'importe lequel de vos projets (React, Next.js, Node.js, Python, Mobile, etc.) ou en ligne de commande.

---

## 🌟 2 Modes d'Utilisation

1. **Serveur Microservice / API REST (FastAPI + Docker)** 🚀  
   Accessible depuis tous vos autres projets via de simples requêtes HTTP (`http://localhost:8000/api/...`). Documentation interactive Swagger disponible sur `http://localhost:8000/docs`.
2. **Assistant CLI (Ligne de commande)** 💻  
   Exécutable directement dans votre terminal pour automatiser vos tâches quotidiennes en quelques secondes.

---

## 📋 Table des Matières

1. [Prérequis](#-prérequis)
2. [Structure du Projet](#-structure-du-projet)
3. [Installation & Configuration](#-installation--configuration)
   - [Variables d'environnement (.env)](#1-variables-denvironnement-env)
   - [Identifiants Google OAuth2 (credentials.json)](#2-identifiants-google-oauth2-credentialsjson)
   - [Génération du jeton (token.json)](#3-première-authentification--génération-du-tokenjson)
4. [Démarrage Rapide](#-démarrage-rapide)
   - [Option A : Via Docker (Recommandé)](#option-a--démarrage-via-docker-recommandé)
   - [Option B : En local avec l'API FastAPI](#option-b--démarrage-de-lapi-en-local)
   - [Option C : En ligne de commande (CLI)](#option-c--utilisation-en-ligne-de-commande-cli)
5. [Documentation Interactive de l'API (Swagger)](#-documentation-interactive-de-lapi-swagger)
6. [Référence des Commandes CLI](#-référence-des-commandes-cli)
   - [Drive](#-drive)
   - [Docs](#-docs)
   - [Sheets](#-sheets)
   - [Slides](#-slides)
   - [Calendar](#-calendar)
   - [Tasks](#-tasks)
   - [Forms](#-forms)
   - [Notebook](#-notebook)
   - [AI Gemini](#-ai-gemini)
7. [Standard vs IA (Coûts & Tokens)](#-standard-vs-ia-coûts--tokens)
8. [Guides et Documentation Complémentaire](#-guides-et-documentation-complémentaire)
9. [Dépannage & Astuces Docker](#-dépannage--astuces-docker)

---

## 🔧 Prérequis

- **Python 3.10+** (ou **Docker Desktop**)
- Un compte **Google** avec accès à Google Workspace
- Un projet **Google Cloud** avec les APIs Workspace activées
- Une clé **Gemini API** (gratuite sur [Google AI Studio](https://aistudio.google.com/))

---

## 📁 Structure du Projet

L'architecture est entièrement modulaire, propre et organisée par responsabilité :

```text
Projet-workspace-API-IA/
├── config/                   # Identifiants Google & configurations
│   ├── credentials.json      # Identifiants OAuth2 client (privé, ignoré par Git)
│   ├── token.json            # Jeton d'accès session Google (généré automatiquement)
│   └── .env.example          # Gabarit de configuration d'environnement
├── data/                     # Données persistantes locales
│   └── usage_history.json    # Historique de consommation des tokens Gemini
├── docs/                     # Guides d'intégration et documentation
│   ├── GUIDE_INTEGRATION_MULTI_PROJETS.md # Guide d'appel depuis d'autres projets
│   ├── Guide_Utilisation.md               # Guide complet des fonctionnalités
│   ├── Sommaire fonction.md               # Référence des fonctions
│   ├── Sommaire_Google_Cloud.md           # Configuration GCP
│   └── Relation_VM_GCP.md                 # Déploiement Cloud
├── scripts/                  # Scripts utilitaires et lanceurs Windows
│   ├── start_api.bat         # Lanceur rapide de l'API FastAPI en local
│   ├── gassist.bat           # Raccourci CLI pour les commandes en terminal
│   └── create_tp2_docx.py    # Générateur de rapports Word
├── src/                      # Code source modulaire
│   ├── __init__.py
│   ├── auth.py               # Authentification OAuth2 & scopes Workspace
│   ├── server.py             # Serveur API REST (FastAPI, CORS, Swagger)
│   ├── google_assistant.py   # Application CLI principale
│   └── services/             # 11 modules de services spécialisés
│       ├── assistant_ai.py       # Fonctions IA Gemini 3.7/3.5 Flash
│       ├── assistant_calendar.py # Google Calendar
│       ├── assistant_docs.py     # Google Docs
│       ├── assistant_drive.py    # Google Drive
│       ├── assistant_forms.py    # Google Forms
│       ├── assistant_notebook.py # Google Colab
│       ├── assistant_recorder.py # Enregistreur vocal & transcription
│       ├── assistant_sheets.py   # Google Sheets
│       ├── assistant_slides.py   # Google Slides
│       ├── assistant_tasks.py    # Google Tasks
│       └── secrets_manager.py    # Gestionnaire de secrets (local + Cloud)
├── Dockerfile                # Image conteneur optimisée (Python 3.11-slim + ffmpeg)
├── docker-compose.yml        # Orchestration Docker avec montages sécurisés
├── pyproject.toml            # Configuration du package Python
├── requirements.txt          # Dépendances Python du projet
├── .env                      # Clé d'API Gemini (privé, ignoré par Git)
├── .gitignore                # Exclusion stricte des secrets et caches
└── README.md                 # Ce document
```

---

## 🚀 Installation & Configuration

### 1. Variables d'environnement (`.env`)

1. Créez un fichier `.env` à la racine en copiant `config/.env.example` :
   ```bash
   cp config/.env.example .env
   ```
2. Renseignez votre clé API Gemini (disponible gratuitement sur [Google AI Studio](https://aistudio.google.com/)) :
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```

### 2. Identifiants Google OAuth2 (`credentials.json`)

1. Rendez-vous sur la [Google Cloud Console](https://console.cloud.google.com/).
2. Activez les APIs nécessaires : **Drive, Docs, Sheets, Slides, Calendar, Tasks, Forms**.
3. Dans **Identifiants (Credentials)**, créez un identifiant client **OAuth 2.0 (Application de bureau / Desktop app)**.
4. Téléchargez le fichier JSON et placez-le dans le dossier :
   ```text
   config/credentials.json
   ```

### 3. Première authentification & génération du `token.json`

Pour générer votre premier jeton d'accès Google, lancez une commande d'authentification :

```powershell
python -m src.auth
```
*(Une fenêtre de navigateur s'ouvre pour autoriser l'accès à votre compte Google. Le fichier `config/token.json` est créé automatiquement).*

---

## ⚡ Démarrage Rapide

### Option A : Démarrage via Docker (Recommandé)

Le serveur tourne en tâche de fond de façon isolée et accessible à tous vos autres projets :

```bash
# 1. Démarrer (ou reconstruire après modification)
docker compose up -d --build

# 2. Vérifier l'état du conteneur
docker compose ps

# 3. Consulter les logs en temps réel
docker compose logs -f

# 4. Arrêter le conteneur
docker compose down
```

> [!TIP]
> **Affichage dans Docker Desktop :**
> - Dans l'onglet **"Containers"**, vous verrez le conteneur actif : **`google-workspace-hub`** (point vert opérationnel).
> - L'onglet **"Build history"** conserve simplement l'historique des constructions passées pour votre information.

---

### Option B : Démarrage de l'API en local

Avec votre environnement virtuel Python activé :

```powershell
# Via le script batch :
.\scripts\start_api.bat

# Ou directement avec Uvicorn :
uvicorn src.server:app --reload --port 8000
```

---

### Option C : Utilisation en ligne de commande (CLI)

Vous pouvez exécuter directement les commandes d'administration :

```powershell
# Via le script batch :
.\scripts\gassist.bat drive search "rapport"

# Ou via le module Python :
python -m src.google_assistant calendar list_events --max 5
```

---

## 📖 Documentation Interactive de l'API (Swagger)

Une fois l'API démarrée, ouvrez dans votre navigateur :
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

Vous pouvez tester immédiatement chaque route directement depuis votre navigateur avec le bouton **"Try it out"**.

Exemple de test rapide avec cURL :
```bash
curl http://localhost:8000/health
```

Réponse JSON :
```json
{
  "status": "ok",
  "service": "Google Workspace & Gemini Hub API",
  "google_auth_ready": true,
  "gemini_api_key_configured": true
}
```

---

## 🛠️ Référence des Commandes CLI

### 📂 Drive

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `drive search` | `<query>` | Recherche des fichiers dans Google Drive |
| `drive download` | `<file_id>` | Télécharge un fichier vers votre machine |
| `drive upload` | `<file_path>` | Téléverse un fichier vers Google Drive |
| `drive share` | `<file_id> --email <email> --role [reader\|writer\|commenter]` | Partage un fichier avec un utilisateur |
| `drive empty_trash` | *(aucun)* | Vide définitivement la corbeille |
| `drive create_folder` | `<title> [--parent <parent_id>]` | Crée un nouveau dossier |
| `drive list_folder` | `<folder_id>` | Liste le contenu d'un dossier |

```powershell
.\scripts\gassist.bat drive search "budget 2026"
.\scripts\gassist.bat drive upload "C:\rapport.pdf"
```

---

### 📄 Docs

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `docs read` | `<id>` | Affiche le texte brut d'un document |
| `docs append_text` | `<id> <text>` | Ajoute du texte en fin de document |
| `docs replace_text` | `<id> <old_text> <new_text>` | Remplace du texte dans le document |
| `docs format_bold` | `<id> <text>` | Met en gras les occurrences d'un texte |
| `docs create_from_template` | `<template_id> <title> <variables_json>` | Crée un doc depuis un modèle avec variables |
| `docs export_pdf` | `<id> <output_filename>` | Exporte le document en PDF |
| `docs export_docx` | `<id> <output_filename>` | Exporte le document en Word (.docx) |

---

### 📊 Sheets

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `sheets add_sheet` | `<id> <title>` | Ajoute un nouvel onglet |
| `sheets read_range` | `<id> <range_name>` | Lit une plage de cellules (ex: `Feuille1!A1:C10`) |
| `sheets add_formula` | `<id> <cell_range> <formula>` | Insère une formule de calcul |
| `sheets format_green` | `<id> <cell_range>` | Met en vert l'arrière-plan d'une plage |

---

### 🖼️ Slides

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `slides create_presentation` | `<title>` | Crée une présentation vierge |
| `slides clone_slide` | `<presentation_id> <slide_id>` | Duplique une diapositive |
| `slides replace_variables` | `<presentation_id> <variable> <valeur>` | Remplace `{{variable}}` par sa valeur |
| `slides insert_textbox` | `<presentation_id> <page_id> <text>` | Ajoute une zone de texte |

---

### 📅 Calendar

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `calendar list_events` | `[--max <n>]` | Liste les prochains événements |
| `calendar create_event` | `<summary> <start_time> <end_time>` | Crée un événement planifié |
| `calendar delete_event` | `<event_id>` | Supprime un événement |
| `calendar add_reminder` | `<event_id> <minutes>` | Ajoute un rappel contextuel |

---

### ✅ Tasks

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `tasks create_list` | `<title>` | Crée une liste de tâches |
| `tasks list_pending` | `<list_id>` | Liste les tâches non complétées |
| `tasks add_task` | `<list_id> <title> [--due <YYYY-MM-DD>]` | Ajoute une tâche avec échéance |
| `tasks complete_task` | `<list_id> <task_id>` | Marque une tâche comme terminée |

---

### 📝 Forms

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `forms create` | `<title>` | Crée un nouveau formulaire Google |
| `forms get_responses` | `<form_id>` | Affiche les réponses collectées |
| `forms add_question` | `<form_id> <question_title> [--type TEXT\|RADIO]` | Ajoute une question au formulaire |
| `forms close_form` | `<form_id>` | Ferme les inscriptions |

---

### 🤖 AI (Gemini)

| Commande | Arguments | Description |
| :--- | :--- | :--- |
| `ai parse_event` | `"<phrase en langage naturel>"` | Analyse la phrase et planifie l'événement dans Calendar |
| `ai summarize` | `<doc_id>` | Résume un Google Doc de manière structurée |
| `ai ask_sheet` | `<sheet_id> "<question>"` | Interroge les données d'un tableur en langage naturel |
| `ai proofread` | `<doc_id>` | Corrige et optimise la syntaxe d'un Google Doc |
| `ai generate_slides` | `"<sujet>" [--num_slides <n>]` | Génère un diaporama complet structuré avec Gemini |
| `ai generate_doc` | `<doc_id> "<prompt>"` | Rédige du contenu via l'IA directement dans le Doc |
| `ai stats` | *(aucun)* | Affiche le tableau de bord de consommation des tokens |

```powershell
# Planifier une réunion en langage naturel
.\scripts\gassist.bat ai parse_event "Point projet demain de 10h à 11h"

# Poser une question sur un Google Sheet
.\scripts\gassist.bat ai ask_sheet "1abc..." "Quel est le produit le plus rentable ?"
```

---

## 💡 Standard vs IA (Coûts & Tokens)

1. **Actions Standards (0 Token, 100% Gratuites)**  
   Les commandes de manipulation de fichiers (`drive`, `docs`, `sheets`, `slides`, `calendar`, `tasks`, `forms`) communiquent directement avec les APIs Google Workspace officielles. Elles sont **entièrement gratuites et illimitées**.
2. **Actions Intelligentes (Consommation de Tokens Gemini)**  
   Les fonctionnalités `ai ...` sollicitent les modèles Gemini. L'historique et votre budget restant sont suivis automatiquement dans `data/usage_history.json` et consultables via :
   ```powershell
   .\scripts\gassist.bat ai stats
   ```

---

## 📚 Guides et Documentation Complémentaire

- 🌐 [Guide d'Intégration Multi-Projets (API REST)](docs/GUIDE_INTEGRATION_MULTI_PROJETS.md) : Comment connecter React, Next.js, Node.js ou d'autres projets Python à ce hub.
- 📖 [Guide d'Utilisation Détaillé](docs/Guide_Utilisation.md) : Guide pas à pas des fonctionnalités et astuces d'utilisation.
- 📋 [Sommaire des Fonctions](docs/Sommaire%20fonction.md) : Synthèse technique complète de chaque module.
- ☁️ [Guide Google Cloud & Déploiement](docs/Sommaire_Google_Cloud.md) : Paramétrage des quotas, Secret Manager et déploiement sur VM.

---

## 🔧 Dépannage & Astuces Docker

### Comprendre l'affichage Docker Desktop
- **Onglet "Containers"** : C'est ici que vit votre serveur actif **`google-workspace-hub`**.
- **Onglet "Build history"** : Conserve simplement l'historique des compilations passées. Vous pouvez supprimer les anciennes lignes avec la poubelle 🗑️.

### Erreur `credentials.json introuvable`
Vérifiez que le fichier téléchargé depuis Google Cloud Console est bien nommé `credentials.json` et se trouve dans le dossier `config/credentials.json`.

### Erreur `token expiré / ré-authentification`
Supprimez simplement `config/token.json` et relancez une commande pour ouvrir la page Google d'autorisation :
```powershell
Remove-Item config/token.json
python -m src.auth
```

### Port 8000 déjà utilisé
Si le port 8000 est déjà occupé par un autre processus sur votre machine :
- En local : `uvicorn src.server:app --port 8080`
- Dans Docker : modifiez la ligne `ports: - "8080:8000"` dans [docker-compose.yml](file:///c:/Users/alves/Desktop/Projet%20Perso/Projet%20API,IA,workspace/docker-compose.yml).
