import os
import json
from typing import Optional, Dict, Any

try:
    from google.cloud import secretmanager
except ImportError:
    secretmanager = None

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gen-lang-client-0497141502")

def _find_file_path(filename: str) -> Optional[str]:
    """Recherche un fichier en local (dossier config/, CWD ou racine du projet)."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(root_dir, "config", filename),
        os.path.join("config", filename),
        filename,
        os.path.join(root_dir, filename),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def get_secret(secret_id: str, version_id: str = "latest") -> Optional[str]:
    """
    Récupère la valeur d'un secret depuis Google Cloud Secret Manager.
    Retourne None si l'API n'est pas installée, non configurée ou en cas d'erreur.
    """
    if secretmanager is None:
        return None
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8").strip()
    except Exception:
        return None

def load_gemini_api_key() -> Optional[str]:
    """
    Charge la clé Gemini API :
    1. Depuis les variables d'environnement actuelles (ex: chargées par .env).
    2. Sinon depuis Google Secret Manager (secret 'gemini-api-key').
    Injecte automatiquement la clé dans os.environ['GEMINI_API_KEY'].
    """
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key.strip()

    secret = get_secret("gemini-api-key")
    if secret:
        for line in secret.splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                key_val = line.split("GEMINI_API_KEY=", 1)[1].strip().strip('"').strip("'")
                os.environ["GEMINI_API_KEY"] = key_val
                return key_val

        os.environ["GEMINI_API_KEY"] = secret.strip()
        return secret.strip()

    return None

def load_oauth_token_dict() -> Optional[Dict[str, Any]]:
    """
    Charge les informations du token OAuth :
    1. Depuis le fichier local token.json s'il existe.
    2. Sinon depuis Secret Manager (secret 'google-oauth-token').
    """
    token_path = _find_file_path("token.json")
    if token_path:
        try:
            with open(token_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    secret_data = get_secret("google-oauth-token")
    if secret_data:
        try:
            return json.loads(secret_data)
        except Exception:
            pass
    return None

def load_oauth_credentials_dict() -> Optional[Dict[str, Any]]:
    """
    Charge la configuration client OAuth :
    1. Depuis le fichier local credentials.json s'il existe.
    2. Sinon depuis Secret Manager (secret 'google-oauth-credentials').
    """
    creds_path = _find_file_path("credentials.json")
    if creds_path:
        try:
            with open(creds_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    secret_data = get_secret("google-oauth-credentials")
    if secret_data:
        try:
            return json.loads(secret_data)
        except Exception:
            pass
    return None

def save_oauth_token_dict(token_info: Dict[str, Any]) -> None:
    """
    Tente de sauvegarder le token OAuth dans config/token.json (ou token.json) en local.
    Silencieux en cas d'impossibilité d'écriture.
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target = _find_file_path("token.json")
    if not target:
        config_dir = os.path.join(root_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        target = os.path.join(config_dir, "token.json")
    try:
        with open(target, "w", encoding="utf-8") as f:
            json.dump(token_info, f, indent=2)
    except Exception:
        pass
