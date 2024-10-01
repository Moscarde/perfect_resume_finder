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

def create_db_session(user="usertest", password="Senha123!", host="localhost", database="tech_recruiter"):
    engine = create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{host}:3306/{database}",
        connect_args={"auth_plugin": "mysql_native_password"}
    )

    Session = sessionmaker(bind=engine)
    return Session(), engine


def create_table(engine):
    Base.metadata.create_all(engine)

def get_db_length():
    session, engine = create_db_session()
    length = session.query(Resume).count()
    session.close()
    return length

def url_exists(session, url):
    return session.query(Resume).filter(Resume.resume_url == url).count() > 0


def add_resume(session, row, full_text):
    new_resume = Resume(name = row.get("Name", ""),
    email = row.get("Email", ""),
    contry = row.get("Country", ""),
    desired_role = row.get("Desired Role", ""),
    salary_expectations = row.get("Salary Expectations in USD", ""),
    english_level = row.get("English Level", ""),
    linkedin_url = row.get("Linkedin", ""),
    resume_url = row.get("Resume File", ""),
    full_text = full_text)

    session.add(new_resume)
    

def update_db(file_path, socketio):
    socketio.emit('status_update', {'status': 'Iniciando processamento...'})
    session, engine = create_db_session()

    # Criar a tabela se não existir
    create_table(engine)

    # 1.1 Ler a planilha e obter as URLs
    df = pd.read_excel(file_path)
    urls = df["Resume File"].tolist()
    socketio.emit('status_update', {'status': f'Encontrado {len(urls)} entradas na planilha.'})

    # 1.2 Obter URLs que ainda não estão no banco de dados
    new_urls = [url for url in urls if not url_exists(session, url)]

    if not new_urls:
        socketio.emit('status_update', {'status': f'Todas as entradas já foram processadas.'})
        print("Nenhuma nova URL encontrada. Finalizando.")
        session.close()
        return  # Finaliza se não houver novas URLs

    df = df[df["Resume File"].isin(new_urls)]
    # 1.3 Processar cada nova URL
    dest_folder = "resume_files"

    for i, row in df.iterrows():
        socketio.emit('status_update', {'status': f'Processando... {i + 1}/{len(new_urls)}'})
        print(f"Baixando arquivo: {row["Resume File"]}")
        file_path = download_file(row["Resume File"], dest_folder)
        extracted_text = extract_text_from_pdf(file_path)

        # Criar um novo registro no banco de dados
        add_resume(session, row, extracted_text)

    # Salvar as alterações no banco de dados
    session.commit()
    session.close()
    print("Processamento concluído!")


def search_by_term( term):
    session, engine = create_db_session()
    query = text(
        f"""
        SELECT * FROM resumes
        WHERE MATCH(full_text) AGAINST('{term}')
    """
    )
    results = session.execute(query, {"term": term}).fetchall()
    session.close()
    return results
