# 🛠️ Sommaire des Fonctions de l'Assistant

Ce document liste l'ensemble des commandes et sous-commandes disponibles dans l'Assistant Ultime Google Workspace (`src/google_assistant.py`), classées par service (`src/services/`).

## 📑 Table des Matières

1. [📂 Drive](#-drive-assistant_drivepy)
2. [📄 Docs](#-docs-assistant_docspy)
3. [📊 Sheets](#-sheets-assistant_sheetspy)
4. [🖼️ Slides](#️-slides-assistant_slidespy)
5. [📅 Calendar](#-calendar-assistant_calendarpy)
6. [✅ Tasks](#-tasks-assistant_taskspy)
7. [📝 Forms](#-forms-assistant_formspy)
8. [🧠 Notebook (Google Colab / Gemini)](#-notebook-google-colab--gemini-assistant_notebookpy)
9. [🤖 IA (Gemini)](#-ia-gemini-assistant_aipy)
10. [🎙️ Enregistrement & Réunions en direct](#️-enregistrement--réunions-en-direct-assistant_recorderpy)

---

## 📂 Drive (`assistant_drive.py`)
- **`search <query>`** : Recherche des fichiers dans votre Drive (tableau coloré avec Nom, Type, ID, Lien).
- **`download <file_id>`** : Télécharge un fichier classique depuis le Cloud vers votre ordinateur.
- **`upload <file_path>`** : Envoie un fichier de votre ordinateur vers votre Google Drive.
- **`share <file_id> --email <email> --role [reader|writer|commenter]`** : Partage un fichier en privé avec un collaborateur spécifique.
- **`empty_trash`** : Vide complètement la corbeille de votre Google Drive.
- **`restore_version <id> <revision_id>`** : Restaure une ancienne version spécifique d'un fichier.
- **`create_folder <title> [--parent <parent_id>]`** : Crée de nouveaux dossiers.
- **`list_folder <folder_id>`** : Affiche le contenu d'un dossier (avec nom, type, taille et ID) dans un tableau.


## 📄 Docs (`assistant_docs.py`)
- **`extract_structure <id>`** : Extrait et affiche la structure (titres, sous-titres) d'un document.
- **`list_comments <id>`** : Liste tous les commentaires laissés sur un document.
- **`format_bold <id> <text>`** : Met en gras toutes les occurrences d'un texte spécifique dans un document.
- **`insert_image <id> <url>`** : Insère une image (depuis une URL) dans le document.
- **`replace_text <id> <old_text> <new_text>`** : Remplace du texte (fonctionnalité Chercher/Remplacer).
- **`export_pdf <id> <output_filename>`** : Exporte le document en format PDF.
- **`read <id>`** : Affiche le texte brut du document dans le terminal.
- **`export_docx <id> <output_filename>`** : Exporte le document au format Word (.docx).
- **`append_text <id> <text>`** : Ajoute un nouveau paragraphe ou section à la fin d'un document.
- **`create_from_template <template_id> <title> <variables_json>`** : Crée un document depuis un modèle avec variables.


## 📊 Sheets (`assistant_sheets.py`)
- **`add_sheet <id> <title>`** : Ajoute un nouvel onglet au tableur.
- **`format_green <id> <cell_range>`** : Colore le fond d'une plage de cellules en vert.
- **`add_formula <id> <cell_range> <formula>`** : Insère une formule de calcul.
- **`read_range <id> <range_name>`** : Lit et affiche le contenu d'une plage (ex: "A1:C10").
- **`add_chart <id> <tab_id>`** : Insère un graphique basique.
- **`add_filter <id> <tab_id>`** : Active les filtres sur la feuille.
- **`export_pdf <id> <tab_id> <filename>`** : Exporte un onglet spécifique en PDF.


## 🖼️ Slides (`assistant_slides.py`)
- **`create_presentation <title>`** : Crée une nouvelle présentation vierge.
- **`clone_slide <presentation_id> <slide_id>`** : Duplique une diapositive existante.
- **`replace_variables <presentation_id> <variable> <valeur>`** : Cherche et remplace un texte (ex: "{{NOM}}").
- **`export_slide <presentation_id> <slide_id> <output_filename>`** : Exporte une seule slide en image.
- **`export_pdf <presentation_id> <output_filename>`** : Exporte toute la présentation au format PDF.
- **`insert_textbox <presentation_id> <page_id> <text>`** : Ajoute une zone de texte.
- **`insert_table <presentation_id> <page_id> <rows> <cols>`** : Insère un tableau avec les dimensions données.
- **`mass_generate <id> <slide_id> <csv_path>`** : Génère des slides en masse depuis un fichier CSV.


## 📅 Calendar (`assistant_calendar.py`)
- **`list_events [--max <n>]`** : Affiche les prochains événements.
- **`create_event <summary> <start_time> <end_time> [--emails] [--timezone]`** : Planifie une réunion.
- **`delete_event <event_id>`** : Annule et supprime un événement.
- **`add_reminder <event_id> <minutes>`** : Ajoute une alerte/notification.
- **`rsvp <event_id> <response>`** : Répond à une invitation (accepted, declined, tentative).


## ✅ Tasks (`assistant_tasks.py`)
- **`create_list <title>`** : Crée une nouvelle liste de tâches avec le titre spécifié.
- **`clear_completed <list_id>`** : Supprime définitivement toutes les tâches terminées d'une liste spécifique.
- **`add_task <list_id> <title> [--parent] [--due <date>]`** : Ajoute une nouvelle tâche avec une date d'échéance optionnelle (format: `YYYY-MM-DDT00:00:00.000Z`).
- **`complete_task <list_id> <task_id>`** : Coche une tâche spécifique comme terminée.
- **`list_pending <list_id>`** : Liste toutes les tâches non complétées d'une liste (tableau coloré avec Statut, Titre, ID).

## 📝 Forms (`assistant_forms.py`)
- **`create <title>`** : Crée un nouveau Google Form avec le titre spécifié.
- **`get_responses <form_id>`** : Récupère et affiche toutes les réponses soumises à un formulaire.
- **`add_question <form_id> <question_title> [--type]`** : Ajoute dynamiquement des questions (type par défaut : TEXT, options : RADIO, CHECKBOX...).
- **`export_responses <form_id> <output_csv>`** : Exporte les réponses directement dans un fichier CSV local.
- **`close_form <form_id>`** : Ferme le formulaire (ne plus accepter de réponses).
- **`add_image <form_id> <image_url>`** : Ajoute une image de présentation (ImageItem) au formulaire.
- **`add_conditional_question <form_id> <question_title> <json_config>`** : Ajoute une question conditionnelle redirigeant vers des sections spécifiques selon les choix.

## 🧠 Notebook (Google Colab / Gemini) (`assistant_notebook.py`)
- **`create <title>`** : Crée un nouveau fichier vierge Google Colab dans votre Google Drive.
- **`list`** : Liste tous les fichiers Google Colab (Gemini Notebooks) existants sur votre Google Drive.

## 🤖 IA Gemini (`assistant_ai.py`)
> Nécessite une clé API Gemini valide dans le fichier `.env` : `GEMINI_API_KEY=...`

- **`parse_event <prompt>`** : Analyse du texte naturel pour créer un événement Calendar.
- **`summarize <doc_id>`** : Demande à Gemini de lire un Doc et d'en faire un résumé structuré.
- **`ask_sheet <sheet_id> <question>`** : Pose une question en français sur les données d'un Sheets.
- **`proofread <doc_id>`** : Corrige les fautes et la syntaxe d'un document.
- **`generate_slides <topic> [--num_slides <n>]`** : Génère une présentation complète avec Titre, Contenu et Conclusion.
- **`generate_doc <doc_id> <prompt>`** : Demande à Gemini de rédiger un texte et l'injecte à la fin du document.
- **`classify_sheet <sheet_id> <read_range> <write_range> <categories>`** : Analyse des données et écrit des étiquettes (labels) automatiquement.
- **`estimate_cost <doc_id>`** : Calcule le nombre de tokens d'un document et estime le coût d'analyse sans rien dépenser.
- **`stats`** : Affiche un tableau de bord récapitulatif des requêtes IA effectuées, des tokens consommés et du coût total.
- **`meeting_audio <audio_file> [--title <titre>] [--format both|word|docs]`** : Analyse un fichier audio de réunion (.wav, .mp3, .m4a), génère la transcription intégrale, crée le compte-rendu (Google Docs et/ou Word .docx) et ajoute les tâches dans Google Tasks.

## 🎙️ Enregistrement & Réunions en direct (`assistant_recorder.py`)
- **`record live [--title <titre>] [--format both|word|docs]`** : Enregistre la réunion en direct (micro/audio). Appuyez sur [Entrée] pour stopper et générer automatiquement le document avec transcription intégrale (Google Docs + Word local .docx) et les tâches Google Tasks.
- **`record start [--title <titre>]`** : Démarre un enregistrement silencieux en tâche de fond.
- **`record stop [--format both|word|docs]`** : Arrête l'enregistrement en tâche de fond et déclenche la synthèse Gemini + transcription intégrale + Docs / Word + Tasks.
- **`record process <audio_file> [--title <titre>] [--format both|word|docs]`** : Traite un enregistrement existant (.wav, .mp3, .m4a).
