from flask import Blueprint, render_template
from routes.auth import login_required
from typing import Any

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
@login_required
def home() -> Any:
    """
    Renders the home page for logged-in users.
    
    Returns:
        Response: Rendered home page template.
    """
    return render_template("home.html")
