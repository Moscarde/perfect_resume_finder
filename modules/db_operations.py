import os

import pandas as pd
from sqlalchemy import Column, Index, Integer, String, Text, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from modules.utils import download_file, extract_text_from_pdf

Base = declarative_base()


# Classe que define a tabela 'resumes'
class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    contry = Column(String(255), nullable=False)
    desired_role = Column(String(255), nullable=False)
    salary_expectations = Column(String(255), nullable=False)
    english_level = Column(String(255), nullable=False)
    linkedin_url = Column(String(255), nullable=False)
    full_text = Column(Text, nullable=False)
    resume_url = Column(String(255), nullable=False, unique=True)

    # Definição do índice FULLTEXT usando SQLAlchemy
    __table_args__ = (Index("busca_fulltext", "full_text", mysql_prefix="FULLTEXT"),)


def create_db_session(user, password, host, database):
    engine = create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{host}:3306/{database}",
        connect_args={"auth_plugin": "mysql_native_password"},
    )

    Session = sessionmaker(bind=engine)
    return Session(), engine


def create_table(engine):
    Base.metadata.create_all(engine)


def get_db_length(app):
    session, engine = create_db_session(
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        host=app.config["MYSQL_HOST"],
        database=app.config["MYSQL_DATABASE"],
    )
    length = session.query(Resume).count()
    session.close()
    return length


def url_exists(session, url):
    return session.query(Resume).filter(Resume.resume_url == url).count() > 0


def db_add_resume(session, row, full_text):
    new_resume = Resume(
        name=row.get("Name", ""),
        email=row.get("Email", ""),
        contry=row.get("Country", ""),
        desired_role=row.get("Desired Role", ""),
        salary_expectations=row.get("Salary Expectations in USD", ""),
        english_level=row.get("English Level", ""),
        linkedin_url=row.get("Linkedin", ""),
        resume_url=row.get("Resume File", ""),
        full_text=full_text,
    )

    session.add(new_resume)


def db_process_and_insert_data(app, socketio):
    resumes_form_path = app.config["EXCEL_FILE"]

    socketio.emit("status_update", {"status": "Iniciando processamento..."})
    session, engine = create_db_session(
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        host=app.config["MYSQL_HOST"],
        database=app.config["MYSQL_DATABASE"],
    )

    create_table(engine)

    df = pd.read_excel(resumes_form_path)
    urls = df["Resume File"].tolist()
    socketio.emit(
        "status_update", {"status": f"Found {len(urls)} entries in the spreadsheet."}
    )

    new_urls = [url for url in urls if not url_exists(session, url)]
    if not new_urls:
        socketio.emit(
            "status_update", {"status": f"All entries have already been processed."}
        )
        session.close()
        return
    df = df[df["Resume File"].isin(new_urls)]

    resumes_path = "resume_files"
    os.makedirs(resumes_path, exist_ok=True)
    for i, row in df.iterrows():
        socketio.emit(
            "status_update", {"status": f"Processing... {i + 1}/{len(new_urls)}"}
        )
        resume = download_file(url=row["Resume File"], output=resumes_path)
        extracted_text = extract_text_from_pdf(resume)

        db_add_resume(session, row, extracted_text)

    session.commit()
    session.close()
    print("Processamento concluído!")


def db_search_by_terms(app, search_terms):
    session, engine = create_db_session(
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        host=app.config["MYSQL_HOST"],
        database=app.config["MYSQL_DATABASE"],
    )

    query = text(
        """
        SELECT * FROM resumes
        WHERE MATCH(full_text) AGAINST(:term IN BOOLEAN MODE)
        """
    )

    results = session.execute(query, {"term": search_terms}).fetchall()

    session.close()
    return results
