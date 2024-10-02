import threading
from functools import wraps

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_socketio import SocketIO, emit

from modules.db_operations import (
    db_process_and_insert_data,
    db_search_by_terms,
    get_db_length,
)
from modules.load_configs import load_config
from modules.utils import count_new_resumes

app = Flask(__name__)
app.secret_key = "secret_key"
load_config(app)
socketio = SocketIO(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session or not session["logged_in"]:
            flash("Você precisa estar logado para acessar esta página.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Autenticação simples com credenciais estáticas
        if username == "admin" and password == "admin":
            session["logged_in"] = True
            session["username"] = username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("home"))
        else:
            flash("Credenciais inválidas, tente novamente.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.pop("logged_in", None)
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    return render_template("home.html")


@app.route("/atualizar_db", methods=["GET"])
@login_required
def atualizar_db():
    count_db = get_db_length(app)
    print("Quantidade de registros no banco:", count_db)

    count_insert = count_new_resumes(table_path=app.config["EXCEL_FILE"])
    print("Quantidade de registros na planilha:", count_insert)

    return render_template(
        "atualizar_db.html", count_db=count_db, count_insert=count_insert
    )


@app.route("/buscar_curriculos", methods=["GET", "POST"])
@login_required
def buscar_curriculos():
    if request.method == "GET":
        return render_template("buscar_curriculos.html")
    else:
        search_terms = request.form.get("search")
        results = db_search_by_terms(app, search_terms)

        results_list = [dict(row._mapping) for row in results]

        return jsonify(results_list)


@app.route("/processar_novos_dados", methods=["POST"])
@login_required
def processar_novos_dados():

    def run_db_process_and_insert_data():
        try:
            db_process_and_insert_data(app, socketio)
            socketio.emit(
                "status_done",
                {"status": "Processamento concluído. Reiniciando a página!"},
            )
        except Exception as e:
            print(e)
            socketio.emit(
                "status_error", {"status": f"Erro ao processar novos dados: {str(e)}"}
            )

    threading.Thread(target=run_db_process_and_insert_data).start()
    return jsonify({"status": "Processamento iniciado!"})


@app.route("/set_dark_mode", methods=["POST"])
def set_dark_mode():
    data = request.json
    dark_mode = data.get("dark_mode")
    if dark_mode is not None:
        session["color_mode"] = "dark" if dark_mode else "light"
        return jsonify({"status": "success", "mode": session["color_mode"]})
    return jsonify({"status": "error"}), 400


if __name__ == "__main__":
    app.run(debug=True)
