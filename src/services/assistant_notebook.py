from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

COLAB_MIME_TYPE = 'application/vnd.google.colaboratory'

def get_drive_service(creds):
    return build('drive', 'v3', credentials=creds)

def list_colabs(creds):
    service = get_drive_service(creds)
    try:
        query = f"mimeType='{COLAB_MIME_TYPE}' and trashed=false"
        print("Recherche de vos notebooks Google Colab (Gemini Notebooks) dans Drive...")
        results = service.files().list(
            q=query,
            pageSize=50,
            fields="nextPageToken, files(id, name, createdTime)",
            orderBy="createdTime desc"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            print("Aucun notebook Colab trouvé sur votre Drive.")
        else:
            print(f"Trouvé {len(items)} notebook(s) Colab :")
            for item in items:
                print(f"- {item['name']} (ID: {item['id']}) - Créé le: {item.get('createdTime')}")
    except HttpError as error:
        print(f"Erreur API Drive : {error}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

def create_colab(creds, title):
    service = get_drive_service(creds)
    file_metadata = {
        'name': title,
        'mimeType': COLAB_MIME_TYPE
    }
    try:
        print(f"Création d'un nouveau notebook Colab '{title}'...")
        file = service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
        
        print(f"✅ Notebook '{file.get('name')}' créé avec succès !")
        print(f"ID du fichier : {file.get('id')}")
        print(f"Vous pouvez l'ouvrir via : https://colab.research.google.com/drive/{file.get('id')}")
    except HttpError as error:
        print(f"Erreur API Drive : {error}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")
