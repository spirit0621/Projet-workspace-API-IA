from googleapiclient.discovery import build
from datetime import datetime

def get_service(creds):
    return build('tasks', 'v1', credentials=creds)

def create_list(creds, title):
    service = get_service(creds)
    tasklist = {'title': title}
    result = service.tasklists().insert(body=tasklist).execute()
    print(f"Liste de tâches '{title}' créée (ID: {result.get('id')}).")
    return result

def clear_completed(creds, tasklist_id):
    service = get_service(creds)
    service.tasks().clear(tasklist=tasklist_id).execute()
    print(f"Les tâches terminées de la liste {tasklist_id} ont été supprimées.")

def add_task(creds, list_id, title, parent_id=None, due=None):
    service = get_service(creds)
    task = {'title': title}
    
    if due:
        try:
            dt = datetime.strptime(due, "%Y-%m-%d")
            task['due'] = dt.isoformat() + "Z"
        except ValueError:
            print("Erreur : La date d'échéance doit être au format YYYY-MM-DD.")
            return None

    try:
        if parent_id:
            result = service.tasks().insert(tasklist=list_id, body=task, parent=parent_id).execute()
        else:
            result = service.tasks().insert(tasklist=list_id, body=task).execute()
        print(f"Tâche '{title}' ajoutée (ID: {result.get('id')}).")
        return result
    except Exception as e:
        print(f"Erreur d'ajout de tâche : {e}")
        return None

def complete_task(creds, list_id, task_id):
    service = get_service(creds)
    try:
        task = service.tasks().get(tasklist=list_id, task=task_id).execute()
        task['status'] = 'completed'
        res = service.tasks().update(tasklist=list_id, task=task_id, body=task).execute()
        print(f"Tâche {task_id} marquée comme terminée.")
        return res
    except Exception as e:
        print(f"Erreur de mise à jour de tâche : {e}")
        return None

def list_pending(creds, list_id):
    service = get_service(creds)
    try:
        results = service.tasks().list(tasklist=list_id, showCompleted=False).execute()
        items = results.get('items', [])
        if not items:
            print("Aucune tâche en attente.")
        else:
            from rich.console import Console
            from rich.table import Table
            console = Console()
            table = Table(title=f"Tâches en attente (Liste: {list_id})")
            table.add_column("Statut", style="cyan")
            table.add_column("Titre", style="magenta")
            table.add_column("ID", style="green")

            for item in items:
                status = "⏳ En attente"
                table.add_row(status, item.get('title', ''), item.get('id', ''))
            
            console.print(table)
        return items
    except Exception as e:
        print(f"Erreur de lecture des tâches : {e}")
        return []
