"""
Download selected EU regulatory PDFs from EUR-Lex using CELEX numbers.

This script downloads 5 English-language EU regulatory documents
based on the project guideline examples:
- GDPR
- DORA
- PSD2
- MiFID II
- AI Act

file: ex1.py
"""

import requests
from pathlib import Path


EU_REGULATORY_DOCUMENTS = [
    {
        "celex": "32016R0679",
        "title": "GDPR",
        "description": "General Data Protection Regulation",
    },
    {
        "celex": "32022R2554",
        "title": "DORA",
        "description": "Digital Operational Resilience Act",
    },
    {
        "celex": "32015L2366",
        "title": "PSD2",
        "description": "Payment Services Directive 2",
    },
    {
        "celex": "32014L0065",
        "title": "MiFID_II",
        "description": "Markets in Financial Instruments Directive II",
    },
    {
        "celex": "32024R1689",
        "title": "AI_Act",
        "description": "Artificial Intelligence Act",
    },
]


def download_eurlex_pdf_by_celex(
    celex_id: str,
    title: str,
    language: str = "EN",
    out_dir: str = "eu_docs",
) -> Path:
    """
    Download an EU legal document PDF from EUR-Lex using a CELEX number.

    Example:
    CELEX 32016R0679 = GDPR Regulation
    """

    Path(out_dir).mkdir(parents=True, exist_ok=True)

    url = (
        f"https://eur-lex.europa.eu/legal-content/{language}/TXT/PDF/"
        f"?uri=CELEX:{celex_id}&from={language}"
    )

    print(f"Downloading {title} from:")
    print(url)

    headers = {
        "User-Agent": "Python EUR-Lex downloader/1.0",
        "Accept": "application/pdf",
    }

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if not response.content.startswith(b"%PDF"):
        debug_path = Path(out_dir) / f"{celex_id}_{title}_ERROR.html"
        debug_path.write_bytes(response.content)

        raise ValueError(
            f"Downloaded content for {title} does not look like a PDF. "
            f"Content-Type: {content_type}. "
            f"Saved response to: {debug_path}"
        )

    file_path = Path(out_dir) / f"{celex_id}_{title}_{language}.pdf"
    file_path.write_bytes(response.content)

    return file_path


if __name__ == "__main__":
    for document in EU_REGULATORY_DOCUMENTS:
        try:
            path = download_eurlex_pdf_by_celex(
                celex_id=document["celex"],
                title=document["title"],
                language="EN",
                out_dir="eu_docs",
            )

            print(f"Downloaded: {path}")
            print(f"Description: {document['description']}")
            print("-" * 80)

        except Exception as e:
            print(f"Failed to download {document['title']}: {e}")
            print("-" * 80)