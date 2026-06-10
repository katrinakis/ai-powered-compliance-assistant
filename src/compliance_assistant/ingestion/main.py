import logging
logging.basicConfig(level=logging.DEBUG)

from compliance_assistant.ingestion import download_eurlex_pdf, download_corpus

if __name__ == '__main__':
    # download_eurlex_pdf("32016R0679")
    download_corpus()