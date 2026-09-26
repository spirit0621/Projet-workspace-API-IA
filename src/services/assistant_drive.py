from googleapiclient.discovery import build
import io
import os
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

def get_service(creds):
    return build('drive', 'v3', credentials=creds)

def search_files(creds, query):
    service = get_service(creds)
    results = service.files().list(
        q=f"name contains '{query}' and trashed=false",
        spaces='drive',
        fields="files(id, name, mimeType, webViewLink)").execute()
    files = results.get('files', [])
    
    if not files:
        print("Aucun fichier trouvé.")
        return []
        
    from rich.console import Console
    from rich.table import Table
    console = Console()
    table = Table(title=f"Résultats de recherche : '{query}'")
    table.add_column("Nom", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("ID", style="green")
    table.add_column("Lien", style="blue")
    
    for f in files:
        table.add_row(f.get('name', ''), f.get('mimeType', ''), f.get('id', ''), f.get('webViewLink', ''))
        
    console.print(table)
    return files

def share(creds, file_id, email, role):
    service = get_service(creds)
    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }
    try:
        service.permissions().create(fileId=file_id, body=permission).execute()
        print(f"Le fichier {file_id} a été partagé avec {email} en tant que '{role}'.")
    except Exception as e:
        print(f"Erreur lors du partage : {e}")

def share_public(creds, file_id):
    service = get_service(creds)
    permission = {'type': 'anyone', 'role': 'reader'}
    service.permissions().create(fileId=file_id, body=permission).execute()
    print(f"Lien de partage public activé pour le fichier {file_id}.")

def restore_version(creds, file_id, revision_id):
    service = get_service(creds)
    print(f"Restauration de la révision {revision_id} du fichier {file_id} (Fonction simulée).")

def empty_trash(creds):
    service = get_service(creds)
    service.files().emptyTrash().execute()
    print("Corbeille vidée avec succès.")

def create_folder(creds, title, parent_id=None):
    service = get_service(creds)
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
        
    try:
        folder = service.files().create(body=file_metadata, fields='id').execute()
        print(f"Dossier '{title}' créé avec succès (ID: {folder.get('id')}).")
        return folder.get('id')
    except Exception as e:
        print(f"Erreur lors de la création du dossier : {e}")

def download_file(creds, file_id):
    service = get_service(creds)
    try:
        file = service.files().get(fileId=file_id).execute()
        mime_type = file.get('mimeType')
        name = file.get('name')
        
        if mime_type.startswith('application/vnd.google-apps'):
            print(f"Le fichier '{name}' est un document Google natif (Docs/Sheets...). Utilisez les commandes d'export dédiées.")
            return
            
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(name, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Téléchargement {int(status.progress() * 100)}%.")
        print(f"Fichier '{name}' téléchargé avec succès !")
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")

def upload_file(creds, file_path):
    service = get_service(creds)
    try:
        if not os.path.exists(file_path):
            print(f"Erreur : Le fichier '{file_path}' n'existe pas sur votre ordinateur.")
            return
            
        name = os.path.basename(file_path)
        file_metadata = {'name': name}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Fichier '{name}' uploadé avec succès ! (ID: {file.get('id')})")
    except Exception as e:
        print(f"Erreur lors de l'upload : {e}")

def list_folder(creds, folder_id):
    service = get_service(creds)
    try:
        folder = service.files().get(fileId=folder_id, fields='name, mimeType').execute()
        if folder.get('mimeType') != 'application/vnd.google-apps.folder':
            print(f"Erreur : '{folder.get('name')}' n'est pas un dossier.")
            return

        folder_name = folder.get('name', folder_id)

        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields="files(id, name, mimeType, size, webViewLink)",
            orderBy="folder,name"
        ).execute()
        files = results.get('files', [])

        from rich.console import Console
        from rich.table import Table
        console = Console()

        if not files:
            console.print(f"[yellow]Le dossier '[bold]{folder_name}[/bold]' est vide.[/yellow]")
            return

        mime_labels = {
            'application/vnd.google-apps.folder':       '📁 Dossier',
            'application/vnd.google-apps.document':     '📄 Docs',
            'application/vnd.google-apps.spreadsheet':  '📊 Sheets',
            'application/vnd.google-apps.presentation': '🖼️  Slides',
            'application/vnd.google-apps.form':         '📝 Forms',
            'application/vnd.google-apps.script':       '⚙️  Script',
            'application/pdf':                          '📕 PDF',
            'image/jpeg':                               '🖼️  Image',
            'image/png':                                '🖼️  Image',
            'video/mp4':                                '🎬 Vidéo',
            'application/zip':                          '🗜️  ZIP',
        }

        table = Table(title=f"📂 Contenu de : {folder_name}  ({len(files)} éléments)")
        table.add_column("Nom", style="cyan", no_wrap=False, min_width=30)
        table.add_column("Type", style="magenta")
        table.add_column("Taille", style="yellow", justify="right")
        table.add_column("ID", style="green")

        for f in files:
            mime = f.get('mimeType', '')
            label = mime_labels.get(mime, mime.split('/')[-1])
            raw_size = f.get('size')
            if raw_size:
                size_kb = int(raw_size) / 1024
                size_str = f"{size_kb:.1f} Ko" if size_kb < 1024 else f"{size_kb/1024:.1f} Mo"
            else:
                size_str = "—"
            table.add_row(f.get('name', ''), label, size_str, f.get('id', ''))

        console.print(table)
        console.print(f"[dim]Lien du dossier : https://drive.google.com/drive/folders/{folder_id}[/dim]")

    except Exception as e:
        print(f"Erreur lors de la liste du dossier : {e}")
