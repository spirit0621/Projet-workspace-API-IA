import argparse
import sys
import auth

# Import the service modules from the services directory
from services import assistant_drive
from services import assistant_docs
from services import assistant_sheets
from services import assistant_slides
from services import assistant_calendar
from services import assistant_tasks
from services import assistant_forms
from services import assistant_notebook
from services import assistant_ai
from services import assistant_recorder
from services import secrets_manager
from dotenv import load_dotenv

# Charge les variables d'environnement (ex: GEMINI_API_KEY) depuis le fichier .env ou Secret Manager
load_dotenv()
secrets_manager.load_gemini_api_key()

def main():
    parser = argparse.ArgumentParser(description="L'Assistant Ultime Google Workspace")
    subparsers = parser.add_subparsers(dest='service', help='Service Google à cibler')

    # ========== DRIVE ==========
    drive_p = subparsers.add_parser('drive')
    drive_sub = drive_p.add_subparsers(dest='action')
    # Les anciennes commandes
    drive_sub.add_parser('search').add_argument('query')
    # Nouvelles commandes
    drive_sub.add_parser('empty_trash')
    rev_p = drive_sub.add_parser('restore_version')
    rev_p.add_argument('id')
    rev_p.add_argument('revision_id')
    cf_p = drive_sub.add_parser('create_folder')
    cf_p.add_argument('title')
    cf_p.add_argument('--parent', dest='parent_id', default=None)
    dl_p = drive_sub.add_parser('download')
    dl_p.add_argument('file_id')
    ul_p = drive_sub.add_parser('upload')
    ul_p.add_argument('file_path')
    share_p = drive_sub.add_parser('share')
    share_p.add_argument('file_id')
    share_p.add_argument('--email', required=True)
    share_p.add_argument('--role', choices=['reader', 'writer', 'commenter'], default='reader')
    lf_p = drive_sub.add_parser('list_folder')
    lf_p.add_argument('folder_id')

    # ========== DOCS ==========
    docs_p = subparsers.add_parser('docs')
    docs_sub = docs_p.add_subparsers(dest='action')
    docs_sub.add_parser('extract_structure').add_argument('id')
    docs_sub.add_parser('list_comments').add_argument('id')
    fb_p = docs_sub.add_parser('format_bold')
    fb_p.add_argument('id')
    fb_p.add_argument('text')
    ii_p = docs_sub.add_parser('insert_image')
    ii_p.add_argument('id')
    ii_p.add_argument('url')
    rt_p = docs_sub.add_parser('replace_text')
    rt_p.add_argument('id')
    rt_p.add_argument('old_text')
    rt_p.add_argument('new_text')
    ep_p = docs_sub.add_parser('export_pdf')
    ep_p.add_argument('id')
    ep_p.add_argument('output_filename')
    docs_sub.add_parser('read').add_argument('id')
    ew_p = docs_sub.add_parser('export_docx')
    ew_p.add_argument('id')
    ew_p.add_argument('output_filename')
    at_docs = docs_sub.add_parser('append_text')
    at_docs.add_argument('id')
    at_docs.add_argument('text')
    cft_docs = docs_sub.add_parser('create_from_template')
    cft_docs.add_argument('template_id')
    cft_docs.add_argument('title')
    cft_docs.add_argument('variables_json')

    # ========== SHEETS ==========
    sheets_p = subparsers.add_parser('sheets')
    sheets_sub = sheets_p.add_subparsers(dest='action')
    ash_p = sheets_sub.add_parser('add_sheet')
    ash_p.add_argument('id')
    ash_p.add_argument('title')
    fg_p = sheets_sub.add_parser('format_green')
    fg_p.add_argument('id')
    fg_p.add_argument('cell_range')
    af_p = sheets_sub.add_parser('add_formula')
    af_p.add_argument('id')
    af_p.add_argument('cell_range')
    af_p.add_argument('formula')
    rr_p = sheets_sub.add_parser('read_range')
    rr_p.add_argument('id')
    rr_p.add_argument('range_name')
    ac_p = sheets_sub.add_parser('add_chart')
    ac_p.add_argument('id')
    ac_p.add_argument('tab_id')
    afi_p = sheets_sub.add_parser('add_filter')
    afi_p.add_argument('id')
    afi_p.add_argument('tab_id')
    exp_p = sheets_sub.add_parser('export_pdf')
    exp_p.add_argument('id')
    exp_p.add_argument('tab_id')
    exp_p.add_argument('filename')

    # ========== SLIDES ==========
    slides_p = subparsers.add_parser('slides')
    slides_sub = slides_p.add_subparsers(dest='action')
    cs_p = slides_sub.add_parser('clone_slide')
    cs_p.add_argument('presentation_id')
    cs_p.add_argument('slide_id')
    rv_p = slides_sub.add_parser('replace_variables')
    rv_p.add_argument('presentation_id')
    rv_p.add_argument('variable')
    rv_p.add_argument('valeur')
    es_p = slides_sub.add_parser('export_slide')
    es_p.add_argument('presentation_id')
    es_p.add_argument('slide_id')
    es_p.add_argument('output_filename')
    ep_slides = slides_sub.add_parser('export_pdf')
    ep_slides.add_argument('presentation_id')
    ep_slides.add_argument('output_filename')
    it_p = slides_sub.add_parser('insert_textbox')
    it_p.add_argument('presentation_id')
    it_p.add_argument('page_id')
    it_p.add_argument('text')
    cp_p = slides_sub.add_parser('create_presentation')
    cp_p.add_argument('title')
    mg_p = slides_sub.add_parser('mass_generate')
    mg_p.add_argument('id')
    mg_p.add_argument('slide_id')
    mg_p.add_argument('csv_path')
    it_p = slides_sub.add_parser('insert_table')
    it_p.add_argument('presentation_id')
    it_p.add_argument('page_id')
    it_p.add_argument('rows', type=int)
    it_p.add_argument('cols', type=int)

    # ========== CALENDAR ==========
    cal_p = subparsers.add_parser('calendar')
    cal_sub = cal_p.add_subparsers(dest='action')
    ar_p = cal_sub.add_parser('add_reminder')
    ar_p.add_argument('event_id')
    ar_p.add_argument('minutes')
    rsvp_p = cal_sub.add_parser('rsvp')
    rsvp_p.add_argument('event_id')
    rsvp_p.add_argument('response')
    le_p = cal_sub.add_parser('list_events')
    le_p.add_argument('--max', default=10, type=int, help='Nombre max d\'événements (défaut: 10)')
    ce_p = cal_sub.add_parser('create_event')
    ce_p.add_argument('summary')
    ce_p.add_argument('start_time')
    ce_p.add_argument('end_time')
    ce_p.add_argument('--emails', default=None)
    ce_p.add_argument('--timezone', default='Europe/Paris', help='Fuseau horaire (défaut: Europe/Paris)')
    de_p = cal_sub.add_parser('delete_event')
    de_p.add_argument('event_id')

    # ========== TASKS ==========
    tasks_p = subparsers.add_parser('tasks')
    tasks_sub = tasks_p.add_subparsers(dest='action')
    cl_p = tasks_sub.add_parser('create_list')
    cl_p.add_argument('title')
    cc_p = tasks_sub.add_parser('clear_completed')
    cc_p.add_argument('list_id')
    at_p = tasks_sub.add_parser('add_task')
    at_p.add_argument('list_id')
    at_p.add_argument('title')
    at_p.add_argument('--parent', dest='parent_id', default=None)
    at_p.add_argument('--due', dest='due', default=None, help="Date d'échéance au format YYYY-MM-DD")
    ct_p = tasks_sub.add_parser('complete_task')
    ct_p.add_argument('list_id')
    ct_p.add_argument('task_id')
    lp_p = tasks_sub.add_parser('list_pending')
    lp_p.add_argument('list_id')

    # ========== FORMS ==========
    forms_p = subparsers.add_parser('forms')
    forms_sub = forms_p.add_subparsers(dest='action')
    fc_p = forms_sub.add_parser('create')
    fc_p.add_argument('title')
    fr_p = forms_sub.add_parser('get_responses')
    fr_p.add_argument('form_id')
    aq_p = forms_sub.add_parser('add_question')
    aq_p.add_argument('form_id')
    aq_p.add_argument('question_title')
    aq_p.add_argument('--type', dest='question_type', default='TEXT', help="Type of question (e.g., TEXT, RADIO, CHECKBOX)")
    er_p = forms_sub.add_parser('export_responses')
    er_p.add_argument('form_id')
    er_p.add_argument('output_csv')
    cfrm_p = forms_sub.add_parser('close_form')
    cfrm_p.add_argument('form_id')
    ai_p = forms_sub.add_parser('add_image')
    ai_p.add_argument('form_id')
    ai_p.add_argument('image_url')
    acq_p = forms_sub.add_parser('add_conditional_question')
    acq_p.add_argument('form_id')
    acq_p.add_argument('question_title')
    acq_p.add_argument('json_config', help='JSON with choices and goto_section mappings')

    # ========== NOTEBOOK ==========
    notebook_p = subparsers.add_parser('notebook')
    notebook_sub = notebook_p.add_subparsers(dest='action')
    nc_p = notebook_sub.add_parser('create')
    nc_p.add_argument('title')
    nl_p = notebook_sub.add_parser('list')

    # ========== AI ==========
    ai_main_p = subparsers.add_parser('ai')
    ai_sub = ai_main_p.add_subparsers(dest='action')
    
    sum_p = ai_sub.add_parser('summarize')
    sum_p.add_argument('doc_id')
    
    pe_p = ai_sub.add_parser('parse_event')
    pe_p.add_argument('prompt')

    as_p = ai_sub.add_parser('ask_sheet')
    as_p.add_argument('sheet_id')
    as_p.add_argument('question')

    pr_p = ai_sub.add_parser('proofread')
    pr_p.add_argument('doc_id')

    gs_p = ai_sub.add_parser('generate_slides')
    gs_p.add_argument('topic')
    gs_p.add_argument('--num_slides', type=int, default=5)

    gd_p = ai_sub.add_parser('generate_doc')
    gd_p.add_argument('doc_id')
    gd_p.add_argument('prompt')
    
    cs_ai_p = ai_sub.add_parser('classify_sheet')
    cs_ai_p.add_argument('sheet_id')
    cs_ai_p.add_argument('read_range')
    cs_ai_p.add_argument('write_range')
    cs_ai_p.add_argument('categories')
    
    ec_ai_p = ai_sub.add_parser('estimate_cost')
    ec_ai_p.add_argument('doc_id')
    
    ai_sub.add_parser('stats')

    ma_p = ai_sub.add_parser('meeting_audio', help="Génère un compte-rendu Google Docs depuis un fichier audio")
    ma_p.add_argument('audio_file', help="Chemin vers le fichier audio (.wav, .mp3, .m4a)")
    ma_p.add_argument('--title', default=None, help="Titre de la réunion")

    # ========== RECORD (Audio & Réunions) ==========
    rec_p = subparsers.add_parser('record', help="Enregistrement audio et synthèse de réunions")
    rec_sub = rec_p.add_subparsers(dest='action')
    
    rl_p = rec_sub.add_parser('live', help="Enregistre la réunion en direct (Entrée pour stopper)")
    rl_p.add_argument('--title', default="Point Réunion", help="Titre de la réunion")
    
    rs_p = rec_sub.add_parser('start', help="Démarre un enregistrement en tâche de fond")
    rs_p.add_argument('--title', default="Point Réunion", help="Titre de la réunion")
    
    stop_p = rec_sub.add_parser('stop', help="Arrête l'enregistrement et génère le compte-rendu Google Docs")
    
    rp_p = rec_sub.add_parser('process', help="Traite un fichier audio existant")
    rp_p.add_argument('audio_file', help="Chemin vers le fichier audio (.wav, .mp3, .m4a)")
    rp_p.add_argument('--title', default=None, help="Titre de la réunion")

    args = parser.parse_args()

    if not args.service or not args.action:
        parser.print_help()
        sys.exit(1)

    print("Authentification en cours...")
    creds = auth.get_credentials()

    try:
        if args.service == 'drive':
            if args.action == 'search': assistant_drive.search_files(creds, args.query)
            elif args.action == 'empty_trash': assistant_drive.empty_trash(creds)
            elif args.action == 'restore_version': assistant_drive.restore_version(creds, args.id, args.revision_id)
            elif args.action == 'create_folder': assistant_drive.create_folder(creds, args.title, args.parent_id)
            elif args.action == 'download': assistant_drive.download_file(creds, args.file_id)
            elif args.action == 'upload': assistant_drive.upload_file(creds, args.file_path)
            elif args.action == 'share': assistant_drive.share(creds, args.file_id, args.email, args.role)
            elif args.action == 'list_folder': assistant_drive.list_folder(creds, args.folder_id)
        
        elif args.service == 'docs':
            if args.action == 'extract_structure': assistant_docs.extract_structure(creds, args.id)
            elif args.action == 'list_comments': assistant_docs.list_comments(creds, args.id)
            elif args.action == 'format_bold': assistant_docs.format_bold(creds, args.id, args.text)
            elif args.action == 'insert_image': assistant_docs.insert_image(creds, args.id, args.url)
            elif args.action == 'replace_text': assistant_docs.replace_text(creds, args.id, args.old_text, args.new_text)
            elif args.action == 'export_pdf': assistant_docs.export_pdf(creds, args.id, args.output_filename)
            elif args.action == 'read': assistant_docs.read_content(creds, args.id)
            elif args.action == 'export_docx': assistant_docs.export_word(creds, args.id, args.output_filename)
            elif args.action == 'append_text': assistant_docs.append_text(creds, args.id, args.text)
            elif args.action == 'create_from_template': assistant_docs.create_from_template(creds, args.template_id, args.title, args.variables_json)
            
        elif args.service == 'sheets':
            if args.action == 'add_sheet': assistant_sheets.add_sheet(creds, args.id, args.title)
            elif args.action == 'format_green': assistant_sheets.format_green(creds, args.id, args.cell_range)
            elif args.action == 'add_formula': assistant_sheets.add_formula(creds, args.id, args.cell_range, args.formula)
            elif args.action == 'read_range': assistant_sheets.read_range(creds, args.id, args.range_name)
            elif args.action == 'add_chart': assistant_sheets.add_chart(creds, args.id, args.tab_id)
            elif args.action == 'add_filter': assistant_sheets.add_filter(creds, args.id, args.tab_id)
            elif args.action == 'export_pdf': assistant_sheets.export_pdf(creds, args.id, args.tab_id, args.filename)
            
        elif args.service == 'slides':
            if args.action == 'clone_slide': assistant_slides.clone_slide(creds, args.presentation_id, args.slide_id)
            elif args.action == 'replace_variables': assistant_slides.replace_variables(creds, args.presentation_id, args.variable, args.valeur)
            elif args.action == 'export_slide': assistant_slides.export_slide(creds, args.presentation_id, args.slide_id, args.output_filename)
            elif args.action == 'insert_textbox': assistant_slides.insert_textbox(creds, args.presentation_id, args.page_id, args.text)
            elif args.action == 'create_presentation': assistant_slides.create_presentation(creds, args.title)
            elif args.action == 'mass_generate': assistant_slides.mass_generate(creds, args.id, args.slide_id, args.csv_path)
            elif args.action == 'insert_table': assistant_slides.insert_table(creds, args.presentation_id, args.page_id, args.rows, args.cols)
            elif args.action == 'export_pdf': assistant_slides.export_pdf(creds, args.presentation_id, args.output_filename)
            
        elif args.service == 'calendar':
            if args.action == 'add_reminder': assistant_calendar.add_reminder(creds, args.event_id, args.minutes)
            elif args.action == 'rsvp': assistant_calendar.rsvp(creds, args.event_id, args.response)
            elif args.action == 'list_events': assistant_calendar.list_events(creds, args.max)
            elif args.action == 'create_event': assistant_calendar.create_event(creds, args.summary, args.start_time, args.end_time, args.emails, args.timezone)
            elif args.action == 'delete_event': assistant_calendar.delete_event(creds, args.event_id)
            
        elif args.service == 'tasks':
            if args.action == 'create_list': assistant_tasks.create_list(creds, args.title)
            elif args.action == 'clear_completed': assistant_tasks.clear_completed(creds, args.list_id)
            elif args.action == 'add_task': assistant_tasks.add_task(creds, args.list_id, args.title, args.parent_id, args.due)
            elif args.action == 'complete_task': assistant_tasks.complete_task(creds, args.list_id, args.task_id)
            elif args.action == 'list_pending': assistant_tasks.list_pending(creds, args.list_id)
            
        elif args.service == 'forms':
            if args.action == 'create': assistant_forms.create_form(creds, args.title)
            elif args.action == 'get_responses': assistant_forms.get_responses(creds, args.form_id)
            elif args.action == 'add_question': assistant_forms.add_question(creds, args.form_id, args.question_title, args.question_type)
            elif args.action == 'export_responses': assistant_forms.export_responses(creds, args.form_id, args.output_csv)
            elif args.action == 'close_form': assistant_forms.close_form(creds, args.form_id)
            elif args.action == 'add_image': assistant_forms.add_image(creds, args.form_id, args.image_url)
            elif args.action == 'add_conditional_question': assistant_forms.add_conditional_question(creds, args.form_id, args.question_title, args.json_config)
            
        elif args.service == 'notebook':
            if args.action == 'create': assistant_notebook.create_colab(creds, args.title)
            elif args.action == 'list': assistant_notebook.list_colabs(creds)
            
        elif args.service == 'ai':
            if args.action == 'summarize': assistant_ai.summarize(creds, args.doc_id)
            elif args.action == 'parse_event': assistant_ai.parse_event(creds, args.prompt)
            elif args.action == 'ask_sheet': assistant_ai.ask_sheet(creds, args.sheet_id, args.question)
            elif args.action == 'proofread': assistant_ai.proofread(creds, args.doc_id)
            elif args.action == 'generate_slides': assistant_ai.generate_slides(creds, args.topic, args.num_slides)
            elif args.action == 'generate_doc': assistant_ai.generate_doc(creds, args.doc_id, args.prompt)
            elif args.action == 'classify_sheet': assistant_ai.classify_sheet(creds, args.sheet_id, args.read_range, args.write_range, args.categories)
            elif args.action == 'estimate_cost': assistant_ai.estimate_cost(creds, args.doc_id)
            elif args.action == 'stats': assistant_ai.stats()
            elif args.action == 'meeting_audio':
                assistant_ai.process_meeting_audio(creds, args.audio_file, meeting_title=args.title)
            
        elif args.service == 'record':
            if args.action == 'live':
                audio_path = assistant_recorder.record_live_meeting(title=args.title)
                if audio_path:
                    assistant_ai.process_meeting_audio(creds, audio_path, meeting_title=args.title)
            elif args.action == 'start':
                assistant_recorder.start_background_recording(title=args.title)
            elif args.action == 'stop':
                audio_path, title = assistant_recorder.stop_background_recording()
                if audio_path:
                    assistant_ai.process_meeting_audio(creds, audio_path, meeting_title=title)
            elif args.action == 'process':
                assistant_ai.process_meeting_audio(creds, args.audio_file, meeting_title=args.title)
    except Exception as e:
        print(f"Une erreur est survenue pendant l'exécution : {e}")

if __name__ == '__main__':
    main()
