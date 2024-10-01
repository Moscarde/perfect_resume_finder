import os
import pandas as pd
import fitz
import requests


def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    response = requests.get(url)
    filename = os.path.join(dest_folder, url.split("/")[-1])

    with open(filename, "wb") as file:
        file.write(response.content)

    return filename


def extract_text_from_pdf(pdf_path):
    # Abre o arquivo PDF a partir dos bytes
    doc = fitz.open(pdf_path)
    extracted_text = []

    # Itera sobre todas as páginas
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Carrega a página
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                extracted_text.append(block_text.strip())

    return "\n".join(extracted_text)

def count_new_resumes(table_path="new_resumes.xlsx"):
    df = pd.read_excel(table_path)
    return len(df)