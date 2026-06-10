"""
Uploads downloaded EUR-Lex PDFs from local folder eu_docs
to a Unity Catalog Volume in Databricks.

file: ex2.py
"""

from pathlib import Path
from databricks.sdk import WorkspaceClient


CATALOG = "accenture2026dbcks"
SCHEMA = "default"
VOLUME = "data"

VOLUME_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

DOWNLOAD_DIR = Path("eu_docs")


def upload_pdf_to_volume(local_file: Path, volume_path: str) -> None:
    """
    Upload one local PDF file to a Databricks Unity Catalog Volume.
    """

    w = WorkspaceClient()

    target_file = f"{volume_path}/{local_file.name}"

    with open(local_file, "rb") as f:
        w.files.upload(
            file_path=target_file,
            contents=f,
            overwrite=True,
        )

    print(f"Uploaded: {local_file} -> {target_file}")


if __name__ == "__main__":
    if not DOWNLOAD_DIR.exists():
        raise FileNotFoundError(
            f"Folder not found: {DOWNLOAD_DIR}. "
            "Run ex1.py first to download the PDFs."
        )

    pdf_files = list(DOWNLOAD_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DOWNLOAD_DIR}. "
            "Run ex1.py first."
        )

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_file in pdf_files:
        upload_pdf_to_volume(
            local_file=pdf_file,
            volume_path=VOLUME_PATH,
        )

    print("All PDFs uploaded successfully.")