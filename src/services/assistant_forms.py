from googleapiclient.discovery import build
import csv
import json

def get_service(creds):
    return build('forms', 'v1', credentials=creds)

def create_form(creds, title):
    service = get_service(creds)
    form = {'info': {'title': title}}
    result = service.forms().create(body=form).execute()
    print(f"Formulaire '{title}' créé avec succès !")
    print(f"Lien : https://docs.google.com/forms/d/{result.get('formId')}/edit")
    return result

def get_responses(creds, form_id):
    service = get_service(creds)
    result = service.forms().responses().list(formId=form_id).execute()
    responses = result.get('responses', [])
    print(f"--- {len(responses)} réponse(s) trouvée(s) ---")
    for r in responses:
        print(f"Réponse ID : {r.get('responseId')}")
    return responses

def add_question(creds, form_id, question_title, question_type, options=None):
    service = get_service(creds)
    question_item = {
        'title': question_title,
    }
    if question_type.upper() == 'RADIO' and options:
        opts = [{'value': opt.strip()} for opt in options.split(',')]
        question_item['questionItem'] = {
            'question': {
                'required': True,
                'choiceQuestion': {
                    'type': 'RADIO',
                    'options': opts
                }
            }
        }
    else:
        question_item['questionItem'] = {
            'question': {
                'required': True,
                'textQuestion': {'paragraph': False}
            }
        }
        
    requests = [{
        'createItem': {
            'item': question_item,
            'location': {'index': 0}
        }
    }]
    try:
        service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        print(f"Question '{question_title}' ajoutée.")
    except Exception as e:
        print(f"Erreur d'ajout de question : {e}")

def export_responses(creds, form_id, output_csv):
    service = get_service(creds)
    try:
        result = service.forms().responses().list(formId=form_id).execute()
        responses = result.get('responses', [])
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ResponseID', 'CreateTime', 'Answers'])
            for r in responses:
                answers = str(r.get('answers', {}))
                writer.writerow([r.get('responseId'), r.get('createTime'), answers])
        print(f"Réponses exportées dans '{output_csv}'.")
    except Exception as e:
        print(f"Erreur d'exportation : {e}")

def close_form(creds, form_id):
    print(f"La fermeture stricte d'un formulaire n'est pas supportée nativement par l'API Forms REST actuelle. (Formulaire {form_id})")

def add_image(creds, form_id, image_url):
    service = get_service(creds)
    requests = [{
        'createItem': {
            'item': {
                'imageItem': {
                    'image': {
                        'sourceUri': image_url
                    }
                }
            },
            'location': {'index': 0}
        }
    }]
    try:
        service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        print("Image d'en-tête (ImageItem) ajoutée.")
    except Exception as e:
        print(f"Erreur d'ajout de l'image : {e}")

def add_conditional_question(creds, form_id, question_title, json_config):
    service = get_service(creds)
    try:
        config = json.loads(json_config)
        options = []
        for choice in config:
            opt = {'value': choice.get('value')}
            if 'goToAction' in choice:
                opt['goToAction'] = choice['goToAction']
            elif 'goToSectionId' in choice:
                opt['goToSectionId'] = choice['goToSectionId']
            options.append(opt)
            
        requests = [{
            'createItem': {
                'item': {
                    'title': question_title,
                    'questionItem': {
                        'question': {
                            'required': True,
                            'choiceQuestion': {
                                'type': 'RADIO',
                                'options': options
                            }
                        }
                    }
                },
                'location': {'index': 0}
            }
        }]
        service.forms().batchUpdate(formId=form_id, body={'requests': requests}).execute()
        print(f"Question conditionnelle '{question_title}' ajoutée.")
    except Exception as e:
        print(f"Erreur d'ajout de la question conditionnelle : {e}")
