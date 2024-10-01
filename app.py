import threading

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

from modules.db_operations import (
    db_process_and_insert_data,
    get_db_length,
    db_search_by_terms,
)
from modules.load_configs import load_config
from modules.utils import count_new_resumes

app = Flask(__name__)
app.secret_key = 'secret_key'
load_config(app)
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/atualizar_db", methods=["GET"])
def atualizar_db():
    count_db = get_db_length(app)
    print("Quantidade de registros no banco:", count_db)

    count_insert = count_new_resumes(table_path=app.config["EXCEL_FILE"])
    print("Quantidade de registros na planilha:", count_insert)

    return render_template(
        "atualizar_db.html", count_db=count_db, count_insert=count_insert
    )


@app.route("/buscar_curriculos", methods=["GET", "POST"])
def buscar_curriculos():
    if request.method == "GET":
        return render_template("buscar_curriculos.html")
    else:
        search_terms = request.form.get("search")
        results = db_search_by_terms(app, search_terms)

        results_list = [dict(row._mapping) for row in results]

        return jsonify(results_list)


@app.route("/processar_novos_dados", methods=["POST"])
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


if __name__ == "__main__":
    app.run(debug=True)
