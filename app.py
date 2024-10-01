import threading

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

from modules.db_operations import get_db_length, search_by_term, update_db
from modules.utils import count_new_resumes

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/atualizar_db")
def atualizar_db():
    count_db = get_db_length()
    count_insert = count_new_resumes()
    return render_template(
        "atualizar_db.html", count_db=count_db, count_insert=count_insert
    )

@app.route("/buscar_curriculos", methods=["GET", "POST"])
def buscar_curriculos():
    if request.method == "GET":
        return render_template("buscar_curriculos.html")
    else:
        termo = request.form.get("termo")

        results = search_by_term(termo)
        print(results)
        print(type(results))
        print(type(results[0]))
        print(type(results[0][0]))

        # Convertendo os resultados para um formato serializável
        results_list = [dict(row._mapping) for row in results]


        return jsonify(results_list)


@app.route("/processar_novos_dados", methods=["POST"])
def processar_novos_dados():
    file_path = "new_resumes.xlsx"  # Ajuste para o caminho correto

    def run_update_db():
        try:
            update_db(file_path, socketio)
            socketio.emit(
                "status_done",
                {"status": "Processamento concluído. Reiniciando a página!"},
            )
        except Exception as e:
            print(e)
            socketio.emit(
                "status_error", {"status": f"Erro ao processar novos dados: {str(e)}"}
            )
        # update_db(file_path, db_type)
        # Você pode usar um sistema de mensageria ou eventos para avisar quando terminar

    threading.Thread(target=run_update_db).start()
    return jsonify({"status": "Processamento iniciado!"})


if __name__ == "__main__":
    app.run(debug=True)
