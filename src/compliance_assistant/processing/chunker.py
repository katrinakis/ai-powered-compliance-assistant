"""
file: ex6.py

Reads 5 EU regulation PDFs from a Databricks Unity Catalog Volume,
splits their text into chunks, and saves the chunks to a Databricks Delta table.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from databricks.connect import DatabricksSession
import pandas as pd

from pdf_reader import get_pages


CATALOG = "accenture2026dbcks"
SCHEMA = "default"
VOLUME = "data"

VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

TABLE_NAME = f"{CATALOG}.{SCHEMA}.eu_law_chunks"


PDF_FILES = [
    {
        "document_id": "32016R0679",
        "document_title": "GDPR",
        "filename": "32016R0679_GDPR_EN.pdf",
    },
    {
        "document_id": "32022R2554",
        "document_title": "DORA",
        "filename": "32022R2554_DORA_EN.pdf",
    },
    {
        "document_id": "32015L2366",
        "document_title": "PSD2",
        "filename": "32015L2366_PSD2_EN.pdf",
    },
    {
        "document_id": "32014L0065",
        "document_title": "MiFID_II",
        "filename": "32014L0065_MiFID_II_EN.pdf",
    },
    {
        "document_id": "32024R1689",
        "document_title": "AI_Act",
        "filename": "32024R1689_AI_Act_EN.pdf",
    },
]


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


def create_chunks_for_pdf(document: dict) -> list[dict]:
    """
    Reads one PDF from Databricks Volume,
    extracts text page by page,
    splits each page into chunks,
    and returns a list of chunk dictionaries.
    """

    pdf_path = f"{VOLUME_PATH}/{document['filename']}"

    print(f"Processing: {document['filename']}")

    pages = get_pages(pdf_path)

    chunks = []

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_num, chunk_text in enumerate(page_chunks, start=1):
            chunks.append(
                {
                    "document_id": document["document_id"],
                    "document_title": document["document_title"],
                    "filename": document["filename"],
                    "page_number": page["page_number"],
                    "chunk_id": f"{document['document_id']}_p{page['page_number']}_c{chunk_num}",
                    "chunk_number": chunk_num,
                    "chunk_text": chunk_text,
                }
            )

    print(f"Created {len(chunks)} chunks for {document['document_title']}")

    return chunks


if __name__ == "__main__":
    all_chunks = []

    for document in PDF_FILES:
        try:
            document_chunks = create_chunks_for_pdf(document)
            all_chunks.extend(document_chunks)

        except Exception as e:
            print(f"Failed to process {document['filename']}: {e}")

    print(f"Total chunks created: {len(all_chunks)}")

    if not all_chunks:
        raise ValueError("No chunks were created. Check that the PDFs exist in the Databricks Volume.")

    df = pd.DataFrame(all_chunks)

    print(df.head())

    spark = (
        DatabricksSession.builder
        .serverless(True)
        .getOrCreate()
    )

    spark_df = spark.createDataFrame(df)

    (
        spark_df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(TABLE_NAME)
    )

    print(f"Saved chunks to table: {TABLE_NAME}")