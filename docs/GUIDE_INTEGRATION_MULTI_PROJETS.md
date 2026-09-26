# Guide d'Intégration Multi-Projets : Google Workspace & Gemini Hub

Ce guide vous explique comment utiliser ce projet centralisé depuis **n'importe lequel de vos autres projets** (React, Next.js, Vue, Node.js, Python, PHP, scripts, etc.) sans jamais avoir à copier ni dupliquer le code.

---

## 1. Démarrer le Hub Centralisé

Vous avez deux méthodes pour faire tourner le service sur votre machine :

### Méthode A : Avec Docker (Recommandé)

Le serveur s'exécute dans un conteneur isolé en tâche de fond. Vos jetons et clés sont montés automatiquement depuis votre machine hôte.

```bash
# Dans le dossier de ce projet :
docker compose up -d
```

- Pour voir les logs en temps réel : `docker compose logs -f`
- Pour arrêter le service : `docker compose down`

### Méthode B : Directement en Python (Local)

Si vous ne souhaitez pas utiliser Docker :

```bash
# Dans le dossier de ce projet avec votre venv actif :
uvicorn src.server:app --reload --port 8000
# Ou directement via le lanceur Windows :
.\start_api.bat
```

---

## 2. Tester et Explorer : Documentation Interactive (Swagger)

Une fois le serveur lancé, ouvrez votre navigateur sur :
👉 [http://localhost:8000/docs](http://localhost:8000/docs)

Vous y trouverez :

- L'interface **Swagger UI** avec la liste exhaustive de toutes les routes classées par service (Drive, Calendar, Docs, Sheets, Slides, Tasks, Forms, AI).
- La possibilité d'exécuter des tests directement dans l'interface en cliquant sur **"Try it out"**.
- Les schémas JSON attendus pour chaque requête.

Pour tester rapidement la santé de l'API :

```bash
curl http://localhost:8000/health
```

Réponse attendue :

```json
{
  "status": "ok",
  "service": "Google Workspace & Gemini Hub API",
  "google_auth_ready": true,
  "gemini_api_key_configured": true
}
```

---

## 3. Appeler le Hub depuis vos Nouveaux Projets

### A. Depuis un projet Web / Frontend (React, Vue, Next.js, Node.js)

Vous n'avez besoin d'installer **aucune dépendance Google ni Gemini** dans votre nouveau projet. Un simple `fetch` ou `axios` suffit.

```javascript
// Exemple 1 : Poser une question à Gemini sur un Google Sheet
async function interrogerSheet(sheetId, question) {
  const response = await fetch("http://localhost:8000/api/ai/ask-sheet", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sheet_id: sheetId,
      question: question
    })
  });
  const data = await response.json();
  console.log("Réponse IA :", data.answer);
}

// Exemple 2 : Créer un événement Google Calendar en langage naturel
async function creerEvenementNaturel(phrase) {
  const response = await fetch("http://localhost:8000/api/ai/parse-event", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: phrase })
  });
  const result = await response.json();
  console.log("Événement créé :", result);
}

// Exemple 3 : Rechercher des fichiers Drive
async function chercherDrive(nom) {
  const res = await fetch(`http://localhost:8000/api/drive/search?query=${encodeURIComponent(nom)}`);
  const data = await res.json();
  return data.files;
}
```

---

### B. Depuis un autre projet Python (via l'API REST)

Dans votre nouveau projet Python, vous n'avez besoin que de `requests` ou `httpx` :

```python
import requests

HUB_URL = "http://localhost:8000"

# 1. Obtenir les 5 prochains événements Calendar
events = requests.get(f"{HUB_URL}/api/calendar/events", params={"max_results": 5}).json()
print("Prochains événements :", events["events"])

# 2. Résumer un Google Doc avec Gemini
summary = requests.post(
    f"{HUB_URL}/api/ai/summarize-doc",
    json={"doc_id": "VOTRE_DOC_ID"}
).json()
print("Résumé :", summary["summary"])

# 3. Ajouter une tâche dans Google Tasks
requests.post(
    f"{HUB_URL}/api/tasks/VOTRE_LIST_ID/tasks",
    json={"title": "Préparer la réunion de projet", "due": "2026-09-30"}
)
```

---

### C. Depuis un projet 100% Python (Import de Module Local sans serveur)

Si vous développez un autre projet Python et préférez importer directement les fonctions Python sans passer par HTTP :

Dans votre nouveau projet (dans son propre venv) :

```bash
pip install -e "c:\Users\alves\Desktop\Projet Perso\Projet API,IA,workspace"
```

Ensuite, dans votre code :

```python
from src import auth
from src.services import assistant_calendar, assistant_drive, assistant_ai

creds = auth.get_credentials()

# Utilisation directe
files = assistant_drive.search_files(creds, "Rapport")
events = assistant_calendar.list_events(creds, max_results=5)
```

---

### D. En Ligne de Commande / Bash / PowerShell (cURL)

Idéal pour automatiser des scripts système ou des webhooks :

```bash
# Résumé d'un document
curl -X POST "http://localhost:8000/api/ai/summarize-doc" \
     -H "Content-Type: application/json" \
     -d '{"doc_id": "VOTRE_DOC_ID"}'

# Vider la corbeille Drive
curl -X POST "http://localhost:8000/api/drive/empty-trash"

# Statistiques de tokens Gemini
curl "http://localhost:8000/api/ai/stats"
```

---

## 4. Tableau Récapitulatif des Endpoints Clés

| Service | Méthode | Route | Description |
| :--- | :--- | :--- | :--- |
| **Santé** | `GET` | `/health` | Statut du hub, présence des jetons Google & Gemini |
| **Drive** | `GET` | `/api/drive/search?query=...` | Recherche de fichiers |
| **Drive** | `POST` | `/api/drive/create-folder` | Créer un dossier |
| **Drive** | `POST` | `/api/drive/upload` | Téléverser un fichier multipart |
| **Drive** | `POST` | `/api/drive/share` | Partager un fichier par e-mail |
| **Calendar** | `GET` | `/api/calendar/events` | Liste des prochains événements |
| **Calendar** | `POST` | `/api/calendar/events` | Créer un événement planifié |
| **Calendar** | `DELETE` | `/api/calendar/events/{id}` | Supprimer un événement |
| **Docs** | `GET` | `/api/docs/{doc_id}` | Lire le contenu textuel |
| **Docs** | `POST` | `/api/docs/{doc_id}/append` | Ajouter du texte en fin de document |
| **Docs** | `POST` | `/api/docs/{doc_id}/replace` | Remplacer du texte |
| **Docs** | `POST` | `/api/docs/create-from-template` | Générer depuis un modèle |
| **Sheets** | `GET` | `/api/sheets/{id}/range` | Lire les cellules d'une plage |
| **Sheets** | `POST` | `/api/sheets/{id}/formula` | Écrire une formule |
| **Slides** | `POST` | `/api/slides/create` | Créer une présentation |
| **Slides** | `POST` | `/api/slides/{id}/replace-variables` | Remplacer `{{variables}}` |
| **Tasks** | `GET` | `/api/tasks/{list_id}/pending` | Liste des tâches en cours |
| **Tasks** | `POST` | `/api/tasks/{list_id}/tasks` | Ajouter une tâche |
| **Forms** | `POST` | `/api/forms` | Créer un formulaire |
| **Forms** | `GET` | `/api/forms/{id}/responses` | Récupérer les réponses |
| **IA** | `POST` | `/api/ai/ask-sheet` | Analyser un Sheet en langage naturel |
| **IA** | `POST` | `/api/ai/summarize-doc` | Résumer un Google Doc |
| **IA** | `POST` | `/api/ai/parse-event` | Créer un événement depuis une phrase |
| **IA** | `POST` | `/api/ai/generate-slides` | Générer un diaporama complet via Gemini |
| **IA** | `GET` | `/api/ai/stats` | Consulter le budget et consommation de tokens |
| **IA** | `POST` | `/api/ai/meeting-audio` | Générer un compte-rendu Docs depuis un audio |
