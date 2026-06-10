"""
src/compliance_assistant/ingestion/__init__.py
 
Ingestion package — section 6.4 of the project scope.
Handles acquisition of EU regulatory documents from external sources.
"""
 
from compliance_assistant.ingestion.eurlex_downloader import (
    REGULATORY_CORPUS,
    download_corpus,
    download_eurlex_pdf,
)
 
__all__ = [
    "download_eurlex_pdf",
    "download_corpus",
    "REGULATORY_CORPUS",
]
 