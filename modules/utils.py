import os
import pandas as pd
import fitz
import requests


def download_file(url, output):
    os.makedirs(output, exist_ok=True)

    response = requests.get(url)
    filepath = os.path.join(output, url.split("/")[-1])

    with open(filepath, "wb") as file:
        file.write(response.content)

    return filepath


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                extracted_text.append(block_text.strip())

    return "\n".join(extracted_text)

def count_new_resumes(table_path):
    df = pd.read_excel(table_path)
    return len(df)