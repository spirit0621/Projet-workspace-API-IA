# ☁️ Architecture & Relation avec la Machine Virtuelle (VM GCP)

Ce document détaille le rôle, l'architecture et les procédures d'utilisation de la Machine Virtuelle **Google Cloud Compute Engine** pour faire fonctionner l'**Assistant Ultime Google Workspace** en continu (24h/24, 7j/7).

---

## 📑 Table des Matières

1. [🎯 Pourquoi utiliser une VM Google Cloud ?](#-pourquoi-utiliser-une-vm-google-cloud-)
2. [📋 Fiche Technique de l'Instance](#-fiche-technique-de-linstance)
3. [🏗️ Architecture : PC Local vs VM Distante](#️-architecture--pc-local-vs-vm-distante)
4. [🔐 Le Secret de l'Authentification (Headless & Token)](#-le-secret-de-lauthentification-headless--token)
5. [🔄 Synchronisation des Fichiers (PC ➔ VM)](#-synchronisation-des-fichiers-pc--vm)
6. [🚀 Mise en Service sur la VM (Pas à pas)](#-mise-en-service-sur-la-vm-pas-à-pas)
7. [⏰ Automatisation 24/7 avec Crontab](#-automatisation-247-avec-crontab)
8. [🛡️ Bonnes Pratiques & Gratuité (Free Tier)](#️-bonnes-pratiques--gratuité-free-tier)

---

## 🎯 Pourquoi utiliser une VM Google Cloud ?

Lorsque vous exécutez `gassist` ou `google_assistant.py` sur votre ordinateur personnel :
- Dès que vous éteignez votre PC, mettez en veille ou coupez la connexion Wi-Fi, les scripts s'arrêtent.
- Vous ne pouvez pas planifier d'automatisations nocturnes ou indépendantes.

En déployant votre projet sur une **Machine Virtuelle Compute Engine** :
- **Exécution 24/7** : Le serveur reste allumé en permanence dans le Cloud de Google.
- **Automatisation Totale** : Vos tâches (rapports quotidiens, synchronisation Drive, vérification d'agenda, tâches Gemini) s'exécutent automatiquement à heures fixes.
- **Ultra-rapide** : La VM se trouve sur le réseau interne de Google, ce qui rend les appels aux APIs Google Workspace (Drive, Sheets, Docs...) quasi-instantanés.

---

## 📋 Fiche Technique de l'Instance

| Paramètre | Valeur |
| :--- | :--- |
| **Nom de l'instance** | `victor-automatisation-04092026` |
| **Projet GCP** | `gen-lang-client-0497141502` |
| **Zone** | `us-central1-a` |
| **Type de machine** | `e2-micro` (2 vCPU partagés, 1 Go RAM) |
| **Système d'exploitation** | Debian GNU/Linux 13 (Trixie) x86_64 |
| **Éligibilité Free Tier** | ✅ Oui (1 instance `e2-micro` gratuite par mois sur us-central1) |
| **Dossier du projet sur la VM** | `/home/alves/google-assistant/` |

---

## 🏗️ Architecture : PC Local vs VM Distante

```
 ┌─────────────────────────────────────────────────────────────┐
 │                      VOTRE PC LOCAL                         │
 │                                                             │
 │  • Écriture et test du code (Python, VS Code)               │
 │  • Première connexion OAuth2 avec navigateur graphique     │
 │  • Génère : credentials.json, token.json, .env              │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                │ 📡 gcloud compute scp
                                │    (Transfert sécurisé du code & des jetons)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │            VM GOOGLE CLOUD (Compute Engine)                 │
 │            victor-automatisation-04092026                   │
 │                                                             │
 │  • Tourne 24h/24 dans le datacenter us-central1             │
 │  • Utilise token.json existant (sans besoin d'écran)        │
 │  • Planificateur cron / systemd (ex: tous les matins à 8h)   │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                │ ⚡ Connexion interne ultra-rapide
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │              SERVICES GOOGLE WORKSPACE & IA                 │
 │   Google Drive • Docs • Sheets • Calendar • Tasks • Gemini  │
 └─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Le Secret de l'Authentification (Headless & Token)

Un serveur Cloud Linux n'a **pas d'interface graphique ni de navigateur web** (*mode headless*). Si vous essayez de lancer l'authentification OAuth2 directement sur la VM, Google tentera d'ouvrir un navigateur qui n'existe pas.

### La solution mise en place :
1. Vous vous authentifiez **une seule fois** sur votre PC local (`python google_assistant.py ...`).
2. Le fichier **`token.json`** est créé localement : il contient le jeton d'accès et le **refresh_token**.
3. Vous copiez `token.json` sur la VM.
4. La bibliothèque Google sur la VM utilise ce `refresh_token` pour renouveler automatiquement les accès en tâche de fond, **sans jamais avoir besoin d'ouvrir de navigateur**.

---

## 🔄 Synchronisation des Fichiers (PC ➔ VM)

Lorsque vous modifiez du code ou que vous ajoutez de nouveaux services, synchronisez vos fichiers depuis PowerShell sur votre PC :

```powershell
# Commande pour envoyer le projet complet vers la VM
gcloud compute scp --recurse google_assistant.py requirements.txt auth.py token.json credentials.json .env services docs victor-automatisation-04092026:/home/alves/google-assistant/ --zone=us-central1-a --project=gen-lang-client-0497141502
```

> [!TIP]
> Pensez à inclure votre fichier `.env` (contenant votre clé `GEMINI_API_KEY`) si vous utilisez les fonctionnalités d'intelligence artificielle sur la VM.

---

## 🚀 Mise en Service sur la VM (Pas à pas)

### 1. Se connecter en SSH à la VM
```powershell
gcloud compute ssh victor-automatisation-04092026 --zone=us-central1-a --project=gen-lang-client-0497141502
```

### 2. Installer Python et les outils système
Une fois dans la console Linux (`alves@victor-automatisation-04092026:~$`) :
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

### 3. Configurer l'environnement virtuel du projet
```bash
cd /home/alves/google-assistant/

# Création de l'environnement virtuel
python3 -m venv .venv

# Activation
source .venv/bin/activate

# Installation des dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Tester l'Assistant sur la VM
```bash
# Vérifier l'accès Drive
python3 google_assistant.py drive list

# Vérifier les statistiques IA
python3 google_assistant.py ai stats
```

---

## ⏰ Automatisation 24/7 avec Crontab

Le grand avantage de la VM est le planificateur de tâches Linux (`cron`).

Pour éditer la planification :
```bash
crontab -e
```

### Exemples de tâches programmées :

```bash
# 1. Tous les matins à 08h00 : Afficher les événements du calendrier du jour dans un log
0 8 * * * /home/alves/google-assistant/.venv/bin/python3 /home/alves/google-assistant/google_assistant.py calendar list >> /home/alves/google-assistant/calendar_daily.log 2>&1

# 2. Tous les lundis à 09h00 : Générer un rapport ou synchroniser des données
0 9 * * 1 cd /home/alves/google-assistant && .venv/bin/python3 mon_script_auto.py >> automation.log 2>&1

# 3. Toutes les 6 heures : Exécuter une tâche d'arrière-plan
0 */6 * * * /home/alves/google-assistant/.venv/bin/python3 /home/alves/google-assistant/google_assistant.py ai stats >> /home/alves/google-assistant/stats.log 2>&1
```

---

## 🛡️ Bonnes Pratiques & Gratuité (Free Tier)

1. **Règles du Free Tier Google Cloud** :
   - L'instance `e2-micro` dans `us-central1` est **gratuite** dans la limite d'1 instance active par mois.
   - Conservez le disque de démarrage à 30 Go ou moins (disque standard persistant).
   - Le trafic sortant vers l'Europe/Internet est inclus jusqu'à 1 Go / mois (très largement suffisant pour des appels API texte/JSON).
2. **Sauvegardes & Sécurité** :
   - Ne publiez jamais `token.json`, `credentials.json` ou `.env` sur un dépôt GitHub public.
   - Votre code reste sauvegardé localement sur votre PC, la VM ne sert que d'exécuteur.
