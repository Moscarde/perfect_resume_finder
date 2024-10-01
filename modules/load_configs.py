import yaml
import os

def load_config(app=None, config_file="config.yaml"):
    try:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"O arquivo de configuração '{config_file}' não foi encontrado.")
        
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
        
        app.config["EXCEL_FILE"] = config["excel_file"]
        app.config["MYSQL_HOST"] = config["mysql"]["host"]
        app.config["MYSQL_PORT"] = config["mysql"]["port"]
        app.config["MYSQL_USER"] = config["mysql"]["user"]
        app.config["MYSQL_PASSWORD"] = config["mysql"]["password"]
        app.config["MYSQL_DATABASE"] = config["mysql"]["database"]

    except FileNotFoundError as fnf_error:
        print(f"Erro: {fnf_error}")

    except KeyError as key_error:
        print(f"Erro: Chave de configuração faltando no arquivo: {key_error}")

    except yaml.YAMLError as yaml_error:
        print(f"Erro ao processar o arquivo YAML: {yaml_error}")

    except Exception as e:
        print(f"Erro inesperado: {e}")