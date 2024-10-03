from flask import Blueprint, render_template, jsonify, request
from threading import Thread
from flask_socketio import emit
from modules.db_operations import db_process_and_insert_data, get_db_length
from modules.utils import count_new_resumes
from routes.auth import login_required
from flask import current_app as app
from typing import Any, Dict

db_bp = Blueprint('db', __name__)

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
        def run_db_process_and_insert_data() -> None:
            """
            Runs the database insertion process in a separate thread.
            Emits socket events to update the client on the status.
            """
            try:
                db_process_and_insert_data(app, emit)
                emit("status_done", {"status": "Processing complete. Restarting the page!"})
            except Exception as e:
                print(e)
                emit("status_error", {"status": f"Error processing new data: {str(e)}"})

        Thread(target=run_db_process_and_insert_data).start()
        return jsonify({"status": "Processing started!"})