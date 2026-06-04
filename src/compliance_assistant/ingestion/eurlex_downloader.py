"""
src/compliance_assistant/ingestion/eurlex_downloader.py

Downloads EU regulatory documents as PDFs from EUR-Lex by CELEX number.

Strategy (per EUR-Lex Web Services documentation v3.0.0):
    1. Primary:  EUR-Lex direct URL
                 eur-lex.europa.eu/legal-content/{lang}/TXT/PDF/?uri=CELEX:{id}
    2. Fallback: CELLAR REST API (open, no registration required)
                 publications.europa.eu/resource/celex/{id}
                 using Accept: application/pdf content negotiation

Relevant project section: 6.4 Data Ingestion & Regulatory Data Acquisition
"""

import logging
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path

log = logging.getLogger(__name__)

# Walk up from this file: ingestion/ -> compliance_assistant/ -> src/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT = 60       # seconds
RATE_LIMIT_DELAY = 1.5     # seconds between requests
MAX_RETRIES = 3

# Key EU regulations for the compliance assistant project
REGULATORY_CORPUS: dict[str, str] = {
    # Data Protection & Privacy
    "32016R0679": "GDPR - General Data Protection Regulation",
    "32022R2065": "DSA  - Digital Services Act",
    "32022R1925": "DMA  - Digital Markets Act",
    # Financial Regulation
    "32014L0065": "MiFID II - Markets in Financial Instruments Directive",
    "32015L2366": "PSD2     - Payment Services Directive 2",
    "32022R2554": "DORA     - Digital Operational Resilience Act",
    "32018L0843": "AMLD5    - 5th Anti-Money Laundering Directive",
    # AI & Digital Finance
    "32024R1689": "EU AI Act",
    "32020R0851": "Taxonomy Regulation (Sustainable Finance)",
}

# ---------------------------------------------------------------------------
# HTTP session
# ---------------------------------------------------------------------------

def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": "Python EUR-Lex downloader/2.0 (academic/research use)"
    })
    return session


_SESSION = _build_session()

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _try_eurlex_direct(celex_id: str, language: str) -> bytes | None:
    """Primary method via EUR-Lex direct PDF URL."""
    url = (
        f"https://eur-lex.europa.eu/legal-content/"
        f"{language}/TXT/PDF/?uri=CELEX:{celex_id}"
    )
    log.debug("[%s] Trying EUR-Lex direct URL: %s", celex_id, url)
    try:
        r = _SESSION.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)

        log.debug(
            "[%s] EUR-Lex direct → status=%s, content-type=%s, size=%d bytes, final-url=%s",
            celex_id,
            r.status_code,
            r.headers.get("Content-Type", "unknown"),
            len(r.content),
            r.url,
        )

        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "").lower()
        if "pdf" not in content_type:
            log.warning(
                "[%s] EUR-Lex direct: expected PDF but got '%s' — "
                "this may be an HTML consent/redirect page. "
                "Falling back to CELLAR API.",
                celex_id,
                content_type,
            )
            return None

        if len(r.content) <= 1024:
            log.warning(
                "[%s] EUR-Lex direct: response looks like a PDF but is suspiciously small "
                "(%d bytes) — likely an error page. Falling back to CELLAR API.",
                celex_id,
                len(r.content),
            )
            return None

        return r.content

    except requests.exceptions.HTTPError as e:
        log.warning("[%s] EUR-Lex direct: HTTP error %s", celex_id, e)
    except requests.exceptions.ConnectionError as e:
        log.warning("[%s] EUR-Lex direct: connection error — %s", celex_id, e)
    except requests.exceptions.Timeout:
        log.warning("[%s] EUR-Lex direct: request timed out after %ds", celex_id, REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        log.warning("[%s] EUR-Lex direct: unexpected error — %s", celex_id, e)

    return None


def _try_cellar_api(celex_id: str, language: str) -> bytes | None:
    """Fallback via CELLAR REST API with content negotiation."""
    url = f"https://publications.europa.eu/resource/celex/{celex_id}"
    log.debug("[%s] Trying CELLAR API: %s", celex_id, url)
    try:
        r = _SESSION.get(
            url,
            headers={"Accept": "application/pdf", "Accept-Language": language.lower()},
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        log.debug(
            "[%s] CELLAR API → status=%s, content-type=%s, size=%d bytes, final-url=%s",
            celex_id,
            r.status_code,
            r.headers.get("Content-Type", "unknown"),
            len(r.content),
            r.url,
        )

        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "").lower()
        if "pdf" not in content_type:
            log.warning(
                "[%s] CELLAR API: expected PDF but got '%s' — "
                "document may not be available as PDF. "
                "Try HTML format or check the CELEX number at eur-lex.europa.eu.",
                celex_id,
                content_type,
            )
            return None

        if len(r.content) <= 1024:
            log.warning(
                "[%s] CELLAR API: response is suspiciously small (%d bytes) — "
                "document may not exist or CELEX number may be wrong.",
                celex_id,
                len(r.content),
            )
            return None

        return r.content

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "unknown"
        if status == 404:
            log.warning(
                "[%s] CELLAR API: 404 Not Found — "
                "double-check the CELEX number at eur-lex.europa.eu",
                celex_id,
            )
        elif status == 406:
            log.warning(
                "[%s] CELLAR API: 406 Not Acceptable — "
                "PDF format not available for this document. "
                "It may only exist as HTML or Formex XML.",
                celex_id,
            )
        else:
            log.warning("[%s] CELLAR API: HTTP error %s", celex_id, e)
    except requests.exceptions.ConnectionError as e:
        log.warning("[%s] CELLAR API: connection error — %s", celex_id, e)
    except requests.exceptions.Timeout:
        log.warning("[%s] CELLAR API: request timed out after %ds", celex_id, REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        log.warning("[%s] CELLAR API: unexpected error — %s", celex_id, e)

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def download_eurlex_pdf(
    celex_id: str,
    language: str = "EN",
    out_dir: str | Path = RAW_DATA_DIR,
) -> Path | None:
    """
    Download a single EU legal document PDF by CELEX number.

    Tries EUR-Lex direct URL first; falls back to the CELLAR REST API.
    Skips the download if the file already exists (idempotent).

    Args:
        celex_id:  CELEX identifier, e.g. "32016R0679" (GDPR).
        language:  Two-letter language code, default "EN".
        out_dir:   Directory to save the file into (default: data/raw).

    Returns:
        Path to the saved PDF, or None if both methods failed.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{celex_id}_{language}.pdf"

    if file_path.exists() and file_path.stat().st_size > 1024:
        log.info("[%s] Already exists, skipping: %s", celex_id, file_path.name)
        return file_path

    log.info("[%s] Starting download (language=%s)...", celex_id, language)

    pdf_bytes = _try_eurlex_direct(celex_id, language)

    if pdf_bytes is None:
        log.info("[%s] Trying CELLAR API fallback...", celex_id)
        pdf_bytes = _try_cellar_api(celex_id, language)

    if pdf_bytes is None:
        log.error(
            "[%s] Both methods failed. Suggestions:\n"
            "  1. Verify the CELEX number at https://eur-lex.europa.eu\n"
            "  2. Check if the document has a PDF version available\n"
            "  3. Try a different language code (e.g. 'FR', 'DE')\n"
            "  4. Run with DEBUG logging for full request details: "
            "logging.basicConfig(level=logging.DEBUG)",
            celex_id,
        )
        return None

    file_path.write_bytes(pdf_bytes)
    log.info("[%s] Saved: %s (%.1f KB)", celex_id, file_path.name, len(pdf_bytes) / 1024)
    return file_path


def download_corpus(
    celex_ids: list[str] | None = None,
    language: str = "EN",
    out_dir: str | Path = RAW_DATA_DIR,
) -> dict[str, Path | None]:
    """
    Download a batch of EU regulatory documents with rate limiting.

    Args:
        celex_ids:  List of CELEX numbers. Defaults to REGULATORY_CORPUS.
        language:   Two-letter language code, default "EN".
        out_dir:    Output directory (default: data/raw).

    Returns:
        Dict mapping each CELEX id to its saved Path, or None on failure.
    """
    ids = celex_ids if celex_ids is not None else list(REGULATORY_CORPUS.keys())
    results: dict[str, Path | None] = {}

    log.info("Starting corpus download: %d documents to %s", len(ids), out_dir)

    for i, celex_id in enumerate(ids):
        celex_id = celex_id.strip()
        if not celex_id:
            continue

        label = REGULATORY_CORPUS.get(celex_id, "unknown regulation")
        log.info("[%d/%d] %s — %s", i + 1, len(ids), celex_id, label)

        results[celex_id] = download_eurlex_pdf(celex_id, language=language, out_dir=out_dir)

        if i < len(ids) - 1:
            log.debug("Rate limiting: waiting %.1fs before next request...", RATE_LIMIT_DELAY)
            time.sleep(RATE_LIMIT_DELAY)

    ok = sum(1 for v in results.values() if v is not None)
    failed = [k for k, v in results.items() if v is None]

    log.info("─" * 60)
    log.info("Corpus download complete: %d/%d succeeded", ok, len(ids))
    if failed:
        log.warning(
            "%d document(s) failed: %s\n"
            "Re-run download_corpus() to retry only the failed ones, or check "
            "the CELEX numbers manually at https://eur-lex.europa.eu",
            len(failed),
            ", ".join(failed),
        )

    return results