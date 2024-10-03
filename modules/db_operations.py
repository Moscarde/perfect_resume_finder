import os
from typing import Any, List, Tuple

import pandas as pd
from flask import Flask
from flask_socketio import SocketIO
from sqlalchemy import Column, Index, Integer, String, Text, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from modules.utils import download_file, extract_text_from_pdf

Base = declarative_base()


# Classe que define a tabela 'resumes'
class Resume(Base):
    """
    ORM class that defines the 'resumes' table in the database.

    Attributes:
        id (int): Primary key for the resume record.
        name (str): Candidate's name.
        email (str): Candidate's email.
        contry (str): Candidate's country.
        desired_role (str): Candidate's desired role.
        salary_expectations (str): Candidate's salary expectations in USD.
        english_level (str): Candidate's English proficiency level.
        linkedin_url (str): Candidate's LinkedIn profile URL.
        full_text (str): Full text of the resume.
        resume_url (str): URL to the resume file.
    """

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


def create_db_session(
    user: str, password: str, host: str, database: str
) -> Tuple[Session, Engine]:
    """
    Creates a database session and engine for connecting to MySQL.

    Args:
        user (str): Database username.
        password (str): Database password.
        host (str): Hostname of the database server.
        database (str): Name of the database to connect to.

    Returns:
        Tuple[Session, Engine]: A tuple containing the database session and engine.
    """
    engine = create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{host}:3306/{database}",
        connect_args={"auth_plugin": "mysql_native_password"},
    )

    Session = sessionmaker(bind=engine)
    return Session(), engine


def create_table(engine: Engine) -> None:
    """
    Creates all tables defined by ORM classes in the database.

    Args:
        engine (Engine): SQLAlchemy engine connected to the database.
    """
    Base.metadata.create_all(engine)


def get_db_length(app: Flask) -> int:
    """
    Retrieves the total number of resumes in the database.

    Args:
        app (Flask): Flask application object, used to access the app config.

    Returns:
        int: The total number of resume records in the database.
    """
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


def url_exists(session: Session, url: str) -> bool:
    """
    Checks if a resume URL already exists in the database.

    Args:
        session (Session): SQLAlchemy session for querying the database.
        url (str): The URL of the resume to check.

    Returns:
        bool: True if the URL exists, False otherwise.
    """
    return session.query(Resume).filter(Resume.resume_url == url).count() > 0


def db_add_resume(session: Session, row: pd.Series, full_text: str) -> None:
    """
    Adds a new resume record to the database.

    Args:
        session (Session): SQLAlchemy session for adding the resume.
        row (pd.Series): A row from the DataFrame containing resume information.
        full_text (str): Extracted full text of the resume PDF.
    """
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


def db_process_and_insert_data(app: Flask, socketio: SocketIO) -> None:
    """
    Processes new resumes from an Excel file and inserts them into the database.

    Args:
        app (Flask): Flask application object, used to access app config.
        socketio (SocketIO): Flask-SocketIO object to emit status updates to the client.
    """
    resumes_form_path = app.config["EXCEL_FILE"]

    socketio.emit("status_update", {"status": "Starting processing..."})
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
            "status_update", {"status": "All entries have already been processed."}
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
    print("Processing complete!")


def db_search_by_terms(app: Flask, search_terms: str) -> List[Any]:
    """
    Searches resumes in the database by full-text search.

    Args:
        app (Flask): Flask application object, used to access app config.
        search_terms (str): The search terms to query the full-text search.

    Returns:
        List[Any]: A list of result rows that match the search terms.
    """
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
