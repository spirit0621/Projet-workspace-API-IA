# 🤖 Assistant Ultime Google Workspace

Un outil CLI puissant pour automatiser et contrôler tous vos services **Google Workspace** (Drive, Docs, Sheets, Slides, Calendar, Tasks, Forms) directement depuis votre terminal — avec une couche d'**intelligence artificielle Gemini** intégrée.

---

## 📋 Table des Matières

1. [Prérequis](#-prérequis)
2. [Installation](#-installation)
3. [Configuration](#-configuration)
   - [Clé API Gemini](#1-clé-api-gemini-pour-les-fonctions-ia)
   - [Credentials Google OAuth2](#2-credentials-google-oauth2)
   - [Première authentification](#3-première-authentification)
4. [Utilisation](#-utilisation)
5. [Référence des Commandes](#-référence-des-commandes)
   - [Drive](#-drive)
   - [Docs](#-docs)
   - [Sheets](#-sheets)
   - [Slides](#-slides)
   - [Calendar](#-calendar)
   - [Tasks](#-tasks)
   - [Forms](#-forms)
   - [Notebook](#-notebook)
   - [AI Gemini](#-ai-gemini)
26. [Standard vs IA (Coûts & Tokens)](#-standard-vs-ia-coûts--tokens)
27. [Structure du Projet](#-structure-du-projet)
28. [Dépannage](#-dépannage)

---

## 🔧 Prérequis

- **Python 3.9+** installé sur votre système
- Un compte **Google** avec accès à Google Workspace
- Un projet **Google Cloud** avec les APIs activées
- Une clé **Gemini API** (pour les fonctions IA uniquement)

---

## 🚀 Installation

### 1. Cloner / Télécharger le projet

```bash
cd "c:\Users\alves\Desktop\google cloud"
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
```

### 3. Activer l'environnement virtuel

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Clé API Gemini (pour les fonctions IA)

> Les commandes `ai summarize`, `ai parse_event`, `ai ask_sheet`, `ai proofread` et `ai generate_slides` nécessitent une clé API Gemini.

1. Rendez-vous sur [Google AI Studio](https://aistudio.google.com/)
2. Cliquez sur **"Get API key"** puis **"Create API key"**
3. Copiez la clé générée
4. Créez un fichier `.env` à la racine du projet :

```env
GEMINI_API_KEY=VOTRE_CLE_API_ICI
```

> **Attention :** Ne partagez jamais votre fichier `.env` ! Il est déjà dans `.gitignore`.

---

### 2. Credentials Google OAuth2

> Obligatoire pour toutes les commandes (Drive, Calendar, Docs, etc.).

1. Rendez-vous sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un projet ou sélectionnez un projet existant
3. Activez les APIs suivantes (dans **Library**) :
   - Google Drive API
   - Google Docs API
   - Google Sheets API
   - Google Slides API
   - Google Calendar API
   - Google Tasks API
   - Google Forms API
4. Allez dans **APIs & Services → Credentials**
5. Cliquez sur **"+ Create Credentials"** → **"OAuth 2.0 Client IDs"**
6. Choisissez **"Desktop app"** comme type d'application
7. Téléchargez le fichier JSON et renommez-le `credentials.json`
8. Placez `credentials.json` à la **racine du projet**

---

### 3. Première authentification

Au premier lancement, une fenêtre de navigateur s'ouvrira pour connecter votre compte Google. Un fichier `token.json` sera créé automatiquement pour les sessions suivantes.

```bash
.\gassist calendar list_events
```

---

## Utilisation

### Avec le raccourci Windows (recommandé)

```powershell
.\gassist <service> <action> [arguments]
```

### Avec Python directement

```powershell
python google_assistant.py <service> <action> [arguments]
```

### Exemples rapides

```bash
# Rechercher un fichier dans Drive
.\gassist drive search "rapport mensuel"

# Lister vos 5 prochains événements
.\gassist calendar list_events --max 5

# Créer un événement via IA en langage naturel
.\gassist ai parse_event "Réunion avec Marc demain à 14h"

# Résumer un document Google Docs
.\gassist ai summarize "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
```

---

## Référence des Commandes

### Drive

| Commande                  | Arguments                                                      | Description                                          |
| ------------------------- | -------------------------------------------------------------- | ---------------------------------------------------- |
| `drive search`          | `<query>`                                                    | Recherche des fichiers (affiche Nom, Type, ID, Lien) |
| `drive download`        | `<file_id>`                                                  | Télécharge un fichier vers votre ordinateur        |
| `drive upload`          | `<file_path>`                                                | Envoie un fichier local vers Google Drive            |
| `drive share`           | `<file_id> --email <email> --role [reader\|writer\|commenter]` | Partage un fichier avec un collaborateur             |
| `drive empty_trash`     | *(aucun)*                                                    | Vide la corbeille Google Drive                       |
| `drive restore_version` | `<id> <revision_id>`                                         | Restaure une ancienne version d'un fichier           |
| `drive create_folder`   | `<title> [--parent <parent_id>]`                             | Crée un dossier (optionnellement dans un parent)    |
| `drive list_folder`     | `<folder_id>`                                                | Liste les fichiers d'un dossier spécifique          |

**Exemples :**

```bash
.\gassist drive search "budget 2025"
.\gassist drive upload "C:\Documents\rapport.pdf"
.\gassist drive share "1abc..." --email "collegue@gmail.com" --role writer
.\gassist drive create_folder "Projets 2025" --parent "0Bxxx..."
```

---

### Docs

| Commande                   | Arguments                      | Description                                   |
| -------------------------- | ------------------------------ | --------------------------------------------- |
| `docs read`              | `<id>`                       | Affiche le texte brut du document             |
| `docs extract_structure` | `<id>`                       | Affiche les titres et sous-titres             |
| `docs list_comments`     | `<id>`                       | Liste tous les commentaires                   |
| `docs format_bold`       | `<id> <text>`                | Met en gras toutes les occurrences d'un texte |
| `docs insert_image`      | `<id> <url>`                 | Insère une image depuis une URL              |
| `docs replace_text`      | `<id> <old_text> <new_text>` | Chercher/Remplacer dans le document           |
| `docs append_text`       | `<id> <text>`                | Ajoute un paragraphe à la fin du document     |
| `docs create_from_template`| `<template_id> <title> <variables_json>` | Crée un document depuis un modèle avec variables |
| `docs export_pdf`        | `<id> <output_filename>`     | Exporte en PDF                                |
| `docs export_docx`       | `<id> <output_filename>`     | Exporte en Word (.docx)                       |

**Exemples :**

```bash
.\gassist docs read "1BxiMVs0XRA5..."
.\gassist docs replace_text "1BxiMVs0XRA5..." "Jean Dupont" "Marie Martin"
.\gassist docs export_pdf "1BxiMVs0XRA5..." "mon_document.pdf"
```

---

### Sheets

| Commande                | Arguments                       | Description                                      |
| ----------------------- | ------------------------------- | ------------------------------------------------ |
| `sheets add_sheet`    | `<id> <title>`                | Ajoute un nouvel onglet                          |
| `sheets read_range`   | `<id> <range_name>`           | Lit une plage de cellules (ex:`Sheet1!A1:C10`) |
| `sheets add_formula`  | `<id> <cell_range> <formula>` | Insère une formule dans une plage               |
| `sheets format_green` | `<id> <cell_range>`           | Formate une plage avec un fond vert              |
| `sheets add_chart`    | `<id> <tab_id>`               | Génère un graphique automatiquement            |
| `sheets add_filter`   | `<id> <tab_id>`               | Active les filtres sur les colonnes              |
| `sheets export_pdf`   | `<id> <tab_id> <filename>`    | Exporte un onglet en PDF                         |

**Exemples :**

```bash
.\gassist sheets read_range "1abc..." "Feuille1!A1:D20"
.\gassist sheets add_formula "1abc..." "B2" "=SUM(A1:A10)"
.\gassist sheets format_green "1abc..." "A1:F1"
```

---

### Slides

| Commande                       | Arguments                                          | Description                                |
| ------------------------------ | -------------------------------------------------- | ------------------------------------------ |
| `slides create_presentation` | `<title>`                                        | Crée une présentation vierge             |
| `slides clone_slide`         | `<presentation_id> <slide_id>`                   | Duplique une diapositive                   |
| `slides replace_variables`   | `<presentation_id> <variable> <valeur>`          | Remplace`{{variable}}` par une valeur    |
| `slides export_slide`        | `<presentation_id> <slide_id> <output_filename>` | Exporte une slide en image                 |
| `slides export_pdf`          | `<presentation_id> <output_filename>`            | Exporte toute la présentation au format PDF |
| `slides insert_textbox`      | `<presentation_id> <page_id> <text>`             | Insère une zone de texte                  |
| `slides insert_table`        | `<presentation_id> <page_id> <rows> <cols>`      | Insère un tableau                         |
| `slides mass_generate`       | `<id> <slide_id> <csv_path>`                     | Génère des slides en masse depuis un CSV |

**Exemples :**

```bash
.\gassist slides create_presentation "Présentation Q4 2025"
.\gassist slides replace_variables "1pPP..." "{{NOM}}" "Marie Martin"
.\gassist slides mass_generate "1pPP..." "g123..." "contacts.csv"
```

---

### Calendar

| Commande                  | Arguments                                                     | Description                                                           |
| ------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------- |
| `calendar list_events`  | `[--max <n>]`                                               | Liste les prochains événements (10 par défaut)                     |
| `calendar create_event` | `<summary> <start_time> <end_time> [--emails] [--timezone]` | Crée un événement                                                  |
| `calendar delete_event` | `<event_id>`                                                | Supprime un événement                                               |
| `calendar add_reminder` | `<event_id> <minutes>`                                      | Ajoute un rappel en minutes avant l'événement                       |
| `calendar rsvp`         | `<event_id> <response>`                                     | Répond à une invitation (`accepted`, `declined`, `tentative`) |

**Exemples :**

```bash
.\gassist calendar list_events --max 20
.\gassist calendar create_event "Réunion équipe" "2025-09-10T09:00:00" "2025-09-10T10:00:00" --emails "alice@gmail.com,bob@gmail.com" --timezone "Europe/Paris"
.\gassist calendar rsvp "abc123_eventid" accepted
.\gassist calendar add_reminder "abc123_eventid" 30
```

---

### Tasks

| Commande                  | Arguments                                                  | Description                         |
| ------------------------- | ---------------------------------------------------------- | ----------------------------------- |
| `tasks create_list`     | `<title>`                                                | Crée une nouvelle liste de tâches |
| `tasks list_pending`    | `<list_id>`                                              | Liste les tâches non complétées  |
| `tasks add_task`        | `<list_id> <title> [--parent <id>] [--due <YYYY-MM-DD>]` | Ajoute une tâche                   |
| `tasks complete_task`   | `<list_id> <task_id>`                                    | Marque une tâche comme terminée   |
| `tasks clear_completed` | `<list_id>`                                              | Supprime les tâches terminées     |

**Exemples :**

```bash
.\gassist tasks create_list "Projet Alpha"
.\gassist tasks add_task "MDc4..." "Rédiger le rapport" --due 2025-09-15
.\gassist tasks list_pending "MDc4..."
.\gassist tasks complete_task "MDc4..." "task_xyz"
```

---

### Forms

| Commande                           | Arguments                                                   | Description                        |
| ---------------------------------- | ----------------------------------------------------------- | ---------------------------------- |
| `forms create`                   | `<title>`                                                 | Crée un nouveau formulaire        |
| `forms get_responses`            | `<form_id>`                                               | Affiche les réponses              |
| `forms add_question`             | `<form_id> <question_title> [--type TEXT\|RADIO\|CHECKBOX]` | Ajoute une question                |
| `forms export_responses`         | `<form_id> <output_csv>`                                  | Exporte les réponses en CSV       |
| `forms close_form`               | `<form_id>`                                               | Ferme le formulaire                |
| `forms add_image`                | `<form_id> <image_url>`                                   | Ajoute une image au formulaire     |
| `forms add_conditional_question` | `<form_id> <question_title> <json_config>`                | Ajoute une question conditionnelle |

**Exemples :**

```bash
.\gassist forms create "Sondage satisfaction client"
.\gassist forms add_question "1FAIpQL..." "Niveau de satisfaction ?" --type RADIO
.\gassist forms export_responses "1FAIpQL..." "reponses_septembre.csv"
```

---

### Notebook

| Commande            | Arguments   | Description                              |
| ------------------- | ----------- | ---------------------------------------- |
| `notebook create` | `<title>` | Crée un nouveau notebook Google Colab   |
| `notebook list`   | *(aucun)* | Liste tous vos notebooks Colab sur Drive |

**Exemples :**

```bash
.\gassist notebook create "Analyse de données Sept 2025"
.\gassist notebook list
```

---

### AI (Gemini)

> **Requiert une clé `GEMINI_API_KEY` valide dans le fichier `.env`**
>
> Obtenez-la gratuitement sur [aistudio.google.com](https://aistudio.google.com/)

| Commande               | Arguments                        | Description                                                 |
| ---------------------- | -------------------------------- | ----------------------------------------------------------- |
| `ai parse_event`     | `"<texte en langage naturel>"` | Crée un événement Calendar depuis une phrase             |
| `ai summarize`       | `<doc_id>`                     | Résume un Google Docs avec Gemini                          |
| `ai ask_sheet`       | `<sheet_id> "<question>"`      | Répond à une question sur les données d'un Sheet         |
| `ai proofread`       | `<doc_id>`                     | Relit et corrige un document                                |
| `ai generate_slides` | `"<sujet>" [--num_slides <n>]` | Génère une présentation Slides (avec intro/conclusion) |
| `ai generate_doc`    | `<doc_id> "<prompt>"`          | Rédige un texte via l'IA et l'insère à la fin du Doc     |
| `ai classify_sheet`  | `<id> <read_range> <write_range> <categories>` | Analyse et classifie automatiquement des colonnes Sheets |
| `ai estimate_cost`   | `<doc_id>`                     | Estime la taille (tokens) et prévient avant d'exécuter     |
| `ai stats`           | *(aucun)*                      | Affiche le tableau de bord de consommation des tokens IA   |

**Exemples :**

```bash
# Générer et injecter du contenu dans un Docs
.\gassist ai generate_doc "1BxiMVs0XRA5..." "Rédige une introduction sur le marketing"

# Surveiller son quota de tokens
.\gassist ai stats
```

---

## 💡 Standard vs IA (Coûts & Tokens)

Il y a deux "cerveaux" dans ce projet, et il est important de comprendre la différence :

1. **Les commandes Standards (0 Token, 100% gratuit)**
   Les commandes telles que `docs append_text`, `sheets add_formula`, ou `slides export_pdf` communiquent directement avec les APIs Google classiques. Ces appels sont **totalement gratuits et illimités**.

2. **Les commandes IA (Consomment des Tokens)**
   Les commandes préfixées par `ai ...` (`ai summarize`, `ai generate_slides`, etc.) utilisent le modèle **Gemini**. Ce modèle "réfléchit" et facture son effort en "Tokens" (mots). Pour maîtriser cela :
   - Utilisez `.\gassist ai stats` pour voir votre budget de Tokens.
   - Utilisez `.\gassist ai estimate_cost "ID"` pour vérifier la taille d'un document avant traitement.

Pour aller plus loin, lisez notre [Guide Complet d'Utilisation](docs/Guide_Utilisation.md).

---

## Structure du Projet

```
google cloud/
├── google_assistant.py       # Point d'entrée principal (CLI)
├── gassist.bat               # Raccourci Windows pour lancer les commandes
├── auth.py                   # Gestion de l'authentification OAuth2 Google
├── requirements.txt          # Dépendances Python
├── .env                      # Variables d'environnement (GEMINI_API_KEY)  <- A creer
├── .env.example              # Exemple de configuration .env
├── .gitignore                # Fichiers exclus du versioning
├── credentials.json          # Credentials OAuth2 Google  <- A telecharger
├── token.json                # Token d'accès (généré automatiquement)
├── services/                 # Modules par service Google
│   ├── __init__.py
│   ├── assistant_ai.py       # Fonctions IA Gemini
│   ├── assistant_calendar.py
│   ├── assistant_docs.py
│   ├── assistant_drive.py
│   ├── assistant_forms.py
│   ├── assistant_notebook.py
│   ├── assistant_sheets.py
│   ├── assistant_slides.py
│   └── assistant_tasks.py
└── docs/                     # Documentation supplémentaire
    ├── Sommaire fonction.md
    ├── Sommaire_Google_Cloud.md
    └── Evolutions.md
```

---

## Dépannage

### Erreur `429 RESOURCE_EXHAUSTED` (Gemini API)

Votre quota gratuit est épuisé. Solutions :

- Attendez quelques minutes avant de réessayer
- Passez à un [plan payant Gemini API](https://ai.google.dev/gemini-api/docs/billing)
- Vérifiez votre quota sur [Google AI Studio](https://aistudio.google.com/)

### Erreur `credentials.json introuvable`

Le fichier `credentials.json` est absent. Suivez les étapes de la section [Credentials Google OAuth2](#2-credentials-google-oauth2).

### Erreur d'authentification / Token expiré

Supprimez le fichier `token.json` et relancez une commande. Une nouvelle fenêtre de connexion s'ouvrira.

```bash
del token.json
.\gassist calendar list_events
```

### `gassist` n'est pas reconnu comme commande

Assurez-vous d'exécuter les commandes depuis le dossier racine du projet :

```powershell
cd "c:\Users\alves\Desktop\google cloud"
.\gassist calendar list_events
```

### Module Python introuvable

Vérifiez que l'environnement virtuel est bien activé :

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Licence

Projet personnel — libre d'utilisation et de modification.
