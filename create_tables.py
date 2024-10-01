import os

from modules.db_operations import create_db_session, create_table


def create_db_tables():
    try:
        session, engine = create_db_session()
        create_table(engine)
        session.close()
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    create_db_tables()
