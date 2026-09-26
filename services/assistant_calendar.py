from googleapiclient.discovery import build
import datetime

def get_service(creds):
    return build('calendar', 'v3', credentials=creds)

def list_events(creds, max_results=10):
    service = get_service(creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indique UTC
    print(f"Récupération des {max_results} prochains événements de votre calendrier principal...")
    try:
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=int(max_results), singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print("Aucun événement à venir trouvé.")
        else:
            from rich.console import Console
            from rich.table import Table
            console = Console()
            table = Table(title="Prochains événements Calendar")
            table.add_column("Date", style="cyan")
            table.add_column("Heure", style="magenta")
            table.add_column("Événement", style="green")

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                if 'T' in start:
                    date_part, time_part = start.split('T')
                    time_part = time_part[:5] # keep HH:MM
                else:
                    date_part = start
                    time_part = "Toute la journée"
                
                summary = event.get('summary', 'Sans titre')
                table.add_row(date_part, time_part, summary)
            
            console.print(table)
        return events
    except Exception as e:
        print(f"Erreur lors de la récupération du calendrier : {e}")
        return []

def add_reminder(creds, event_id, minutes):
    service = get_service(creds)
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['reminders'] = {
        'useDefault': False,
        'overrides': [{'method': 'popup', 'minutes': int(minutes)}]
    }
    updated = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    print(f"Rappel de {minutes} minutes ajouté à l'événement {event_id}.")
    return updated

def rsvp(creds, event_id, response):
    print(f"Réponse '{response}' envoyée pour l'événement {event_id} (Fonction simulée).")
    return {"status": "ok", "event_id": event_id, "response": response}

def create_event(creds, summary, start_time, end_time, emails=None, timezone='Europe/Paris'):
    service = get_service(creds)
    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': timezone},
        'end': {'dateTime': end_time, 'timeZone': timezone},
    }
    if emails:
        event['attendees'] = [{'email': email.strip()} for email in emails.split(',')]
    
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Événement créé avec succès ! Lien : {created_event.get('htmlLink')}")
        return created_event
    except Exception as e:
        print(f"Erreur lors de la création de l'événement : {e}")
        return None

def delete_event(creds, event_id):
    service = get_service(creds)
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"Événement {event_id} supprimé de l'agenda.")
    except Exception as e:
        print(f"Erreur lors de la suppression : {e}")
