from flask import Blueprint, jsonify, request, session

mode_bp = Blueprint('mode', __name__)

@mode_bp.route("/set_dark_mode", methods=["POST"])
def set_dark_mode():
    data = request.json
    dark_mode = data.get("dark_mode")
    if dark_mode is not None:
        session["color_mode"] = "dark" if dark_mode else "light"
        return jsonify({"status": "success", "mode": session["color_mode"]})
    return jsonify({"status": "error"}), 400
