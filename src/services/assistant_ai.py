import os
import json
import datetime
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

try:
    from services import (
        assistant_docs,
        assistant_calendar,
        assistant_sheets,
        assistant_slides,
        assistant_drive,
        assistant_tasks,
        secrets_manager
    )
except ImportError:
    from src.services import (
        assistant_docs,
        assistant_calendar,
        assistant_sheets,
        assistant_slides,
        assistant_drive,
        assistant_tasks,
        secrets_manager
    )

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
FALLBACK_MODELS = [DEFAULT_MODEL, "gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.8-flash", "gemini-3.5-flash-lite"]

def _find_history_file() -> str:
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(root_dir, "data", "usage_history.json"),
        os.path.join("data", "usage_history.json"),
        "usage_history.json",
        os.path.join(root_dir, "usage_history.json")
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # Par défaut, enregistrer dans data/
    data_dir = os.path.join(root_dir, "data")
    try:
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, "usage_history.json")
    except Exception:
        return "usage_history.json"


HISTORY_FILE = _find_history_file()
MONTHLY_TOKEN_BUDGET = 1_000_000

def get_client():
    try:
        api_key = secrets_manager.load_gemini_api_key()
        if api_key:
            return genai.Client(api_key=api_key)
        return genai.Client()
    except Exception as e:
        print("Erreur d'initialisation de Gemini. Avez-vous défini GEMINI_API_KEY ?")
        print(e)
        return None

def generate_content_with_retry(client, contents, config=None, model=None, max_retries_per_model=2):
    """
    Exécute client.models.generate_content avec retries exponentiels et bascule
    automatique sur des modèles de secours en cas d'erreur 503 ou 429.
    """
    primary = model or DEFAULT_MODEL
    models_to_try = [primary]
    for m in FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_exception = None

    for m in models_to_try:
        for attempt in range(1, max_retries_per_model + 1):
            try:
                if m != primary and attempt == 1:
                    print(f"🔄 Bascule automatique sur le modèle de secours '{m}'...")
                return client.models.generate_content(
                    model=m,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                err_str = str(e).lower()
                last_exception = e
                
                if "404" in err_str or "not_found" in err_str:
                    break
                
                is_transient = (
                    "503" in err_str or 
                    "unavailable" in err_str or 
                    "demand" in err_str or 
                    "429" in err_str or 
                    "resource_exhausted" in err_str
                )
                if is_transient and attempt < max_retries_per_model:
                    wait_time = attempt * 3
                    print(f"⚠️ Serveur Gemini ({m}) en forte demande (503). Nouvelle tentative dans {wait_time}s...")
                    time.sleep(wait_time)
                elif is_transient:
                    print(f"⚠️ Modèle '{m}' temporairement indisponible. Test d'un modèle alternatif...")
                    break
                else:
                    raise e

    raise last_exception

def _log_and_display_usage(response):
    try:
        usage = response.usage_metadata
        if not usage:
            return
            
        prompt_tokens = usage.prompt_token_count
        candidate_tokens = usage.candidates_token_count
        total_tokens = usage.total_token_count
        
        record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "prompt_tokens": prompt_tokens,
            "candidate_tokens": candidate_tokens,
            "total_tokens": total_tokens
        }
        
        target_file = _find_history_file()
        history = []
        if os.path.exists(target_file):
            with open(target_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        history.append(record)
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
            
        total_tokens_used = sum(r.get("total_tokens", 0) for r in history)
        tokens_remaining = MONTHLY_TOKEN_BUDGET - total_tokens_used
            
        console = Console()
        panel_content = (
            f"• Coût de l'action    : [bold]{total_tokens} tokens[/bold] (Entrée: {prompt_tokens}, Sortie: {candidate_tokens})\n"
            f"• Budget restant      : [bold green]{tokens_remaining} tokens[/bold green] (sur {MONTHLY_TOKEN_BUDGET})"
        )
        console.print(Panel(panel_content, title="📊 Consommation", border_style="blue", expand=False))
        
    except Exception as e:
        print(f"Erreur lors du calcul des coûts : {e}")

# ─────────────────────────────────────────────────────
# 1. SUMMARIZE : Résumé d'un document Google Docs
# ─────────────────────────────────────────────────────
def summarize(creds, doc_id):
    print("⏳ Lecture du document...")
    try:
        text_content = assistant_docs.read_content(creds, doc_id, return_text=True)
    except Exception as e:
        print(f"Erreur lors de la lecture du document: {e}")
        return None

    if not text_content or not text_content.strip():
        print("Le document semble vide.")
        return None

    print("⏳ Génération du résumé par Gemini...")
    client = get_client()
    if not client:
        return None

    try:
        response = generate_content_with_retry(
            client=client,
            contents=f"Résume ce document de manière concise et structurée en français :\n\n{text_content}"
        )
        console = Console()
        console.print("\n[bold cyan]✨ Résumé de Gemini :[/bold cyan]\n")
        console.print(Markdown(response.text))
        _log_and_display_usage(response)
        return response.text
    except Exception as e:
        print(f"Erreur lors de la génération du résumé : {e}")
        return None

# ─────────────────────────────────────────────────────
# 2. PARSE_EVENT : Langage naturel → Calendar
# ─────────────────────────────────────────────────────
class CalendarEvent(BaseModel):
    summary: str = Field(description="Le titre de l'événement.")
    start_time: str = Field(description="La date et heure de début au format RFC3339 (ex: 2026-09-06T10:00:00).")
    end_time: str = Field(description="La date et heure de fin au format RFC3339 (ex: 2026-09-06T11:00:00).")

def parse_event(creds, prompt):
    print("⏳ Analyse de la demande avec Gemini...")
    client = get_client()
    if not client:
        return None

    now = datetime.datetime.now().isoformat()

    try:
        config = types.GenerateContentConfig(
            response_mime_type='application/json',
            response_json_schema=CalendarEvent.model_json_schema()
        )
        response = generate_content_with_retry(
            client=client,
            contents=f"Nous sommes le {now}. Extrais les détails de cet événement pour Google Calendar. Si la durée n'est pas spécifiée, mets 1 heure par défaut : '{prompt}'",
            config=config
        )
        event_data = json.loads(response.text)
        summary = event_data.get('summary')
        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')

        print(f"✅ Événement compris : '{summary}' de {start_time} à {end_time}.")
        print("⏳ Création dans Google Calendar...")
        created = assistant_calendar.create_event(creds, summary, start_time, end_time)
        _log_and_display_usage(response)
        return {"event_data": event_data, "created_event": created}
    except Exception as e:
        print(f"Erreur lors de l'analyse ou de la création de l'événement : {e}")
        return None

# ─────────────────────────────────────────────────────
# 3. ASK_SHEET : Question en langage naturel sur un Sheet
# ─────────────────────────────────────────────────────
def ask_sheet(creds, sheet_id, question):
    print("⏳ Lecture des données du Sheet...")
    try:
        data = assistant_sheets.read_range(creds, sheet_id, "A1:Z200", return_data=True)
    except Exception as e:
        print(f"Erreur lors de la lecture du Sheet : {e}")
        return None

    if not data:
        print("Le Sheet semble vide ou illisible.")
        return None

    print("⏳ Analyse par Gemini...")
    client = get_client()
    if not client:
        return None

    data_str = json.dumps(data, ensure_ascii=False, indent=2)

    try:
        response = generate_content_with_retry(
            client=client,
            contents=(
                f"Voici des données extraites d'un Google Sheet (format JSON, première ligne = en-têtes) :\n\n"
                f"{data_str}\n\n"
                f"Réponds à la question suivante en français, de façon claire et précise : {question}"
            )
        )
        console = Console()
        console.print("\n[bold green]📊 Réponse de Gemini :[/bold green]\n")
        console.print(Markdown(response.text))
        _log_and_display_usage(response)
        return response.text
    except Exception as e:
        print(f"Erreur lors de l'analyse : {e}")
        return None

# ─────────────────────────────────────────────────────
# 4. PROOFREAD : Relecture et correction d'un Doc
# ─────────────────────────────────────────────────────
def proofread(creds, doc_id):
    print("⏳ Lecture du document...")
    try:
        text_content = assistant_docs.read_content(creds, doc_id, return_text=True)
    except Exception as e:
        print(f"Erreur lors de la lecture du document: {e}")
        return None

    if not text_content or not text_content.strip():
        print("Le document semble vide.")
        return None

    print("⏳ Relecture par Gemini...")
    client = get_client()
    if not client:
        return None

    try:
        response = generate_content_with_retry(
            client=client,
            contents=(
                "Relis attentivement le texte suivant en français. "
                "Identifie et corrige les fautes d'orthographe, de grammaire et de syntaxe. "
                "Propose également des reformulations plus percutantes si nécessaire. "
                "Présente le résultat de façon claire avec le texte corrigé et une liste des changements suggérés.\n\n"
                f"{text_content}"
            )
        )
        console = Console()
        console.print("\n[bold yellow]📝 Résultat de la relecture par Gemini :[/bold yellow]\n")
        console.print(Markdown(response.text))
        _log_and_display_usage(response)
        return response.text
    except Exception as e:
        print(f"Erreur lors de la relecture : {e}")
        return None

# ─────────────────────────────────────────────────────
# 5. GENERATE_SLIDES : Génération auto de présentation
# ─────────────────────────────────────────────────────
class Slide(BaseModel):
    title: str = Field(description="Le titre de la diapositive.")
    bullets: list[str] = Field(description="Liste de 3 à 5 points clés pour la diapositive.")

class Presentation(BaseModel):
    presentation_title: str = Field(description="Le titre global de la présentation.")
    slides: list[Slide] = Field(description="La liste des diapositives de la présentation.")

def generate_slides(creds, topic, num_slides=5):
    print(f"⏳ Génération du plan de la présentation par Gemini ({num_slides} slides de contenu)...")
    client = get_client()
    if not client:
        return None

    try:
        config = types.GenerateContentConfig(
            response_mime_type='application/json',
            response_json_schema=Presentation.model_json_schema()
        )
        response = generate_content_with_retry(
            client=client,
            contents=(
                f"Crée une présentation professionnelle en français sur le sujet : '{topic}'. "
                f"Elle doit commencer par une diapositive de titre (Introduction/Titre), "
                f"suivie d'exactement {num_slides} diapositives de contenu, "
                f"et se terminer par une diapositive de conclusion. "
                "Pour chaque diapositive, fournis un titre accrocheur et 3 à 5 points clés concis."
            ),
            config=config
        )

        pres_data = json.loads(response.text)
        pres_title = pres_data.get('presentation_title', topic)
        slides = pres_data.get('slides', [])

        print(f"✅ Plan généré : '{pres_title}' avec {len(slides)} slides (incluant titre et conclusion).")
        print("⏳ Création de la présentation dans Google Slides...")

        pres_id = assistant_slides.create_presentation(creds, pres_title)
        if not pres_id:
            print("Impossible de créer la présentation.")
            return None

        for i, slide in enumerate(slides):
            print(f"  → Ajout de la slide {i+1}/{len(slides)} : {slide.get('title', '')}")
            assistant_slides.add_text_slide(
                creds, pres_id,
                slide.get('title', f'Slide {i+1}'),
                slide.get('bullets', [])
            )

        console = Console()
        console.print(f"\n[bold magenta]🎉 Présentation créée avec succès ![/bold magenta]")
        console.print(f"[cyan]Ouvrez-la sur : https://docs.google.com/presentation/d/{pres_id}/edit[/cyan]")
        _log_and_display_usage(response)
        return {"presentation_id": pres_id, "title": pres_title, "slides": slides}
    except Exception as e:
        print(f"Erreur lors de la génération de la présentation : {e}")
        return None

# ─────────────────────────────────────────────────────
# 6. GENERATE_DOC : Générer du texte et l'injecter
# ─────────────────────────────────────────────────────
def generate_doc(creds, doc_id, prompt):
    print("⏳ Génération du contenu par Gemini...")
    client = get_client()
    if not client:
        return None
    try:
        response = generate_content_with_retry(
            client=client,
            contents=prompt
        )
        print("⏳ Insertion du contenu généré à la fin du document...")
        assistant_docs.append_text(creds, doc_id, response.text)
        _log_and_display_usage(response)
        return response.text
    except Exception as e:
        print(f"Erreur lors de la génération ou insertion : {e}")
        return None

# ─────────────────────────────────────────────────────
# 7. CLASSIFY_SHEET : Classifier des données Sheets
# ─────────────────────────────────────────────────────
class ClassificationResult(BaseModel):
    categories: list[str] = Field(description="La liste des catégories assignées, une pour chaque ligne lue, dans le même ordre.")

def classify_sheet(creds, sheet_id, read_range, write_range, categories_str):
    print("⏳ Lecture des données depuis le Sheet...")
    try:
        data = assistant_sheets.read_range(creds, sheet_id, read_range, return_data=True)
    except Exception as e:
        print(f"Erreur lors de la lecture du Sheet : {e}")
        return None

    if not data:
        print("Le Sheet semble vide ou illisible.")
        return None

    print(f"⏳ Classification par Gemini ({len(data)} lignes)...")
    client = get_client()
    if not client:
        return None

    data_str = json.dumps(data, ensure_ascii=False)

    try:
        config = types.GenerateContentConfig(
            response_mime_type='application/json',
            response_json_schema=ClassificationResult.model_json_schema()
        )
        response = generate_content_with_retry(
            client=client,
            contents=(
                f"Voici un tableau de données :\n{data_str}\n\n"
                f"Pour chaque ligne de ce tableau, choisis UNE SEULE catégorie appropriée parmi la liste suivante : {categories_str}. "
                f"Tu dois renvoyer exactement {len(data)} catégories, dans l'ordre strict des lignes."
            ),
            config=config
        )
        result = json.loads(response.text)
        labels = result.get('categories', [])
        
        if len(labels) != len(data):
            print(f"Attention : Gemini a retourné {len(labels)} labels pour {len(data)} lignes lues.")
        
        print(f"✅ Classification terminée. Écriture dans le Sheet...")
        assistant_sheets.write_column(creds, sheet_id, write_range, labels)
        _log_and_display_usage(response)
        return labels
    except Exception as e:
        print(f"Erreur lors de la classification : {e}")
        return None

# ─────────────────────────────────────────────────────
# 8. ESTIMATE_COST : Estimer le coût d'un document
# ─────────────────────────────────────────────────────
def estimate_cost(creds, doc_id):
    print("⏳ Lecture du document...")
    try:
        text_content = assistant_docs.read_content(creds, doc_id, return_text=True)
    except Exception as e:
        print(f"Erreur lors de la lecture du document: {e}")
        return None

    if not text_content or not text_content.strip():
        print("Le document semble vide.")
        return None

    print("⏳ Calcul des tokens...")
    client = get_client()
    if not client:
        return None
        
    try:
        response = client.models.count_tokens(
            model=DEFAULT_MODEL,
            contents=text_content
        )
        tokens = response.total_tokens
        
        console = Console()
        console.print(f"\nCe document fait [bold]{tokens}[/bold] tokens.")
        console.print(f"L'analyser coûtera environ [bold green]{tokens} tokens[/bold green].\n")
        return tokens
    except Exception as e:
        print(f"Erreur lors de l'estimation : {e}")
        return None

# ─────────────────────────────────────────────────────
# 9. STATS : Afficher les statistiques de consommation
# ─────────────────────────────────────────────────────
def stats():
    target_file = _find_history_file()
    if not os.path.exists(target_file):
        print("Aucun historique d'utilisation trouvé.")
        return {
            "monthly_budget": MONTHLY_TOKEN_BUDGET,
            "total_tokens_used": 0,
            "tokens_remaining": MONTHLY_TOKEN_BUDGET,
            "total_requests": 0
        }
        
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            history = json.load(f)
            
        total_requests = len(history)
        total_tokens = sum(r.get("total_tokens", 0) for r in history)
        tokens_remaining = MONTHLY_TOKEN_BUDGET - total_tokens
        
        console = Console()
        panel_content = (
            f"• Budget global alloué             : [bold]{MONTHLY_TOKEN_BUDGET} tokens[/bold]\n"
            f"• Total des tokens consommés       : [bold red]{total_tokens} tokens[/bold red]\n"
            f"• Tokens restants disponibles      : [bold green]{tokens_remaining} tokens[/bold green]\n"
            f"• Nombre de requêtes IA effectuées : [bold]{total_requests}[/bold]"
        )
        console.print(Panel(panel_content, title="📈 Tableau de Bord Budget IA", border_style="magenta", expand=False))
        return {
            "monthly_budget": MONTHLY_TOKEN_BUDGET,
            "total_tokens_used": total_tokens,
            "tokens_remaining": tokens_remaining,
            "total_requests": total_requests
        }
    except Exception as e:
        print(f"Erreur lors de la lecture des statistiques : {e}")
        return None

# ─────────────────────────────────────────────────────
# 10. MEETING : Synthèse audio de réunion + Docs + Tasks
# ─────────────────────────────────────────────────────
class MeetingActionItem(BaseModel):
    assignee: str = Field(description="Nom de la personne responsable (ex: 'Victor', 'Marc', 'Alice' ou 'Équipe').")
    task: str = Field(description="Description claire et précise de la tâche.")
    due_date: str = Field(default="", description="Date d'échéance au format YYYY-MM-DD si mentionnée, sinon vide ''.")

class MeetingNotes(BaseModel):
    title: str = Field(description="Titre officiel de la réunion ou du cours.")
    participants: list[str] = Field(description="Liste des participants identifiés dans l'audio.")
    executive_summary: str = Field(description="Résumé exécutif clair et synthétique en 3 à 5 phrases.")
    key_points: list[str] = Field(description="Points clés et sujets abordés lors de la réunion ou du cours.")
    decisions: list[str] = Field(description="Décisions formelles actées ou notions clés à retenir.")
    action_items: list[MeetingActionItem] = Field(description="Liste des actions concrètes à mener issues de la réunion.")
    full_transcript: str = Field(description="Transcription intégrale et détaillée de l'ensemble de la discussion ou du cours.")

def process_meeting_audio(creds, audio_file_path, meeting_title=None, create_doc=True, **kwargs):
    if not os.path.exists(audio_file_path):
        print(f"❌ Erreur : Le fichier audio '{audio_file_path}' n'existe pas.")
        return None

    client = get_client()
    if not client:
        return None

    console = Console()
    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    print(f"\n⏳ [1/3] Envoi du fichier audio à Google Gemini ({file_size_mb:.2f} Mo)...")

    try:
        audio_file = client.files.upload(file=audio_file_path)
    except Exception as e:
        print(f"❌ Erreur lors de l'upload de l'audio : {e}")
        return None

    print(f"🧠 [2/3] Analyse et écoute de la réunion par Gemini ({DEFAULT_MODEL})...")
    prompt_text = (
        "Tu es un assistant exécutif et pédagogique expert. Analyse attentivement cet enregistrement audio en français.\n"
        "1. Identifie tous les participants / intervenants qui s'expriment.\n"
        "2. Rédige un résumé exécutif clair et percutant.\n"
        "3. Liste les points clés abordés et les débats/explications importants.\n"
        "4. Isole toutes les décisions fermes prises ou conclusions à retenir.\n"
        "5. Extrais chaque action/tâche concrète avec son responsable et son échéance si elle est mentionnée.\n"
        "6. Rédige la TRANSCRIPTION INTÉGRALE de l'ensemble de la discussion ou du cours de façon exhaustive et chronologique."
    )
    if meeting_title:
        prompt_text += f"\nTitre suggéré pour la réunion : '{meeting_title}'."

    try:
        config = types.GenerateContentConfig(
            response_mime_type='application/json',
            response_json_schema=MeetingNotes.model_json_schema()
        )
        response = generate_content_with_retry(
            client=client,
            contents=[audio_file, prompt_text],
            config=config,
            model=DEFAULT_MODEL
        )
        _log_and_display_usage(response)
        notes_data = json.loads(response.text)
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse Gemini : {e}")
        return None

    title = notes_data.get("title") or meeting_title or "Compte-Rendu de Réunion"
    participants = notes_data.get("participants", [])
    summary = notes_data.get("executive_summary", "")
    key_points = notes_data.get("key_points", [])
    decisions = notes_data.get("decisions", [])
    actions = notes_data.get("action_items", [])
    full_transcript = notes_data.get("full_transcript", "")

    console.print(f"\n[bold cyan]✨ Fiche de Réunion : {title}[/bold cyan]")
    if participants:
        console.print(f"[dim]👥 Participants : {', '.join(participants)}[/dim]")
    console.print(Panel(summary, title="📌 Résumé Exécutif", border_style="cyan"))

    doc_id = None
    if create_doc:
        print("📄 [3/3] Création du compte-rendu Google Docs avec transcription...")
        try:
            today_str = datetime.datetime.now().strftime("%d/%m/%Y")
            doc_title = f"📄 Compte-Rendu : {title} - {today_str}"

            body_parts = [
                f"{doc_title}\n",
                f"Date : {today_str}\n",
                f"Participants : {', '.join(participants) if participants else 'Non spécifiés'}\n",
                "\n" + "="*50 + "\n",
                "\n1. RÉSUMÉ EXÉCUTIF\n",
                summary + "\n",
                "\n2. POINTS CLÉS & DÉBATS\n"
            ]
            for p in key_points:
                body_parts.append(f"• {p}\n")

            body_parts.append("\n3. DÉCISIONS ACTÉES\n")
            for d in decisions:
                body_parts.append(f"✔ {d}\n")

            body_parts.append("\n4. PLAN D'ACTIONS\n")
            for a in actions:
                assignee = a.get("assignee", "Équipe")
                task = a.get("task", "")
                due = a.get("due_date", "")
                due_info = f" (Échéance: {due})" if due else ""
                body_parts.append(f"☐ [{assignee}] {task}{due_info}\n")

            if full_transcript:
                body_parts.append("\n5. TRANSCRIPTION INTÉGRALE DE LA DISCUSSION\n")
                body_parts.append(full_transcript + "\n")

            full_text = "".join(body_parts)

            docs_service = assistant_docs.get_service(creds)
            doc = docs_service.documents().create(body={'title': doc_title}).execute()
            doc_id = doc.get('documentId')

            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': [{'insertText': {'location': {'index': 1}, 'text': full_text}}]}
            ).execute()

            console.print(f"✅ [bold green]Google Doc créé :[/bold green] https://docs.google.com/document/d/{doc_id}/edit")

        except Exception as e:
            print(f"⚠️ Erreur lors de la création du document : {e}")

    console.print("\n[bold magenta]🎉 Synthèse de réunion terminée avec succès ![/bold magenta]\n")
    return {
        "doc_id": doc_id,
        "title": title,
        "notes": notes_data
    }
