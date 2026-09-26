# Guide Complet d'Utilisation : Assistant Google Workspace

Bienvenue dans le guide détaillé de votre Assistant Google Workspace. Ce document vous expliquera comment fonctionne le projet, quelles sont les différences entre les différentes commandes, et comment maîtriser votre budget d'Intelligence Artificielle.

---

## 📑 Sommaire

1. [Comment fonctionne ce projet ?](#1-comment-fonctionne-ce-projet-)
2. [Actions Classiques (100% Gratuites / 0 Token)](#2-actions-classiques-100-gratuites--0-token)
3. [Les Super-Pouvoirs de l'IA Gemini (Génération & Analyse)](#3-les-super-pouvoirs-de-lia-gemini-génération--analyse)
4. [🎙️ Enregistrement Audio, Réunions & Transcription (Word / Docs)](#4-️-enregistrement-audio-réunions--transcription-word--docs)
5. [Gérer et Surveiller son Budget IA (Tokens)](#5-gérer-et-surveiller-son-budget-ia-tokens)

---

## 1. Comment fonctionne ce projet ?

Ce projet est un programme exécutable depuis votre terminal Windows (via le raccourci `.\gassist`). Il se connecte à votre compte Google pour automatiser des tâches.

Il possède **deux moteurs bien distincts** :

* **Le moteur "API Google" (Les bras) :** Il s'authentifie avec le fichier `credentials.json` et peut lire, écrire, créer des fichiers sur votre Drive, Docs, Sheets, etc. Ces actions sont **gratuites**.
* **Le moteur "Gemini AI" (Le cerveau) :** Il s'authentifie avec la clé `GEMINI_API_KEY` stockée dans le fichier `.env`. Il utilise le modèle haute performance **Gemini 3.6 Flash** pour "réfléchir" (résumer un texte, écrire un brouillon, analyser un tableau, transcrire et synthétiser un enregistrement audio). Ce moteur consomme des **Tokens**.

---

## 2. Actions Classiques (100% Gratuites / 0 Token)

Ces commandes sont instantanées, ne nécessitent pas la clé API Gemini et ne coûtent rien. Elles sont idéales pour l'automatisation pure (manipulation de fichiers, transferts, formatage).

### Exemples de commandes que vous pouvez écrire sans rien dépenser :

* **Manipuler le Drive :**

  ```bash
  # Créer un dossier
  .\gassist drive create_folder "Dossier Client"

  # Uploader un PDF
  .\gassist drive upload "C:\rapport.pdf"
  ```
* **Travailler sur Docs :**

  ```bash
  # Ajouter un paragraphe à la fin d'un contrat
  .\gassist docs append_text "ID_DU_DOC" "Fait à Paris, le 10 Septembre."

  # Créer un contrat personnalisé à partir d'un modèle (remplace {{NOM}} par "Jean")
  .\gassist docs create_from_template "ID_MODELE" "Contrat Jean" '{"NOM": "Jean"}'

  # Exporter en fichier Word (.docx)
  .\gassist docs export_docx "ID_DU_DOC" "contrat.docx"
  ```
* **Travailler sur Sheets :**

  ```bash
  # Mettre une ligne en vert
  .\gassist sheets format_green "ID_SHEET" "A1:E1"
  ```
* **Gérer son Calendrier :**

  ```bash
  # Lister les 5 prochaines réunions
  .\gassist calendar list_events --max 5
  ```
* **Générer des PDF (Slides & Docs) :**

  ```bash
  .\gassist slides export_pdf "ID_PRES" "ma_presentation.pdf"
  ```

---

## 3. Les Super-Pouvoirs de l'IA Gemini (Génération & Analyse)

Ces commandes font appel à l'Intelligence Artificielle **Gemini 3.6 Flash**. Vous pouvez les identifier car elles commencent par `.\gassist ai ...`.

### Ce que l'IA peut faire pour vous :

* **Rédiger et Injecter du contenu (`generate_doc`)** : Demandez à l'IA d'écrire un article de blog, un mail ou une conclusion, et elle l'insérera directement à la fin de votre Google Docs.

  ```bash
  .\gassist ai generate_doc "ID_DOC" "Rédige une conclusion optimiste de 3 lignes"
  ```
* **Créer des présentations de A à Z (`generate_slides`)** : L'IA planifie le contenu, crée les titres, rédige les *bullet points*, et génère un Google Slides complet (incluant une intro et une conclusion automatiques).

  ```bash
  .\gassist ai generate_slides "Le futur du télétravail" --num_slides 6
  ```
* **Classifier des données Intelligemment (`classify_sheet`)** : Marre de trier à la main ? L'IA lit une colonne de votre Sheets et attribue des étiquettes (ex: Positif/Négatif) dans une autre colonne.

  ```bash
  .\gassist ai classify_sheet "ID_SHEET" "A1:A20" "B1:B20" "Urgent, Normal, Ignorer"
  ```
* **Discuter avec vos données (`ask_sheet`, `summarize`, `proofread`)** : L'IA lit vos fichiers pour répondre à des questions (quel est le meilleur produit de ce tableur ?), pour résumer un long contrat de 50 pages, ou pour corriger vos fautes d'orthographe.

---

## 4. 🎙️ Enregistrement Audio, Réunions & Transcription (Word / Docs)

Ce module (`record`) vous permet d'enregistrer une réunion, un cours ou un mémo vocal, puis de laisser **Gemini 3.6 Flash** tout analyser, transcrire et exporter automatiquement.

### A. Enregistrement en Direct (`record live`)

Vous lancez l'enregistrement, assistez à votre cours ou réunion, et appuyez simplement sur **[ENTRÉE]** dans le terminal lorsque c'est terminé :

```bash
# Enregistrement direct (Génère par défaut un Google Doc + un fichier Word .docx local)
.\gassist record live --title "Cours Programmation Python"

# Forcer uniquement le format Word (.docx) local :
.\gassist record live --title "Point Equipe" --format word

# Forcer uniquement le format Google Docs en ligne :
.\gassist record live --title "Point Equipe" --format docs
```

### B. Enregistrement en Arrière-Plan (`record start` / `record stop`)

Si vous souhaitez enregistrer pendant que vous utilisez votre terminal pour d'autres commandes :

```bash
# Démarre l'enregistrement silencieux
.\gassist record start --title "Reunion Projet"

# Arrête l'enregistrement et déclenche la synthèse + transcription
.\gassist record stop
```

### C. Traitement d'un Fichier Audio Existant (`record process`)

Si vous avez déjà un enregistrement sur votre PC (`.wav`, `.mp3`, `.m4a`) :

```bash
.\gassist record process "recordings\audio.wav" --title "Synthèse Cours"
```

### D. Ce que le document final contient :

À la fin du traitement, le document généré (accessible en ligne via **Google Docs** et sauvegardé en local dans **`recordings/*.docx`**) contient automatiquement :
1. **📌 Résumé Exécutif** : Vue synthétique en 3 à 5 phrases.
2. **💡 Points Clés & Débats** : Tous les concepts, arguments et notions abordées.
3. **✔ Décisions Actées** : Les conclusions fermes prises.
4. **☑ Plan d'Actions & Tâches** : Tâches précises avec responsables et dates d'échéances (automatiquement synchronisées dans **Google Tasks** !).
5. **📝 Transcription Intégrale de la Discussion** : Retranscription intégrale et chronologique de l'ensemble des échanges entre intervenants.

---

## 5. Gérer et Surveiller son Budget IA (Tokens)

Puisque les actions IA nécessitent une réflexion, l'API Google compte cet effort en **Tokens** (environ 1 token = 1 mot ou morceau de mot).
Pour éviter toute mauvaise surprise et utiliser l'IA de manière professionnelle, un système de budget est intégré.

### A. Estimer avant d'agir (Dry-Run)

Avant de lancer un résumé sur un document qui vous semble très long, utilisez la commande d'estimation. **C'est 100% gratuit.**

```bash
.\gassist ai estimate_cost "ID_DU_DOC"
```

*L'assistant lira le document et vous répondra par exemple : "Ce document fait 14 500 tokens. L'analyser coûtera environ 14 500 tokens."*

### B. L'affichage après action

Chaque fois que vous utilisez une commande `ai ...` ou `record ...`, l'assistant vous affiche un reçu à la fin.

```text
╭───────── 📊 Consommation ─────────╮
│ • Coût de l'action    : 420 tokens (Entrée: 320, Sortie: 100) │
│ • Budget restant      : 999 580 tokens (sur 1000000)          │
╰───────────────────────────────────╯
```

*(Le budget par défaut est de 1 000 000 de tokens, ce qui correspond approximativement à un usage modéré mensuel gratuit. Ce chiffre est modifiable dans le code `assistant_ai.py`).*

### C. Le Tableau de Bord

Pour voir votre historique complet et surveiller votre quota global :

```bash
.\gassist ai stats
```

Vous obtiendrez un tableau récapitulant toutes vos requêtes depuis que vous utilisez l'assistant, vous permettant de savoir précisément où vous en êtes dans votre consommation.
