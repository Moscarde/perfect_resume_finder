import os
import pandas as pd
import fitz
import requests


def download_file(url: str, output: str) -> str:
    """
    Downloads a file from the specified URL and saves it to the given output directory.

    If the output directory does not exist, it is created.

    Parameters:
    ----------
    url : str
        The URL of the file to download.
    output : str
        The path to the directory where the file should be saved.

    Returns:
    -------
    str
        The full path to the downloaded file.

    Exceptions:
    ----------
    requests.exceptions.RequestException:
        Raised for any network-related errors during the download process.
    """
    os.makedirs(output, exist_ok=True)

    response = requests.get(url)
    filepath = os.path.join(output, url.split("/")[-1])

    with open(filepath, "wb") as file:
        file.write(response.content)

    return filepath


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF file by reading its pages and collecting text blocks.

    Parameters:
    ----------
    pdf_path : str
        The path to the PDF file to extract text from.

    Returns:
    -------
    str
        The extracted text from the PDF, with each block separated by newlines.

    Exceptions:
    ----------
    fitz.fitz.FileDataError:
        Raised if the file cannot be opened as a PDF.
    """
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

def count_new_resumes(table_path: str) -> int:
    """
    Counts the number of new resumes from an Excel table.

    Parameters:
    ----------
    table_path : str
        The path to the Excel file containing the resume table.

    Returns:
    -------
    int
        The number of rows (resumes) in the Excel table.

    Exceptions:
    ----------
    FileNotFoundError:
        Raised if the Excel file cannot be found.
    pandas.errors.EmptyDataError:
        Raised if the Excel file is empty or invalid.
    """
    df = pd.read_excel(table_path)
    return len(df)
