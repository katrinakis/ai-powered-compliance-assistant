"""
Reads EU regulation PDF files from a Databricks Unity Catalog Volume,
extracts text from each page, and prints the first 1000 characters
of the first page for each PDF.

file: ex5.py
"""

from io import BytesIO
from pypdf import PdfReader
from databricks.sdk import WorkspaceClient
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


CATALOG = "accenture2026dbcks"
SCHEMA = "default"
VOLUME = "data"

VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"


PDF_FILES = [
    "32016R0679_GDPR_EN.pdf",
    "32022R2554_DORA_EN.pdf",
    "32015L2366_PSD2_EN.pdf",
    "32014L0065_MiFID_II_EN.pdf",
    "32024R1689_AI_Act_EN.pdf",
]


def get_pages(pdf_path: str) -> list[dict]:
    """
    Download a PDF from a Databricks Volume,
    extract text from all pages, and return a list of page dictionaries.
    """

    logging.info(f"Extracting pages from: {pdf_path}")

    w = WorkspaceClient()

    pdf_bytes = (
        w.files.download(pdf_path)
        .contents
        .read()
    )

    reader = PdfReader(BytesIO(pdf_bytes))

    pages = []

    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        pages.append(
            {
                "page_number": page_num,
                "text": page_text,
            }
        )

    logging.info(f"Pages extracted: {len(pages)}")

    return pages


def process_pdf(pdf_filename: str) -> list[dict]:
    """
    Build full Volume path for a PDF file,
    extract its pages, and print a preview.
    """

    pdf_path = f"{VOLUME_PATH}/{pdf_filename}"

    pages = get_pages(pdf_path)

    print("=" * 100)
    print(f"PDF file: {pdf_filename}")
    print(f"Total pages: {len(pages)}")
    print("-" * 100)

    if pages:
        print("First 1000 characters of page 1:")
        print(pages[0]["text"][:1000])
    else:
        print("No pages found.")

    print("=" * 100)
    print()

    return pages


if __name__ == "__main__":
    all_documents = {}

    for pdf_filename in PDF_FILES:
        try:
            pages = process_pdf(pdf_filename)
            all_documents[pdf_filename] = pages

        except Exception as e:
            logging.error(f"Failed to process {pdf_filename}: {e}")

    print(f"Processed {len(all_documents)} PDF files successfully.")