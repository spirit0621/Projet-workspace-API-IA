from googleapiclient.discovery import build

def get_service(creds):
    return build('sheets', 'v4', credentials=creds)

def add_sheet(creds, sheet_id, title):
    service = get_service(creds)
    requests = [{'addSheet': {'properties': {'title': title}}}]
    service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()
    print(f"Nouvel onglet '{title}' créé.")

def format_green(creds, sheet_id, cell_range):
    """Colore le fond d'une plage de cellules en vert."""
    service = get_service(creds)
    try:
        # Récupérer les métadonnées pour trouver le sheetId numérique
        spreadsheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        
        # Extraire le nom de l'onglet depuis la plage (ex: "Feuil1!A1:B10" ou "A1:B10")
        if '!' in cell_range:
            sheet_name, range_part = cell_range.split('!', 1)
        else:
            sheet_name = spreadsheet['sheets'][0]['properties']['title']
            range_part = cell_range
        
        sheet_id_num = next(
            s['properties']['sheetId']
            for s in spreadsheet['sheets']
            if s['properties']['title'] == sheet_name
        )

        # Parser la plage (A1:B10) en indices
        from googleapiclient.discovery import build
        import re
        def col_to_index(col):
            idx = 0
            for c in col.upper():
                idx = idx * 26 + (ord(c) - ord('A') + 1)
            return idx - 1

        match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', range_part.upper())
        if not match:
            print("Format de plage invalide. Utilisez par exemple A1:C5.")
            return

        sc, sr, ec, er = match.groups()
        requests = [{
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id_num,
                    'startRowIndex': int(sr) - 1,
                    'endRowIndex': int(er),
                    'startColumnIndex': col_to_index(sc),
                    'endColumnIndex': col_to_index(ec) + 1
                },
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.18, 'green': 0.80, 'blue': 0.44}
                    }
                },
                'fields': 'userEnteredFormat.backgroundColor'
            }
        }]
        service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body={'requests': requests}).execute()
        print(f"✅ La plage {cell_range} a été colorée en vert.")
    except Exception as e:
        print(f"Erreur lors du formatage : {e}")


def add_formula(creds, sheet_id, cell_range, formula):
    service = get_service(creds)
    body = {'values': [[formula]]}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=cell_range, valueInputOption="USER_ENTERED", body=body).execute()
    print(f"Formule {formula} ajoutée en {cell_range}.")

import json

def read_range(creds, sheet_id, range_name, return_data=False):
    service = get_service(creds)
    try:
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])
        if return_data:
            return values
        if not values:
            print('Aucune donnée trouvée.')
        else:
            print(json.dumps(values, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur lors de la lecture : {e}")

def add_chart(creds, sheet_id, tab_id):
    service = get_service(creds)
    requests = [
        {
            "addChart": {
                "chart": {
                    "spec": {
                        "title": "Nouveau Graphique",
                        "basicChart": {
                            "chartType": "COLUMN",
                            "legendPosition": "BOTTOM_LEGEND",
                            "domains": [{"domain": {"sourceRange": {"sources": [{"sheetId": int(tab_id), "startRowIndex": 0, "endRowIndex": 10, "startColumnIndex": 0, "endColumnIndex": 1}]}}}],
                            "series": [{"series": {"sourceRange": {"sources": [{"sheetId": int(tab_id), "startRowIndex": 0, "endRowIndex": 10, "startColumnIndex": 1, "endColumnIndex": 2}]}}}],
                        }
                    },
                    "position": {
                        "overlayPosition": {
                            "anchorCell": {"sheetId": int(tab_id), "rowIndex": 2, "columnIndex": 3},
                        }
                    }
                }
            }
        }
    ]
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()
        print(f"Graphique ajouté au classeur.")
    except Exception as e:
        print(f"Erreur lors de l'ajout du graphique : {e}")

def add_filter(creds, sheet_id, tab_id):
    service = get_service(creds)
    requests = [
        {
            "setBasicFilter": {
                "filter": {
                    "range": {
                        "sheetId": int(tab_id),
                        "startRowIndex": 0,
                        "startColumnIndex": 0
                    }
                }
            }
        }
    ]
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={'requests': requests}).execute()
        print(f"Filtre ajouté sur la feuille {tab_id}.")
    except Exception as e:
        print(f"Erreur lors de l'ajout du filtre : {e}")

import requests as req
from google.auth.transport.requests import Request

def export_pdf(creds, sheet_id, tab_id, output_filename):
    if not creds.valid:
        creds.refresh(Request())
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=pdf&gid={tab_id}"
    headers = {'Authorization': f'Bearer {creds.token}'}
    try:
        response = req.get(url, headers=headers)
        if response.status_code == 200:
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            print(f"Onglet {tab_id} exporté avec succès dans {output_filename}")
        else:
            print(f"Erreur HTTP {response.status_code} lors de l'exportation. Détails : {response.text}")
    except Exception as e:
        print(f"Erreur lors de l'exportation PDF : {e}")

def write_column(creds, sheet_id, cell_range, values_list):
    """Écrit une liste de valeurs verticalement dans une colonne."""
    service = get_service(creds)
    # Format the data into a list of lists representing rows (each inner list is a row with 1 column)
    body = {
        'values': [[str(v)] for v in values_list]
    }
    try:
        service.spreadsheets().values().update(
            spreadsheetId=sheet_id, range=cell_range,
            valueInputOption="USER_ENTERED", body=body).execute()
        print(f"✅ Données écrites avec succès dans la plage {cell_range}.")
    except Exception as e:
        print(f"Erreur lors de l'écriture en colonne : {e}")
