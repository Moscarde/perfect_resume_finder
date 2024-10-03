import yaml
import os
from flask import Flask
from typing import Optional, Dict, Union

def load_config(app: Optional[Flask] = None, config_file: str = "config.yaml") -> Optional[Dict[str, Union[str, int]]]:
    """
    Loads configuration from a YAML file.

    If an app instance is provided, it updates `app.config` with values from the YAML file.
    Otherwise, it returns the configuration as a dictionary.

    Parameters:
    ----------
    app : Flask, optional
        The Flask app instance to update with config values.
    config_file : str, optional
        Path to the YAML configuration file (default is "config.yaml").

    Returns:
    -------
    dict:
        A dictionary with config values if no app is passed.

    Exceptions:
    ----------
    FileNotFoundError:
        Raised if the configuration file is not found.
    KeyError:
        Raised if required keys are missing from the YAML file.
    yaml.YAMLError:
        Raised for any errors in processing the YAML file.
    Exception:
        Catches any other unexpected errors.
    """
    try:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
            
        if not app:
            return config

        app.config["EXCEL_FILE"] = config["excel_file"]
        app.config["MYSQL_HOST"] = config["mysql"]["host"]
        app.config["MYSQL_PORT"] = config["mysql"]["port"]
        app.config["MYSQL_USER"] = config["mysql"]["user"]
        app.config["MYSQL_PASSWORD"] = config["mysql"]["password"]
        app.config["MYSQL_DATABASE"] = config["mysql"]["database"]

    except FileNotFoundError as fnf_error:
        print(f"Erro: {fnf_error}")

    except KeyError as key_error:
        print(f"Erro: Config key is missing: {key_error}")

    except yaml.YAMLError as yaml_error:
        print(f"Error processing YAML file: {yaml_error}")

    except Exception as e:
        print(f"Unexpected error: {e}")