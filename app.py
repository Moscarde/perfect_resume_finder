from flask import Flask
from flask_socketio import SocketIO
from modules.load_configs import load_config
from routes.auth import auth_bp
from routes.db import db_bp
from routes.home import home_bp
from routes.search import search_bp
from routes.color_mode import mode_bp

app = Flask(__name__)
app.secret_key = "secret_key"
load_config(app)

socketio = SocketIO(app)

# Registro dos blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(db_bp)
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)
app.register_blueprint(mode_bp)

if __name__ == "__main__":
    app.run(debug=True)
