# 📂 Sommaire du Dossier `google cloud`

Ce dossier contient l'ensemble des scripts composant l'**Assistant Ultime Google Workspace**. L'architecture a été modularisée pour séparer la logique de chaque service Google dans des fichiers distincts.

## 📑 Table des Matières

1. [🚀 Le Fichier Principal (À exécuter)](#-le-fichier-principal-à-exécuter)
2. [📦 Dépendances & Configuration](#-dépendances--configuration)
3. [🔐 Authentification & Sécurité](#-authentification--sécurité)
4. [🧩 Les Sous-Modules (`services/`)](#-les-sous-modules-services)
5. [📚 Documentation (`docs/`)](#-documentation-docs)
6. [⚙️ Fichiers Générés Automatiquement](#️-fichiers-générés-automatiquement)

---

## 🚀 Le Fichier Principal (À exécuter)

* **`google_assistant.py`** : 
  C'est le chef d'orchestre. C'est l'**unique fichier** que vous devez appeler depuis le terminal. Il analyse votre commande (ex: `python google_assistant.py drive search "Projet"`) et se charge d'appeler les bons modules ci-dessous.

---

## 📦 Dépendances & Configuration

* **`requirements.txt`** :
  Contient la liste des bibliothèques Python nécessaires pour faire fonctionner le projet. À installer avec `pip install -r requirements.txt`.

---

## 🔐 Authentification & Sécurité

* **`auth.py`** :
  Gère l'authentification OAuth2. Ce fichier va lire `credentials.json`, ouvrir le navigateur pour vous demander l'autorisation, et générer le "passeport" (`token.json`) avec les accès à tous les services (Drive, Docs, Forms, etc.).
* **`credentials.json`** *(Fichier secret de Google Cloud)* :
  Contient vos identifiants d'API Google Cloud. À ne jamais partager.
* **`token.json`** *(Généré automatiquement)* :
  Votre "passeport" qui prouve que vous avez accordé les permissions au script. S'il y a une erreur de droits (`403`), il suffit de supprimer ce fichier pour forcer une nouvelle demande.

---

## 🧩 Les Sous-Modules (`services/`)

Ces fichiers sont rangés dans le dossier `services/` et importés automatiquement par `google_assistant.py`. Ils contiennent les fonctions spécifiques à chaque application Google :

* **`assistant_drive.py`** :
  Gère les fichiers globaux (Recherche, création de dossiers de partage public, corbeille, création de dossiers, restauration de versions).
* **`assistant_docs.py`** :
  Pilote Google Docs (Récupérer les titres d'un chapitre, mettre du texte en gras, remplacer du texte, exporter en PDF, lister les commentaires, insérer des images).
* **`assistant_sheets.py`** :
  Pilote Google Sheets (Ajouter de nouveaux onglets, colorier des cellules, lire des plages, ajouter des graphiques ou des filtres, insérer des formules de calcul).
* **`assistant_slides.py`** :
  Pilote Google Slides (Créer des présentations, insérer des zones de texte, cloner des diapositives, remplacer les variables textuelles comme `{{NOM}}`, exporter en image).
* **`assistant_calendar.py`** :
  Pilote l'Agenda (Créer et supprimer des événements, lister les prochains événements, ajouter des rappels pop-up, répondre aux invitations).
* **`assistant_tasks.py`** :
  Pilote Google Tasks (Créer des listes de tâches, ajouter, lister et effacer les tâches terminées).
* **`assistant_forms.py`** :
  Pilote Google Forms (Créer des formulaires de bêta-lecture, ajouter des questions, récupérer et exporter les réponses, fermer les formulaires).
* **`assistant_notebook.py`** :
  Gère les notebooks Google Colab (Gemini Notebooks) en interagissant avec votre Google Drive. Permet de lister tous vos carnets existants et d'en créer de nouveaux directement depuis le terminal.
* **`assistant_ai.py`** :
  Intègre l'Intelligence Artificielle **Gemini 3.6 Flash** (résumés de documents, rédaction assistée, questions/réponses sur tableurs, correction orthographique, génération de présentations Slides, classification automatique, estimation des coûts et suivi des quotas de tokens).
* **`assistant_recorder.py`** :
  Gère la capture audio directe (microphone) ou en arrière-plan (16 kHz mono) avec arrêt interactif pour l'analyse de réunions, cours et mémos vocaux.

---

## 📚 Documentation (`docs/`)

Le dossier `docs/` centralise toute la documentation du projet :
* **`Sommaire_Google_Cloud.md`** : Ce fichier même (l'architecture du projet et rôle des fichiers).
* **`Guide_Utilisation.md`** : Guide pas-à-pas de prise en main de l'outil CLI (actions gratuites, IA, enregistrement audio et gestion des budgets).
* **`Sommaire fonction.md`** : La liste complète et rapide de toutes les commandes CLI disponibles.
* **`Relation_VM_GCP.md`** : Guide complet du déploiement, de l'architecture et de l'automatisation 24/7 sur la Machine Virtuelle Google Cloud (Compute Engine).
* **`Historique/`** : Dossier d'historique et de versions.
  * **`Historique_Fonctionnalites.md`** : Répertoire exhaustif de toutes les évolutions (v1.0 à v1.5), détails techniques, configuration IA et formats d'export (Word & Docs).

---

## ⚙️ Fichiers Générés Automatiquement & Données Locales

* **`recordings/`** :
  Dossier local contenant les enregistrements audio bruts (`.wav`) ainsi que les comptes-rendus et transcriptions intégrales exportés au format **Microsoft Word (`.docx`)**.
* **`usage_history.json`** :
  Fichier local de persistance du journal de consommation des tokens IA (tokens d'entrée, de sortie et nombre de requêtes).
* **`.recording_state.json`** :
  Fichier temporaire conservant le PID et le titre d'un enregistrement audio lancé en arrière-plan (`record start`).
* **`.gitignore`** :
  Fichier de configuration Git indiquant les fichiers et dossiers à ne jamais publier (ex: secrets, tokens, environnements virtuels, recordings).
* **`__pycache__/`** :
  Dossier créé automatiquement par Python contenant le bytecode compilé (`.pyc`) pour accélérer l'exécution.
