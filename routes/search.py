from flask import Blueprint, jsonify, render_template, request
from modules.db_operations import db_search_by_terms
from routes.auth import login_required
from flask import current_app as app
from typing import Any, List, Dict

search_bp = Blueprint('search', __name__)

@search_bp.route("/search", methods=["GET", "POST"])
@login_required
def search() -> Any:
    """
    Handles search requests. 
    In GET requests, it renders the search page.
    In POST requests, it performs a search based on the provided terms and returns the results as JSON.
    
    Returns:
        Response: Rendered template (GET) or JSON with search results (POST).
    """
    if request.method == "GET":
        return render_template("search.html")
    else:
        search_terms = request.form.get("search")
        results = db_search_by_terms(app, search_terms)
        results_list: List[Dict[str, Any]] = [dict(row._mapping) for row in results]
        return jsonify(results_list)