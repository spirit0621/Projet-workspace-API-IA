from googleapiclient.discovery import build
import uuid
import csv
import io
import requests

def get_service(creds):
    return build('slides', 'v1', credentials=creds)

def clone_slide(creds, presentation_id, slide_id):
    service = get_service(creds)
    requests = [{'duplicateObject': {'objectId': slide_id}}]
    service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': requests}).execute()
    print(f"La slide {slide_id} a été dupliquée avec succès.")

def replace_variables(creds, presentation_id, variable, valeur):
    service = get_service(creds)
    requests = [{'replaceAllText': {'containsText': {'text': variable}, 'replaceText': valeur}}]
    service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': requests}).execute()
    print(f"Remplacement de {variable} par {valeur} terminé.")

def export_slide(creds, presentation_id, slide_id, output_filename):
    service = get_service(creds)
    try:
        response = service.presentations().pages().getThumbnail(
            presentationId=presentation_id,
            pageObjectId=slide_id,
            thumbnailProperties_thumbnailSize='LARGE'
        ).execute()
        url = response.get('contentUrl')
        if url:
            img_data = requests.get(url).content
            with open(output_filename, 'wb') as handler:
                handler.write(img_data)
            print(f"Slide exportée avec succès sous '{output_filename}'.")
        else:
            print("Impossible de générer la vignette de cette slide.")
    except Exception as e:
        print(f"Erreur lors de l'export : {e}")

def insert_textbox(creds, presentation_id, page_id, text):
    service = get_service(creds)
    box_id = f"textbox_{page_id}_custom"
    reqs = [
        {
            'createShape': {
                'objectId': box_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {'width': {'magnitude': 300, 'unit': 'PT'}, 'height': {'magnitude': 50, 'unit': 'PT'}},
                    'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 50, 'translateY': 50, 'unit': 'PT'}
                }
            }
        },
        {
            'insertText': {
                'objectId': box_id,
                'text': text,
                'insertionIndex': 0
            }
        }
    ]
    try:
        service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': reqs}).execute()
        print("Zone de texte insérée.")
    except Exception as e:
        print(f"Erreur d'insertion : {e}")

def insert_table(creds, presentation_id, page_id, rows, cols):
    service = get_service(creds)
    reqs = [
        {
            'createTable': {
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {'width': {'magnitude': 300, 'unit': 'PT'}, 'height': {'magnitude': 150, 'unit': 'PT'}},
                    'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': 50, 'translateY': 50, 'unit': 'PT'}
                },
                'rows': int(rows),
                'columns': int(cols)
            }
        }
    ]
    try:
        service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': reqs}).execute()
        print(f"Tableau ({rows}x{cols}) inséré avec succès.")
    except Exception as e:
        print(f"Erreur d'insertion du tableau : {e}")

def create_presentation(creds, title):
    service = get_service(creds)
    try:
        presentation = service.presentations().create(body={'title': title}).execute()
        pres_id = presentation.get('presentationId')
        print(f"Présentation '{title}' créée avec l'ID : {pres_id}")
        return pres_id
    except Exception as e:
        print(f"Erreur de création : {e}")
        return None

def add_text_slide(creds, presentation_id, title, bullets):
    service = get_service(creds)
    slide_id = f"slide_{uuid.uuid4().hex[:8]}"
    title_id = f"title_{uuid.uuid4().hex[:8]}"
    body_id = f"body_{uuid.uuid4().hex[:8]}"
    
    bullets_text = "\n".join(f"• {b}" for b in bullets)

    reqs = [
        {"createSlide": {"objectId": slide_id, "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}}},
        {"createShape": {"objectId": title_id, "shapeType": "TEXT_BOX",
            "elementProperties": {"pageObjectId": slide_id,
                "size": {"width": {"magnitude": 600, "unit": "PT"}, "height": {"magnitude": 60, "unit": "PT"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": 50, "translateY": 30, "unit": "PT"}}}},
        {"insertText": {"objectId": title_id, "text": title, "insertionIndex": 0}},
        {"createShape": {"objectId": body_id, "shapeType": "TEXT_BOX",
            "elementProperties": {"pageObjectId": slide_id,
                "size": {"width": {"magnitude": 600, "unit": "PT"}, "height": {"magnitude": 300, "unit": "PT"}},
                "transform": {"scaleX": 1, "scaleY": 1, "translateX": 50, "translateY": 110, "unit": "PT"}}}},
        {"insertText": {"objectId": body_id, "text": bullets_text, "insertionIndex": 0}},
    ]
    try:
        service.presentations().batchUpdate(presentationId=presentation_id, body={"requests": reqs}).execute()
    except Exception as e:
        print(f"Erreur lors de l'ajout de la slide '{title}' : {e}")

def mass_generate(creds, presentation_id, template_slide_id, csv_filename):
    service = get_service(creds)
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            print("Le fichier CSV est vide ou invalide.")
            return

        for index, row in enumerate(rows):
            new_slide_id = f"generated_{uuid.uuid4().hex[:8]}"
            duplicate_req = [{'duplicateObject': {'objectId': template_slide_id, 'objectIds': {template_slide_id: new_slide_id}}}]
            service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': duplicate_req}).execute()
            
            replace_reqs = []
            for key, value in row.items():
                replace_reqs.append({
                    'replaceAllText': {
                        'containsText': {'text': f"{{{{{key}}}}}"},
                        'replaceText': str(value),
                        'pageObjectIds': [new_slide_id]
                    }
                })
            
            if replace_reqs:
                service.presentations().batchUpdate(presentationId=presentation_id, body={'requests': replace_reqs}).execute()
                
            print(f"Slide générée pour la ligne {index + 1}.")
    except Exception as e:
        print(f"Erreur lors de la génération en masse : {e}")

def export_pdf(creds, presentation_id, output_filename):
    from googleapiclient.http import MediaIoBaseDownload
    drive_service = build('drive', 'v3', credentials=creds)
    try:
        request = drive_service.files().export_media(fileId=presentation_id, mimeType='application/pdf')
        with io.FileIO(output_filename, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        print(f"Présentation {presentation_id} exportée en PDF sous le nom '{output_filename}'.")
    except Exception as e:
        print(f"Erreur lors de l'exportation PDF : {e}")
