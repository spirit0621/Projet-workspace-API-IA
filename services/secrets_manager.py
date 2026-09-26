import os
import json
from typing import Optional, Dict, Any

try:
    from google.cloud import secretmanager
except ImportError:
    secretmanager = None

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gen-lang-client-0497141502")


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
        # Gère le cas où le secret stocké est au format fichier .env (GEMINI_API_KEY=xxx)
        for line in secret.splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                key_val = line.split("GEMINI_API_KEY=", 1)[1].strip().strip('"').strip("'")
                os.environ["GEMINI_API_KEY"] = key_val
                return key_val

        # Sinon le secret est directement la clé brute
        os.environ["GEMINI_API_KEY"] = secret.strip()
        return secret.strip()

    return None


def load_oauth_token_dict() -> Optional[Dict[str, Any]]:
    """
    Charge les informations du token OAuth :
    1. Depuis le fichier local token.json s'il existe.
    2. Sinon depuis Secret Manager (secret 'google-oauth-token').
    """
    if os.path.exists("token.json"):
        try:
            with open("token.json", "r", encoding="utf-8") as f:
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
    if os.path.exists("credentials.json"):
        try:
            with open("credentials.json", "r", encoding="utf-8") as f:
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
    Tente de sauvegarder le token OAuth dans token.json en local (environnement dev).
    Silencieux en cas d'impossibilité d'écriture.
    """
    try:
        with open("token.json", "w", encoding="utf-8") as f:
            json.dump(token_info, f, indent=2)
    except Exception:
        pass
