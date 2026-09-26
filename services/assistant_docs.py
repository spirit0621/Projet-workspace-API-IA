from googleapiclient.discovery import build

def get_service(creds):
    return build('docs', 'v1', credentials=creds)

def format_bold(creds, doc_id, text_to_bold):
    """Met en gras toutes les occurrences d'un texte dans un document."""
    service = get_service(creds)
    try:
        # Lire le document pour trouver les index du texte cible
        document = service.documents().get(documentId=doc_id).execute()
        content = document.get('body', {}).get('content', [])
        
        requests = []
        for element in content:
            if 'paragraph' not in element:
                continue
            for p_elem in element['paragraph'].get('elements', []):
                text_run = p_elem.get('textRun')
                if not text_run:
                    continue
                run_text = text_run.get('content', '')
                start_offset = 0
                while True:
                    idx = run_text.find(text_to_bold, start_offset)
                    if idx == -1:
                        break
                    abs_start = p_elem['startIndex'] + idx
                    abs_end = abs_start + len(text_to_bold)
                    requests.append({
                        'updateTextStyle': {
                            'range': {'startIndex': abs_start, 'endIndex': abs_end},
                            'textStyle': {'bold': True},
                            'fields': 'bold'
                        }
                    })
                    start_offset = idx + len(text_to_bold)
        
        if not requests:
            print(f"Texte '{text_to_bold}' introuvable dans le document.")
            return
        
        service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        print(f"✅ {len(requests)} occurrence(s) de '{text_to_bold}' mises en gras.")
    except Exception as e:
        print(f"Erreur lors du formatage en gras : {e}")

def extract_structure(creds, doc_id):
    service = get_service(creds)
    document = service.documents().get(documentId=doc_id).execute()
    print(f"Structure de '{document.get('title')}' :")
    for element in document.get('body').get('content'):
        if 'paragraph' in element:
            style = element.get('paragraph').get('paragraphStyle', {}).get('namedStyleType')
            if style and 'HEADING' in style:
                text = ""
                for p_element in element.get('paragraph').get('elements'):
                    if 'textRun' in p_element:
                        text += p_element.get('textRun').get('content')
                print(f"- [{style}] {text.strip()}")

def read_content(creds, doc_id, return_text=False):
    service = get_service(creds)
    document = service.documents().get(documentId=doc_id).execute()
    
    full_text = ""
    for element in document.get('body').get('content'):
        if 'paragraph' in element:
            text = ""
            for p_element in element.get('paragraph').get('elements'):
                if 'textRun' in p_element:
                    text += p_element.get('textRun').get('content')
            if text.strip():
                full_text += text.strip() + "\n"
                
    if return_text:
        return full_text
        
    print(f"--- Contenu de '{document.get('title')}' ---")
    print(full_text.strip())
    print("-----------------------------------")

def list_comments(creds, file_id):
    # Les commentaires se lisent via l'API Drive
    drive_service = build('drive', 'v3', credentials=creds)
    comments = drive_service.comments().list(fileId=file_id, fields="comments(content, author)").execute()
    for comment in comments.get('comments', []):
        print(f"[{comment['author']['displayName']}] : {comment['content']}")

def insert_image(creds, doc_id, image_url):
    """Insère une image depuis une URL à la fin du document."""
    service = get_service(creds)
    try:
        # On insère à l'index 1 (début du document) pour éviter la complexité du curseur
        document = service.documents().get(documentId=doc_id).execute()
        # Trouver le dernier index pour insérer à la fin
        end_index = document['body']['content'][-1]['endIndex'] - 1
        requests = [
            {
                'insertInlineImage': {
                    'uri': image_url,
                    'location': {'index': end_index},
                    'objectSize': {
                        'height': {'magnitude': 200, 'unit': 'PT'},
                        'width': {'magnitude': 300, 'unit': 'PT'}
                    }
                }
            }
        ]
        service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        print(f"✅ Image insérée avec succès à la fin du document.")
    except Exception as e:
        print(f"Erreur lors de l'insertion de l'image : {e}")

def replace_text(creds, doc_id, old_text, new_text):
    service = get_service(creds)
    requests = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': old_text,
                    'matchCase': False
                },
                'replaceText': new_text,
            }
        }
    ]
    try:
        result = service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        replacements = result.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)
        print(f"Remplacement effectué : {replacements} occurrences de '{old_text}' remplacées par '{new_text}'.")
    except Exception as e:
        print(f"Erreur lors du remplacement : {e}")

def export_pdf(creds, doc_id, output_filename):
    import io
    from googleapiclient.http import MediaIoBaseDownload
    drive_service = build('drive', 'v3', credentials=creds)
    try:
        request = drive_service.files().export_media(fileId=doc_id, mimeType='application/pdf')
        with io.FileIO(output_filename, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        print(f"Document {doc_id} exporté en PDF sous le nom '{output_filename}'.")
    except Exception as e:
        print(f"Erreur lors de l'export : {e}")

def export_word(creds, doc_id, output_filename):
    import io
    from googleapiclient.http import MediaIoBaseDownload
    drive_service = build('drive', 'v3', credentials=creds)
    try:
        request = drive_service.files().export_media(fileId=doc_id, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        with io.FileIO(output_filename, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        print(f"Document {doc_id} exporté en Word (DOCX) sous le nom '{output_filename}'.")
    except Exception as e:
        print(f"Erreur lors de l'export Word : {e}")

def append_text(creds, doc_id, text):
    """Ajoute un nouveau paragraphe à la fin du document."""
    service = get_service(creds)
    try:
        # Récupérer la taille actuelle pour insérer à la fin
        document = service.documents().get(documentId=doc_id).execute()
        end_index = document['body']['content'][-1]['endIndex'] - 1

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': end_index,
                    },
                    'text': "\n" + text + "\n"
                }
            }
        ]

        service.documents().batchUpdate(
            documentId=doc_id, body={'requests': requests}).execute()
        print(f"✅ Texte ajouté avec succès à la fin du document.")
    except Exception as e:
        print(f"Erreur lors de l'ajout de texte : {e}")

def create_from_template(creds, template_id, title, variables_json):
    """Crée un document depuis un template et remplace les variables."""
    import json
    from googleapiclient.discovery import build
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = get_service(creds)
    
    try:
        variables = json.loads(variables_json)
        
        # 1. Copier le document modèle
        print(f"⏳ Copie du template {template_id}...")
        copied_file = {'name': title}
        new_doc = drive_service.files().copy(
            fileId=template_id, body=copied_file).execute()
        new_doc_id = new_doc.get('id')
        print(f"✅ Nouveau document créé : {title} (ID: {new_doc_id})")
        
        # 2. Remplacer les variables
        print("⏳ Remplacement des variables...")
        requests = []
        for key, value in variables.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': key,
                        'matchCase': False
                    },
                    'replaceText': str(value),
                }
            })
            
        if requests:
            result = docs_service.documents().batchUpdate(
                documentId=new_doc_id, body={'requests': requests}).execute()
            
            # Compter les remplacements
            total_replacements = 0
            for reply in result.get('replies', []):
                total_replacements += reply.get('replaceAllText', {}).get('occurrencesChanged', 0)
                
            print(f"✅ {total_replacements} variable(s) remplacée(s).")
            
        print(f"Document accessible ici : https://docs.google.com/document/d/{new_doc_id}")
        return new_doc_id
        
    except json.JSONDecodeError:
        print("Erreur : variables_json n'est pas un JSON valide.")
    except Exception as e:
        print(f"Erreur lors de la création depuis le template : {e}")
