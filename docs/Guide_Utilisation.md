# Guide Complet d'Utilisation : Assistant Google Workspace & Gemini Hub

Bienvenue dans le guide détaillé de votre Assistant Google Workspace. Ce document vous expliquera comment fonctionne le projet, comment l'utiliser au quotidien (en ligne de commande ou via son API centralisée), quelles sont les différences entre les différentes commandes, et comment maîtriser votre budget d'Intelligence Artificielle.

---

## 📑 Sommaire

1. [Comment fonctionne ce projet ?](#1-comment-fonctionne-ce-projet-)
2. [Actions Classiques (100% Gratuites / 0 Token)](#2-actions-classiques-100-gratuites--0-token)
3. [Les Super-Pouvoirs de l'IA Gemini (Génération & Analyse)](#3-les-super-pouvoirs-de-lia-gemini-génération--analyse)
4. [🎙️ Enregistrement Audio, Réunions & Transcription (Word / Docs)](#4-️-enregistrement-audio-réunions--transcription-word--docs)
5. [Gérer et Surveiller son Budget IA (Tokens)](#5-gérer-et-surveiller-son-budget-ia-tokens)
6. [Modes d'accès : CLI & API REST Centralisée](#6-modes-daccès--cli--api-rest-centralisée)

---

## 1. Comment fonctionne ce projet ?

Ce projet est conçu pour être à la fois un **assistant CLI local** et une **API REST centralisée**. Il se connecte de façon sécurisée à votre compte Google Workspace et aux modèles de langage Gemini.

Il possède **deux moteurs bien distincts** :

* **Le moteur "API Google" (Les bras) :** Il s'authentifie avec le fichier `config/credentials.json` (et le jeton `config/token.json`) pour lire, écrire et créer des documents sur votre Drive, Docs, Sheets, Calendar, Tasks, etc. Ces actions sont **100% gratuites et illimitées**.
* **Le moteur "Gemini AI" (Le cerveau) :** Il s'authentifie avec la clé `GEMINI_API_KEY` stockée dans le fichier `.env`. Il utilise les modèles **Gemini 3.7 / 3.5 Flash** pour "réfléchir" (résumer un texte, rédiger un contenu, analyser un tableau, transcrire et synthétiser un enregistrement audio). Ce moteur consomme des **Tokens** (suivis dans `data/usage_history.json`).

---

## 2. Actions Classiques (100% Gratuites / 0 Token)

Ces commandes sont instantanées, ne nécessitent pas la clé API Gemini et ne coûtent rien. Elles sont idéales pour l'automatisation pure (manipulation de fichiers, transferts, formatage).

### Exemples de commandes que vous pouvez exécuter sans rien dépenser

* **Manipuler le Drive**

  ```powershell
  # Créer un dossier
  .\scripts\gassist.bat drive create_folder "Dossier Client"

  # Uploader un fichier
  .\scripts\gassist.bat drive upload "C:\rapport.pdf"
  ```

* **Travailler sur Docs**

  ```powershell
  # Ajouter un paragraphe à la fin d'un document
  .\scripts\gassist.bat docs append_text "ID_DU_DOC" "Fait à Paris, le 10 Septembre."

  # Créer un document depuis un modèle avec variables JSON
  .\scripts\gassist.bat docs create_from_template "ID_MODELE" "Contrat Jean" '{"NOM": "Jean"}'

  # Exporter en fichier Word (.docx)
  .\scripts\gassist.bat docs export_docx "ID_DU_DOC" "contrat.docx"
  ```

* **Travailler sur Sheets**

  ```powershell
  # Mettre une ligne en vert
  .\scripts\gassist.bat sheets format_green "ID_SHEET" "A1:E1"

  # Insérer une formule
  .\scripts\gassist.bat sheets add_formula "ID_SHEET" "B2" "=SUM(A1:A10)"
  ```

* **Gérer son Calendrier**

  ```powershell
  # Lister les 5 prochaines réunions
  .\scripts\gassist.bat calendar list_events --max 5
  ```

* **Générer des PDF (Slides & Docs)**

  ```powershell
  .\scripts\gassist.bat slides export_pdf "ID_PRES" "ma_presentation.pdf"
  ```

---

## 3. Les Super-Pouvoirs de l'IA Gemini (Génération & Analyse)

Ces commandes font appel à l'Intelligence Artificielle **Gemini 3.7 / 3.5 Flash**. Vous pouvez les identifier car elles commencent par `.\scripts\gassist.bat ai ...`.

### Ce que l'IA peut faire pour vous

* **Rédiger et Injecter du contenu (`generate_doc`)** : Demandez à l'IA d'écrire un article de blog, un mail ou une conclusion, et elle l'insérera directement à la fin de votre Google Docs.

  ```powershell
  .\scripts\gassist.bat ai generate_doc "ID_DOC" "Rédige une conclusion optimiste de 3 lignes"
  ```

* **Créer des présentations de A à Z (`generate_slides`)** : L'IA planifie le contenu, crée les titres, rédige les *bullet points*, et génère un Google Slides complet (incluant une intro et une conclusion automatiques).

  ```powershell
  .\scripts\gassist.bat ai generate_slides "Le futur du télétravail" --num_slides 6
  ```

* **Classifier des données Intelligemment (`classify_sheet`)** : Marre de trier à la main ? L'IA lit une colonne de votre Sheets et attribue des étiquettes (ex: Urgent/Normal/Ignorer) dans une autre colonne.

  ```powershell
  .\scripts\gassist.bat ai classify_sheet "ID_SHEET" "A1:A20" "B1:B20" "Urgent, Normal, Ignorer"
  ```

* **Discuter avec vos données (`ask_sheet`, `summarize`, `proofread`)** : L'IA lit vos fichiers pour répondre à des questions sur un tableau de données, résumer un document de 50 pages, ou corriger vos fautes d'orthographe.

---

## 4. 🎙️ Enregistrement Audio, Réunions & Transcription (Word / Docs)

Ce module (`record`) vous permet d'enregistrer une réunion, un cours ou un mémo vocal, puis de laisser **Gemini** tout analyser, transcrire et exporter automatiquement.

### A. Enregistrement en Direct (`record live`)

Vous lancez l'enregistrement, assistez à votre réunion, et appuyez simplement sur **[ENTRÉE]** dans le terminal lorsque c'est terminé :

```powershell
# Enregistrement direct (Génère par défaut un Google Doc + un fichier Word .docx local)
.\scripts\gassist.bat record live --title "Point Equipe Q4"
```

### B. Traitement d'un Fichier Audio Existant (`record process`)

Si vous avez déjà un enregistrement audio sur votre PC (`.wav`, `.mp3`, `.m4a`) :

```powershell
.\scripts\gassist.bat record process "audio.wav" --title "Synthèse Réunion"
```

### C. Ce que le document final contient

Le document généré (accessible en ligne sur Google Docs et sauvegardé en local au format `.docx`) contient automatiquement :

1. **📌 Résumé Exécutif** : Vue synthétique en 3 à 5 phrases.
2. **💡 Points Clés & Débats** : Tous les concepts et notions abordées.
3. **✔ Décisions Actées** : Les conclusions fermes prises.
4. **☑ Plan d'Actions & Tâches** : Tâches précises avec responsables et dates d'échéances (synchronisables dans Google Tasks).
5. **📝 Transcription Intégrale de la Discussion** : Retranscription intégrale et chronologique de l'ensemble des échanges.

---

## 5. Gérer et Surveiller son Budget IA (Tokens)

Puisque les actions IA nécessitent une réflexion, l'API Gemini comptabilise cet effort en **Tokens** (environ 1 token = 1 mot ou morceau de mot).

### A. Estimer avant d'agir (Dry-Run)

Avant de lancer un résumé sur un document qui vous semble très long, utilisez la commande d'estimation (100% gratuite) :

```powershell
.\scripts\gassist.bat ai estimate_cost "ID_DU_DOC"
```

### B. Le reçu de consommation

Chaque action IA affiche un encadré récapitulatif :
```text
╭───────── 📊 Consommation ─────────╮
│ • Coût de l'action    : 420 tokens (Entrée: 320, Sortie: 100) │
│ • Budget restant      : 999 580 tokens (sur 1000000)          │
╰───────────────────────────────────╯
```

### C. Le Tableau de Bord

Pour consulter votre historique complet stocké dans `data/usage_history.json` :

```powershell
.\scripts\gassist.bat ai stats
```

---

## 6. Modes d'accès : CLI & API REST Centralisée

Pour rappel, vous pouvez utiliser ce projet selon vos besoins :
* **En ligne de commande locale** : via `.\scripts\gassist.bat <service> <action>` ou `python -m src.google_assistant`.
* **En API REST pour d'autres projets** : démarrez le serveur avec `docker compose up -d` ou `.\scripts\start_api.bat`, puis consultez la documentation interactive sur [http://localhost:8000/docs](http://localhost:8000/docs).
