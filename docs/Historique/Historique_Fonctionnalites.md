# 📜 Historique des Évolutions & Répertoire des Fonctions

Ce document retrace l'historique complet des fonctionnalités ajoutées au projet **Assistant Ultime Google Workspace**, les détails techniques d'implémentation, ainsi que les informations supplémentaires nécessaires à l'exploitation et à l'administration de l'outil.

---

## 📑 Sommaire

1. [Vue d'Ensemble & Chronologie des Versions](#1-vue-densemble--chronologie-des-versions)
   - [v1.0 : Socle Fondateur Google Workspace](#v10--socle-fondateur-google-workspace)
   - [v1.1 : Module Avancé Google Forms](#v11--module-avancé-google-forms)
   - [v1.2 : Intégration Google Colab / Notebooks](#v12--intégration-google-colab--notebooks)
   - [v1.3 : Super-Pouvoirs IA Gemini (Multimodal & NLP)](#v13--super-pouvoirs-ia-gemini-multimodal--nlp)
   - [v1.4 : Enregistrement Audio & Synthèse Réunions / Cours](#v14--enregistrement-audio--synthèse-réunions--cours)
   - [v1.5 : Transcription Intégrale & Export Word (.docx)](#v15--transcription-intégrale--export-word-docx)
2. [Répertoire Détaillé des Fonctions par Service](#2-répertoire-détaillé-des-fonctions-par-service)
   - [📂 Google Drive (`assistant_drive.py`)](#-google-drive-assistant_drivepy)
   - [📄 Google Docs (`assistant_docs.py`)](#-google-docs-assistant_docspy)
   - [📊 Google Sheets (`assistant_sheets.py`)](#-google-sheets-assistant_sheetspy)
   - [🖼️ Google Slides (`assistant_slides.py`)](#️-google-slides-assistant_slidespy)
   - [📅 Google Calendar (`assistant_calendar.py`)](#-google-calendar-assistant_calendarpy)
   - [✅ Google Tasks (`assistant_tasks.py`)](#-google-tasks-assistant_taskspy)
   - [📝 Google Forms (`assistant_forms.py`)](#-google-forms-assistant_formspy)
   - [🧠 Google Colab Notebooks (`assistant_notebook.py`)](#-google-colab-notebooks-assistant_notebookpy)
   - [🤖 Intelligence Artificielle Gemini (`assistant_ai.py`)](#-intelligence-artificielle-gemini-assistant_aipy)
   - [🎙️ Enregistrement & Réunions (`assistant_recorder.py`)](#️-enregistrement--réunions-assistant_recorderpy)
3. [Informations Techniques Supplémentaires](#3-informations-techniques-supplémentaires)
   - [Architecture du Projet](#architecture-du-projet)
   - [Authentification OAuth 2.0 & Portée des Scopes](#authentification-oauth-20--portée-des-scopes)
   - [Configuration Gemini API & Gestion des Modèles](#configuration-gemini-api--gestion-des-modèles)
   - [Suivi du Budget et Tokens (`usage_history.json`)](#suivi-du-budget-et-tokens-usage_historyjson)
   - [Export Natif Word (.docx) sans dépendance lourde](#export-natif-word-docx-sans-dépendance-lourde)
   - [Raccourci Shell Windows `gassist`](#raccourci-shell-windows-gassist)

---

## 1. Vue d'Ensemble & Chronologie des Versions

### v1.0 : Socle Fondateur Google Workspace
- Mise en place du dispatcher CLI principal dans `google_assistant.py`.
- Authentification unique OAuth 2.0 Google Workspace gérée dans `auth.py`.
- Intégration des services de base :
  - **Drive** : recherche avec rendu enrichi en tableau Rich, upload, download, partage d'accès, vidage corbeille, gestion des dossiers et révisions.
  - **Docs** : lecture du texte brut, formatage en gras ciblé, recherche/remplacement, export PDF, extraction de plan et lecture des commentaires.
  - **Sheets** : lecture de plages, insertion d'onglets, injection de formules, coloration conditionnelle, création de filtres et graphiques basiques.
  - **Slides** : création de présentations, clonage de diapositives, remplacement de variables dynamiques, export individuel ou PDF, génération de masse via CSV.
  - **Calendar** : listing des réunions, création avec invités/fuseau horaire, suppression, gestion des réponses RSVP et alertes/rappels.
  - **Tasks** : création de listes, ajout de tâches avec échéances ISO, validation et purge des tâches terminées.

### v1.1 : Module Avancé Google Forms
- Fichier dédié : `services/assistant_forms.py`.
- **Création dynamique de formulaires** Google Forms.
- **Ajout de questions interactives** de types variés (textuel, boutons radio, cases à cocher).
- **Logique conditionnelle** : redirection automatique des répondants vers des sections spécifiques en fonction de leurs réponses (`add_conditional_question`).
- **Insertion de médias** : injection d'images d'en-tête ou illustratives via URL (`ImageItem`).
- **Collecte & Export** : interrogation de toutes les réponses et extraction automatique au format CSV local (`export_responses`).
- **Clôture** programmatique de formulaire (`close_form`).

### v1.2 : Intégration Google Colab / Notebooks
- Fichier dédié : `services/assistant_notebook.py`.
- **Création instantanée de notebooks Colab** (`.ipynb`) préconfigurés directement à la racine ou dans un dossier Google Drive.
- **Listing des notebooks** Gemini / Colab avec métadonnées (ID, nom, lien d'ouverture directe dans Google Colab).

### v1.3 : Super-Pouvoirs IA Gemini (Multimodal & NLP)
- Fichier dédié : `services/assistant_ai.py`.
- Utilisation du nouveau SDK officiel `google-genai` et passage au modèle **Gemini 3.6 Flash**.
- **Compréhension du langage naturel** :
  - Parsing de texte libre pour planifier des événements Google Calendar (`parse_event`).
  - Questions/réponses en français sur des classeurs Sheets sans formule manuelle (`ask_sheet`).
- **Traitement de texte & Rédaction** :
  - Résumé exécutif automatique d'un document Docs (`summarize`).
  - Relecture critique, correction orthographique et stylistique (`proofread`).
  - Rédaction assistée et insertion directe dans un document (`generate_doc`).
  - Classification automatique de lignes d'un tableau en catégories (`classify_sheet`).
- **Génération créative** :
  - Création de présentations Google Slides complètes (titre, contenu, design, conclusion) à partir d'un simple thème (`generate_slides`).
- **Gestion budgétaire & Sécurité** :
  - Simulation de coût et calcul de tokens préalable avant exécution (`estimate_cost`).
  - Dashboard de consommation et suivi du budget de tokens (`stats`).

### v1.4 : Enregistrement Audio & Synthèse Réunions / Cours
- Fichier dédié : `services/assistant_recorder.py`.
- Capture audio native en direct du microphone (16 kHz mono) avec arrêt interactif via `[ENTRÉE]`.
- Mode enregistrement en tâche de fond (`start` / `stop`) avec suivi d'état dans `.recording_state.json`.
- Envoi automatique du fichier `.wav` vers l'API Gemini multimodale.
- Génération d'une fiche de réunion avec participants, résumé, décisions et injection des actions dans Google Tasks.

### v1.5 : Transcription Intégrale & Export Word (.docx)
- **Mise à niveau du modèle** : bascule complète vers `gemini-3.6-flash`.
- **Transcription intégrale** : ajout du champ `full_transcript` dans le schéma structuré Pydantic `MeetingNotes` et le prompt IA, permettant de capturer l'intégralité des propos, discussions, cours et questions/réponses.
- **Section 5 dédiée** : insertion de la transcription exhaustive dans le document final.
- **Export Multi-Format (Google Docs & Word .docx)** :
  - Création automatique du Google Doc en ligne.
  - Conversion et export simultané au format Microsoft Word (`.docx`) dans le dossier `recordings/`.
  - Nouveau paramètre CLI `--format [both|word|docs]`.

---

## 2. Répertoire Détaillé des Fonctions par Service

### 📂 Google Drive (`assistant_drive.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `drive search` | `<query>` | Recherche des fichiers par mot-clé avec affichage en tableau coloré (Nom, Type, ID, Lien). |
| `drive download` | `<file_id>` | Télécharge un fichier binaire depuis Google Drive vers la machine locale. |
| `drive upload` | `<file_path>` | Téléverse un fichier local vers la racine de Google Drive. |
| `drive share` | `<file_id> --email <email> --role <role>` | Partage un fichier avec des droits spécifiques (`reader`, `writer`, `commenter`). |
| `drive empty_trash` | *(aucun)* | Purge et vide intégralement la corbeille de Google Drive. |
| `drive restore_version` | `<id> <revision_id>` | Restaure une version historique précise d'un fichier. |
| `drive create_folder` | `<title> [--parent <parent_id>]` | Crée un nouveau dossier (racine ou sous-dossier). |
| `drive list_folder` | `<folder_id>` | Liste le contenu complet d'un dossier sous forme de tableau Rich. |

---

### 📄 Google Docs (`assistant_docs.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `docs read` | `<id>` | Affiche le texte brut d'un document Docs directement dans la console. |
| `docs extract_structure` | `<id>` | Extrait et liste l'arborescence des titres et sous-titres (`HEADING_1`, etc.). |
| `docs list_comments` | `<id>` | Liste tous les commentaires et discussions associés au document. |
| `docs format_bold` | `<id> <text>` | Recherche toutes les occurrences du texte et les met en gras. |
| `docs insert_image` | `<id> <url>` | Télécharge et insère une image web à la fin du document. |
| `docs replace_text` | `<id> <old_text> <new_text>` | Remplace globalement un mot ou une phrase par un autre texte. |
| `docs append_text` | `<id> <text>` | Ajoute un paragraphe ou une section à la fin du document. |
| `docs create_from_template` | `<template_id> <title> <json_vars>` | Duplique un modèle et remplace dynamiquement les variables balisées `{{CLE}}`. |
| `docs export_pdf` | `<id> <output_filename>` | Exporte et télécharge le document sous forme de fichier PDF. |
| `docs export_docx` | `<id> <output_filename>` | Exporte et convertit le document en fichier Microsoft Word (`.docx`). |

---

### 📊 Google Sheets (`assistant_sheets.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `sheets read_range` | `<id> <range_name>` | Lit et affiche le contenu d'une plage (ex: `Feuille 1!A1:D10`). |
| `sheets add_sheet` | `<id> <title>` | Crée un nouvel onglet avec le titre spécifié dans le classeur. |
| `sheets add_formula` | `<id> <cell_range> <formula>` | Écrit une formule de calcul Google Sheets (ex: `=SOMME(B2:B10)`). |
| `sheets format_green` | `<id> <cell_range>` | Applique un style avec fond vert sur la plage sélectionnée. |
| `sheets add_chart` | `<id> <tab_id>` | Génère et insère un graphique en barres basique sur la feuille. |
| `sheets add_filter` | `<id> <tab_id>` | Active les menus déroulants de filtrage sur les colonnes. |
| `sheets export_pdf` | `<id> <tab_id> <filename>` | Exporte un onglet particulier sous forme de document PDF. |

---

### 🖼️ Google Slides (`assistant_slides.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `slides create_presentation` | `<title>` | Crée une présentation Google Slides vierge. |
| `slides clone_slide` | `<presentation_id> <slide_id>` | Duplique une diapositive cible au sein de la présentation. |
| `slides replace_variables` | `<presentation_id> <variable> <valeur>` | Remplace les étiquettes textuelles (ex: `{{NOM}}`) par une valeur concrète. |
| `slides insert_textbox` | `<presentation_id> <page_id> <text>` | Insère une nouvelle zone de texte positionnée sur la diapositive. |
| `slides insert_table` | `<presentation_id> <page_id> <rows> <cols>` | Insère un tableau vide de taille définie. |
| `slides mass_generate` | `<id> <slide_id> <csv_path>` | Génère une suite de diapositives personnalisées à partir des lignes d'un fichier CSV. |
| `slides export_slide` | `<presentation_id> <slide_id> <output>` | Exporte une seule diapositive sous forme d'image. |
| `slides export_pdf` | `<presentation_id> <output_filename>` | Exporte l'ensemble de la présentation en un unique fichier PDF. |

---

### 📅 Google Calendar (`assistant_calendar.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `calendar list_events` | `[--max <n>]` | Liste les événements à venir de votre agenda principal. |
| `calendar create_event` | `<summary> <start> <end> [--emails] [--timezone]` | Planifie un rendez-vous avec invités et fuseau horaire. |
| `calendar delete_event` | `<event_id>` | Annule et supprime définitivement une réunion. |
| `calendar add_reminder` | `<event_id> <minutes>` | Configure une notification/rappel avant le début de la réunion. |
| `calendar rsvp` | `<event_id> <response>` | Répond à une invitation (`accepted`, `declined`, `tentative`). |

---

### ✅ Google Tasks (`assistant_tasks.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `tasks create_list` | `<title>` | Crée une nouvelle liste de tâches. |
| `tasks list_pending` | `<list_id>` | Affiche un tableau récapitulatif des tâches non cochées. |
| `tasks add_task` | `<list_id> <title> [--parent] [--due <date>]` | Ajoute une tâche avec date d'échéance optionnelle (`YYYY-MM-DD`). |
| `tasks complete_task` | `<list_id> <task_id>` | Marque une tâche comme effectuée. |
| `tasks clear_completed` | `<list_id>` | Purge toutes les tâches achevées d'une liste. |

---

### 📝 Google Forms (`assistant_forms.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `forms create` | `<title>` | Crée un nouveau formulaire Google Forms vierge. |
| `forms get_responses` | `<form_id>` | Récupère et affiche dans le terminal toutes les soumissions enregistrées. |
| `forms add_question` | `<form_id> <title> [--type]` | Ajoute une question (texte libre, case à cocher, choix unique). |
| `forms add_image` | `<form_id> <image_url>` | Ajoute une image décorative ou explicative dans le formulaire. |
| `forms add_conditional_question` | `<form_id> <title> <json_config>` | Crée une question avec embranchement conditionnel vers d'autres sections. |
| `forms export_responses` | `<form_id> <output_csv>` | Télécharge toutes les réponses sous forme de tableau CSV prêt pour Excel. |
| `forms close_form` | `<form_id>` | Bloque l'accès aux réponses du formulaire (statut fermé). |

---

### 🧠 Google Colab Notebooks (`assistant_notebook.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `notebook create` | `<title>` | Crée un fichier Google Colab `.ipynb` prêt à exécuter du code Python sur le Cloud. |
| `notebook list` | *(aucun)* | Liste l'ensemble des carnets de notes Colab présents sur Google Drive avec leurs URLs. |

---

### 🤖 Intelligence Artificielle Gemini (`assistant_ai.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `ai parse_event` | `<prompt>` | Extrait le titre, l'heure et la date d'une phrase naturelle et l'inscrit dans Calendar. |
| `ai summarize` | `<doc_id>` | Analyse et rédige un résumé exécutif structuré d'un Google Doc. |
| `ai ask_sheet` | `<sheet_id> <question>` | Pose des questions sur un tableur (ex: *"Quel est le commercial le plus rentable ?"*). |
| `ai proofread` | `<doc_id>` | Corrige les fautes d'orthographe, de grammaire et suggère des reformulations. |
| `ai generate_slides` | `<topic> [--num_slides <n>]` | Conçoit et génère une présentation complète avec diapositives structurées. |
| `ai generate_doc` | `<doc_id> <prompt>` | Rédige un contenu détaillé selon vos consignes et l'injecte dans le Doc cible. |
| `ai classify_sheet` | `<id> <read_range> <write_range> <categories>` | Analyse une colonne de texte et remplit une autre colonne avec les catégories adéquates. |
| `ai estimate_cost` | `<doc_id>` | Analyse le volume de tokens d'un document et estime le coût financier sans appel payant. |
| `ai stats` | *(aucun)* | Affiche la consommation actuelle, le coût cumulé et le quota de tokens restant. |
| `ai meeting_audio` | `<audio_file> [--title] [--format]` | Transcrit et analyse un fichier audio, crée le compte-rendu Docs/Word et les tâches Tasks. |

---

### 🎙️ Enregistrement & Réunions (`assistant_recorder.py`)

| Commande | Paramètres | Description |
| :--- | :--- | :--- |
| `record live` | `[--title <titre>] [--format both\|word\|docs]` | Enregistre en direct depuis votre microphone (16 kHz). Arrêt via `[ENTRÉE]`. Analyse audio par Gemini 3.6 Flash, génération du document avec transcription intégrale et création des tâches. |
| `record start` | `[--title <titre>]` | Démarre un enregistrement silencieux en arrière-plan (processus détaché). |
| `record stop` | `[--format both\|word\|docs]` | Interrompt l'enregistrement en tâche de fond et déclenche la synthèse Gemini + Docs + Word + Tasks. |
| `record process` | `<audio_file> [--title] [--format]` | Traite un enregistrement déjà existant sur votre disque dur (`.wav`, `.mp3`, `.m4a`). |

---

## 3. Informations Techniques Supplémentaires

### Architecture du Projet

Le projet suit une architecture modulaire et découplée pour garantir maintenabilité et extensibilité :

```text
Projet API,IA,workspace/
├── google_assistant.py         # Point d'entrée CLI (argparse & routage)
├── auth.py                     # Gestion OAuth 2.0 Google Workspace
├── gassist.bat                 # Lanceur rapide Windows (alias .\gassist)
├── requirements.txt            # Dépendances Python du projet
├── credentials.json            # Identifiants OAuth Client Google Cloud (non versionné)
├── token.json                  # Token d'accès & refresh token utilisateur (non versionné)
├── .env                        # Variables d'environnement privées (GEMINI_API_KEY)
├── usage_history.json          # Journal local de suivi des tokens IA consommés
├── recordings/                 # Stockage des fichiers audio .wav et documents .docx
├── docs/                       # Documentation, guides et historique
│   ├── Sommaire fonction.md    # Sommaire synthétique
│   ├── Guide_Utilisation.md    # Guide d'utilisation pas-à-pas
│   ├── Evolutions.md           # Roadmap et évolutions futures
│   └── Historique/             # Historique des ajouts et versions
│       └── Historique_Fonctionnalites.md
└── services/                   # Modules métiers indépendants
    ├── assistant_drive.py      # Google Drive API v3
    ├── assistant_docs.py       # Google Docs API v1 & Drive Export
    ├── assistant_sheets.py     # Google Sheets API v4
    ├── assistant_slides.py     # Google Slides API v1
    ├── assistant_calendar.py   # Google Calendar API v3
    ├── assistant_tasks.py      # Google Tasks API v1
    ├── assistant_forms.py      # Google Forms API v1
    ├── assistant_notebook.py   # Google Colab (Drive MIME type)
    ├── assistant_ai.py         # Gemini 3.6 Flash (google-genai)
    └── assistant_recorder.py   # Enregistrement audio (sounddevice / numpy)
```

---

### Authentification OAuth 2.0 & Portée des Scopes

Le fichier `auth.py` gère le cycle de vie des autorisations :
1. Lecture des identifiants client depuis `credentials.json` (issu de la console Google Cloud).
2. Vérification et rechargement automatique du jeton rafraîchi dans `token.json`.
3. Si le jeton est expiré ou absent, ouverture automatique du navigateur pour validation par l'utilisateur.

**Scopes actifs requis :**
- `https://www.googleapis.com/auth/drive`
- `https://www.googleapis.com/auth/documents`
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/presentations`
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/tasks`
- `https://www.googleapis.com/auth/forms.body`
- `https://www.googleapis.com/auth/forms.responses.readonly`

---

### Configuration Gemini API & Gestion des Modèles

Les fonctionnalités d'intelligence artificielle reposent sur le SDK officiel `google-genai` (Google GenAI SDK 2025/2026).
- **Configuration** : la clé d'API doit être définie dans `.env` :
  ```env
  GEMINI_API_KEY=AIzaSy...
  ```
- **Modèle de référence** : `gemini-3.6-flash`.
  - Ce modèle offre un temps de réponse instantané, un support multimodal natif (texte, tableurs, audio jusqu'à plusieurs heures) et une fenêtre de contexte étendue (> 1 million de tokens).
  - *Note d'évolution :* L'ancien modèle `gemini-2.5-flash` a été définitivement déprécié et remplacé par `gemini-3.6-flash`.

---

### Suivi du Budget et Tokens (`usage_history.json`)

Chaque appel aux fonctions IA de `assistant_ai.py` interroge les métadonnées de consommation renvoyées par Gemini (`usage_metadata`) et met à jour automatiquement `usage_history.json` :

```json
{
  "total_prompt_tokens": 1520,
  "total_candidates_tokens": 890,
  "total_tokens": 2410,
  "requests_count": 5
}
```

La commande `.\gassist ai stats` affiche un tableau de bord visuel indiquant :
- Le budget global alloué (par défaut 1 000 000 tokens).
- Les tokens consommés.
- Les tokens restants.
- Le nombre total de requêtes exécutées.

---

### Export Natif Word (.docx) sans dépendance lourde

Pour garantir une portabilité maximale sans nécessiter l'installation de bibliothèques lourdes ou instables, l'export Microsoft Word (`.docx`) s'appuie sur le mécanisme d'export natif de Google Drive API (`assistant_docs.export_word`) :

```python
drive_service.files().export_media(
    fileId=doc_id,
    mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
)
```

**Avantages :**
1. Mise en page, styles de titres, listes à puces et tableaux parfaitement convertis par le moteur de rendu officiel Google Drive.
2. Compatibilité totale avec Microsoft Word, LibreOffice et Apple Pages.
3. Aucune dépendance tierce à compiler.

---

### Raccourci Shell Windows `gassist`

Un script batch `gassist.bat` est configuré à la racine du projet pour simplifier les saisies :

Au lieu de saisir :
```powershell
python google_assistant.py record live --title "Mon Cours"
```
Vous pouvez simplement utiliser :
```powershell
.\gassist record live --title "Mon Cours"
```
Ou pour vérifier le budget IA :
```powershell
.\gassist ai stats
```
