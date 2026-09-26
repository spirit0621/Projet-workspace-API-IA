import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    import auth
    from services import (
        assistant_drive,
        assistant_docs,
        assistant_sheets,
        assistant_slides,
        assistant_calendar,
        assistant_tasks,
        assistant_forms,
        assistant_notebook,
        assistant_ai,
        secrets_manager,
    )
except ImportError:
    from src import auth
    from src.services import (
        assistant_drive,
        assistant_docs,
        assistant_sheets,
        assistant_slides,
        assistant_calendar,
        assistant_tasks,
        assistant_forms,
        assistant_notebook,
        assistant_ai,
        secrets_manager,
    )

load_dotenv()
if (root_dir / ".env").exists():
    load_dotenv(dotenv_path=root_dir / ".env")
secrets_manager.load_gemini_api_key()

app = FastAPI(
    title="Google Workspace & Gemini Hub API",
    description="API REST centralisée pour piloter l'écosystème Google Workspace (Drive, Docs, Sheets, Slides, Calendar, Tasks, Forms) et Gemini AI depuis n'importe quel projet.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_creds():
    try:
        creds = auth.get_credentials()
        if not creds:
            raise HTTPException(
                status_code=401,
                detail="Identifiants Google non trouvés. Veuillez exécuter auth.py pour générer token.json."
            )
        return creds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'authentification : {str(e)}")

# Drive
class DriveCreateFolderReq(BaseModel):
    title: str
    parent_id: Optional[str] = None

class DriveShareReq(BaseModel):
    file_id: str
    email: str
    role: str = Field(default="reader", pattern="^(reader|writer|commenter)$")

# Calendar
class CalendarEventReq(BaseModel):
    summary: str
    start_time: str = Field(..., description="Format RFC3339 ex: 2026-09-27T10:00:00")
    end_time: str = Field(..., description="Format RFC3339 ex: 2026-09-27T11:00:00")
    emails: Optional[str] = None
    timezone: str = "Europe/Paris"

class CalendarReminderReq(BaseModel):
    minutes: int

# Docs
class DocsAppendReq(BaseModel):
    text: str

class DocsReplaceReq(BaseModel):
    old_text: str
    new_text: str

class DocsFormatBoldReq(BaseModel):
    text: str

class DocsTemplateReq(BaseModel):
    template_id: str
    title: str
    variables: Dict[str, Any]

# Sheets
class SheetsAddSheetReq(BaseModel):
    title: str

class SheetsFormulaReq(BaseModel):
    cell_range: str
    formula: str

class SheetsFormatGreenReq(BaseModel):
    cell_range: str

# Slides
class SlidesCreateReq(BaseModel):
    title: str

class SlidesCloneReq(BaseModel):
    slide_id: str

class SlidesReplaceVariablesReq(BaseModel):
    variable: str
    valeur: str

class SlidesTextboxReq(BaseModel):
    page_id: str
    text: str

# Tasks
class TasksCreateListReq(BaseModel):
    title: str

class TasksCreateTaskReq(BaseModel):
    title: str
    due: Optional[str] = Field(None, description="Format YYYY-MM-DD")
    parent_id: Optional[str] = None

# Forms
class FormsCreateReq(BaseModel):
    title: str

class FormsAddQuestionReq(BaseModel):
    question_title: str
    question_type: str = "TEXT"
    options: Optional[str] = None

# AI
class AIAskSheetReq(BaseModel):
    sheet_id: str
    question: str

class AISummarizeDocReq(BaseModel):
    doc_id: str

class AIGenerateDocReq(BaseModel):
    doc_id: str
    prompt: str

class AIGenerateSlidesReq(BaseModel):
    topic: str
    num_slides: int = 5

class AIParseEventReq(BaseModel):
    prompt: str

@app.get("/health", tags=["Système"])
def health_check():
    token_present = (
        os.path.exists("token.json")
        or (root_dir / "token.json").exists()
        or (os.getenv("GOOGLE_OAUTH_TOKEN_JSON") is not None)
    )
    gemini_key_present = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "ok",
        "service": "Google Workspace & Gemini Hub API",
        "google_auth_ready": token_present,
        "gemini_api_key_configured": gemini_key_present
    }

# 1. GOOGLE DRIVE
@app.get("/api/drive/search", tags=["Google Drive"])
def search_drive_files(query: str = Query(..., description="Terme de recherche"), creds=Depends(get_creds)):
    files = assistant_drive.search_files(creds, query)
    return {"query": query, "count": len(files), "files": files}

@app.post("/api/drive/create-folder", tags=["Google Drive"])
def create_drive_folder(body: DriveCreateFolderReq, creds=Depends(get_creds)):
    folder_id = assistant_drive.create_folder(creds, body.title, body.parent_id)
    return {"status": "ok", "title": body.title, "folder_id": folder_id}

@app.post("/api/drive/share", tags=["Google Drive"])
def share_drive_file(body: DriveShareReq, creds=Depends(get_creds)):
    assistant_drive.share(creds, body.file_id, body.email, body.role)
    return {"status": "ok", "file_id": body.file_id, "shared_with": body.email, "role": body.role}

@app.post("/api/drive/empty-trash", tags=["Google Drive"])
def empty_drive_trash(creds=Depends(get_creds)):
    assistant_drive.empty_trash(creds)
    return {"status": "ok", "message": "Corbeille vidée avec succès."}

@app.post("/api/drive/upload", tags=["Google Drive"])
async def upload_file_to_drive(file: UploadFile = File(...), creds=Depends(get_creds)):
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        assistant_drive.upload_file(creds, temp_path)
        return {"status": "ok", "filename": file.filename}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# 2. GOOGLE CALENDAR
@app.get("/api/calendar/events", tags=["Google Calendar"])
def list_calendar_events(max_results: int = 10, creds=Depends(get_creds)):
    events = assistant_calendar.list_events(creds, max_results=max_results)
    return {"count": len(events), "events": events}

@app.post("/api/calendar/events", tags=["Google Calendar"])
def create_calendar_event(body: CalendarEventReq, creds=Depends(get_creds)):
    created = assistant_calendar.create_event(
        creds,
        summary=body.summary,
        start_time=body.start_time,
        end_time=body.end_time,
        emails=body.emails,
        timezone=body.timezone
    )
    return {"status": "ok", "event": created}

@app.delete("/api/calendar/events/{event_id}", tags=["Google Calendar"])
def delete_calendar_event(event_id: str, creds=Depends(get_creds)):
    assistant_calendar.delete_event(creds, event_id)
    return {"status": "ok", "event_id": event_id, "message": "Événement supprimé."}

@app.post("/api/calendar/events/{event_id}/reminder", tags=["Google Calendar"])
def add_calendar_reminder(event_id: str, body: CalendarReminderReq, creds=Depends(get_creds)):
    updated = assistant_calendar.add_reminder(creds, event_id, body.minutes)
    return {"status": "ok", "event_id": event_id, "minutes": body.minutes}

# 3. GOOGLE DOCS
@app.get("/api/docs/{doc_id}", tags=["Google Docs"])
def get_doc_content(doc_id: str, creds=Depends(get_creds)):
    content = assistant_docs.read_content(creds, doc_id, return_text=True)
    return {"doc_id": doc_id, "content": content}

@app.post("/api/docs/{doc_id}/append", tags=["Google Docs"])
def append_to_doc(doc_id: str, body: DocsAppendReq, creds=Depends(get_creds)):
    assistant_docs.append_text(creds, doc_id, body.text)
    return {"status": "ok", "doc_id": doc_id}

@app.post("/api/docs/{doc_id}/replace", tags=["Google Docs"])
def replace_doc_text(doc_id: str, body: DocsReplaceReq, creds=Depends(get_creds)):
    assistant_docs.replace_text(creds, doc_id, body.old_text, body.new_text)
    return {"status": "ok", "doc_id": doc_id, "replaced": body.old_text, "with": body.new_text}

@app.post("/api/docs/{doc_id}/format-bold", tags=["Google Docs"])
def format_doc_bold(doc_id: str, body: DocsFormatBoldReq, creds=Depends(get_creds)):
    assistant_docs.format_bold(creds, doc_id, body.text)
    return {"status": "ok", "doc_id": doc_id}

@app.post("/api/docs/create-from-template", tags=["Google Docs"])
def create_doc_from_template(body: DocsTemplateReq, creds=Depends(get_creds)):
    new_doc_id = assistant_docs.create_from_template(
        creds, body.template_id, body.title, json.dumps(body.variables)
    )
    return {"status": "ok", "new_doc_id": new_doc_id, "title": body.title}

# 4. GOOGLE SHEETS
@app.get("/api/sheets/{sheet_id}/range", tags=["Google Sheets"])
def read_sheet_range(sheet_id: str, range_name: str = Query("A1:Z100"), creds=Depends(get_creds)):
    data = assistant_sheets.read_range(creds, sheet_id, range_name, return_data=True)
    return {"sheet_id": sheet_id, "range": range_name, "values": data}

@app.post("/api/sheets/{sheet_id}/add-sheet", tags=["Google Sheets"])
def add_new_sheet(sheet_id: str, body: SheetsAddSheetReq, creds=Depends(get_creds)):
    assistant_sheets.add_sheet(creds, sheet_id, body.title)
    return {"status": "ok", "sheet_id": sheet_id, "title": body.title}

@app.post("/api/sheets/{sheet_id}/formula", tags=["Google Sheets"])
def add_sheet_formula(sheet_id: str, body: SheetsFormulaReq, creds=Depends(get_creds)):
    assistant_sheets.add_formula(creds, sheet_id, body.cell_range, body.formula)
    return {"status": "ok", "sheet_id": sheet_id, "cell_range": body.cell_range, "formula": body.formula}

@app.post("/api/sheets/{sheet_id}/format-green", tags=["Google Sheets"])
def format_sheet_green(sheet_id: str, body: SheetsFormatGreenReq, creds=Depends(get_creds)):
    assistant_sheets.format_green(creds, sheet_id, body.cell_range)
    return {"status": "ok", "sheet_id": sheet_id, "cell_range": body.cell_range}

# 5. GOOGLE SLIDES
@app.post("/api/slides/create", tags=["Google Slides"])
def create_presentation(body: SlidesCreateReq, creds=Depends(get_creds)):
    assistant_slides.create_presentation(creds, body.title)
    return {"status": "ok", "title": body.title}

@app.post("/api/slides/{presentation_id}/clone-slide", tags=["Google Slides"])
def clone_slide(presentation_id: str, body: SlidesCloneReq, creds=Depends(get_creds)):
    assistant_slides.clone_slide(creds, presentation_id, body.slide_id)
    return {"status": "ok", "presentation_id": presentation_id, "slide_id": body.slide_id}

@app.post("/api/slides/{presentation_id}/replace-variables", tags=["Google Slides"])
def replace_slides_variables(presentation_id: str, body: SlidesReplaceVariablesReq, creds=Depends(get_creds)):
    assistant_slides.replace_variables(creds, presentation_id, body.variable, body.valeur)
    return {"status": "ok", "presentation_id": presentation_id, "variable": body.variable}

@app.post("/api/slides/{presentation_id}/textbox", tags=["Google Slides"])
def insert_slide_textbox(presentation_id: str, body: SlidesTextboxReq, creds=Depends(get_creds)):
    assistant_slides.insert_textbox(creds, presentation_id, body.page_id, body.text)
    return {"status": "ok", "presentation_id": presentation_id, "page_id": body.page_id}

# 6. GOOGLE TASKS
@app.post("/api/tasks/lists", tags=["Google Tasks"])
def create_task_list(body: TasksCreateListReq, creds=Depends(get_creds)):
    assistant_tasks.create_list(creds, body.title)
    return {"status": "ok", "title": body.title}

@app.get("/api/tasks/{list_id}/pending", tags=["Google Tasks"])
def list_pending_tasks(list_id: str, creds=Depends(get_creds)):
    tasks = assistant_tasks.list_pending(creds, list_id)
    return {"list_id": list_id, "count": len(tasks), "tasks": tasks}

@app.post("/api/tasks/{list_id}/tasks", tags=["Google Tasks"])
def add_task(list_id: str, body: TasksCreateTaskReq, creds=Depends(get_creds)):
    assistant_tasks.add_task(creds, list_id, body.title, body.parent_id, body.due)
    return {"status": "ok", "list_id": list_id, "title": body.title}

@app.post("/api/tasks/{list_id}/tasks/{task_id}/complete", tags=["Google Tasks"])
def complete_task(list_id: str, task_id: str, creds=Depends(get_creds)):
    assistant_tasks.complete_task(creds, list_id, task_id)
    return {"status": "ok", "list_id": list_id, "task_id": task_id}

@app.post("/api/tasks/{list_id}/clear-completed", tags=["Google Tasks"])
def clear_completed_tasks(list_id: str, creds=Depends(get_creds)):
    assistant_tasks.clear_completed(creds, list_id)
    return {"status": "ok", "list_id": list_id}

# 7. GOOGLE FORMS
@app.post("/api/forms", tags=["Google Forms"])
def create_form(body: FormsCreateReq, creds=Depends(get_creds)):
    result = assistant_forms.create_form(creds, body.title)
    return {"status": "ok", "result": result}

@app.get("/api/forms/{form_id}/responses", tags=["Google Forms"])
def get_form_responses(form_id: str, creds=Depends(get_creds)):
    responses = assistant_forms.get_responses(creds, form_id)
    return {"form_id": form_id, "count": len(responses), "responses": responses}

@app.post("/api/forms/{form_id}/questions", tags=["Google Forms"])
def add_form_question(form_id: str, body: FormsAddQuestionReq, creds=Depends(get_creds)):
    assistant_forms.add_question(creds, form_id, body.question_title, body.question_type, body.options)
    return {"status": "ok", "form_id": form_id, "question": body.question_title}

@app.post("/api/forms/{form_id}/close", tags=["Google Forms"])
def close_form(form_id: str, creds=Depends(get_creds)):
    assistant_forms.close_form(creds, form_id)
    return {"status": "ok", "form_id": form_id, "closed": True}

# 8. GEMINI AI
@app.get("/api/ai/stats", tags=["Gemini AI"])
def get_ai_stats():
    stats = assistant_ai.stats()
    return {"status": "ok", "stats": stats}

@app.post("/api/ai/ask-sheet", tags=["Gemini AI"])
def ask_sheet_with_ai(body: AIAskSheetReq, creds=Depends(get_creds)):
    answer = assistant_ai.ask_sheet(creds, body.sheet_id, body.question)
    return {"sheet_id": body.sheet_id, "question": body.question, "answer": answer}

@app.post("/api/ai/summarize-doc", tags=["Gemini AI"])
def summarize_doc_with_ai(body: AISummarizeDocReq, creds=Depends(get_creds)):
    summary = assistant_ai.summarize(creds, body.doc_id)
    return {"doc_id": body.doc_id, "summary": summary}

@app.post("/api/ai/generate-doc", tags=["Gemini AI"])
def generate_doc_with_ai(body: AIGenerateDocReq, creds=Depends(get_creds)):
    assistant_ai.generate_doc(creds, body.doc_id, body.prompt)
    return {"status": "ok", "doc_id": body.doc_id, "prompt": body.prompt}

@app.post("/api/ai/generate-slides", tags=["Gemini AI"])
def generate_slides_with_ai(body: AIGenerateSlidesReq, creds=Depends(get_creds)):
    assistant_ai.generate_slides(creds, body.topic, body.num_slides)
    return {"status": "ok", "topic": body.topic, "num_slides": body.num_slides}

@app.post("/api/ai/parse-event", tags=["Gemini AI"])
def parse_and_create_event_ai(body: AIParseEventReq, creds=Depends(get_creds)):
    result = assistant_ai.parse_event(creds, body.prompt)
    return {"status": "ok", "result": result}

@app.post("/api/ai/meeting-audio", tags=["Gemini AI"])
async def process_audio_meeting(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    creds=Depends(get_creds)
):
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result = assistant_ai.process_meeting_audio(creds, temp_path, meeting_title=title)
        return {"status": "ok", "result": result}
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
