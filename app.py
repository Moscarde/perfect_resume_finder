from flask import Flask
from flask_socketio import SocketIO
from modules.load_configs import load_config
from routes.auth import auth_bp
from routes.db import db_bp
from routes.home import home_bp
from routes.search import search_bp
from routes.color_mode import mode_bp

def create_app() -> Flask:
    """
    Cria e configura a aplicação Flask.

    Returns:
        Flask: Instância da aplicação Flask.
    """
    app = Flask(__name__)
    app.secret_key = "secret_key"
    load_config(app)

    # Inicialização do SocketIO
    socketio = SocketIO(app)

    # Registro dos blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(db_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(mode_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)