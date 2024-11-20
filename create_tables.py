import os

from modules.db_operations import create_db_session, create_table
from modules.load_configs import load_config


def create_db_tables():
    try:
        config = load_config()
        session, engine = create_db_session(
            user=config["mysql"]["user"],
            password=config["mysql"]["password"],
            host=config["mysql"]["host"],
            database=config["mysql"]["database"],
        )
        create_table(engine)
        session.close()
        print("Tables created!")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    create_db_tables()
