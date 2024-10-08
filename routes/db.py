from flask import Blueprint, render_template, jsonify, request, Response
from threading import Thread
from flask_socketio import emit
from modules.db_operations import db_process_and_insert_data, get_db_length
from modules.utils import count_new_resumes
from routes.auth import login_required
from flask import current_app as app, copy_current_request_context
from typing import Any, Dict
import time
import json

db_bp = Blueprint('db', __name__)

status_updates = []

@db_bp.route("/process_database", methods=["GET", "POST"])
@login_required
def process_database() -> Any:
    """
    Handles database processing operations. 
    In GET requests, it returns the count of records in the database and spreadsheet.
    In POST requests, it starts the processing of new database records in a separate thread.
    
    Returns:
        Response: Rendered template with database information (GET), or JSON status (POST).
    """
    if request.method == "GET":
        count_db = get_db_length(app)
        count_insert = count_new_resumes(table_path=app.config["EXCEL_FILE"])
        return render_template("process_database.html", count_db=count_db, count_insert=count_insert)

    elif request.method == "POST":

        @copy_current_request_context
        def run_db_process_and_insert_data() -> None:
            """
            Runs the database insertion process in a separate thread.
            Emits socket events to update the client on the status.
            """
            try:

                global status_updates
                status_updates.clear()
                
                with app.app_context():
                    db_process_and_insert_data(app, add_status_update)
                    add_status_update("status_done", "Processing complete. Restarting the page!")
            except Exception as e:
                print(e)
                add_status_update("status_error", f"Error processing new data: {str(e)}")

        Thread(target=run_db_process_and_insert_data).start()
        return jsonify({"status": "Processing started!"})
    
def add_status_update(event: str, message: str) -> None:
    status_updates.append({"event": event, "status": message})

@db_bp.route('/status_updates')
def status_stream():
    def generate():
        while True:
            if status_updates:
                update = status_updates.pop(0)
                yield f"data: {json.dumps(update)}\n\n"
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')