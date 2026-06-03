"""
Create a FastAPI API for loading EU law chunks from a Databricks table.

Run with:
    uv run uvicorn api:app --reload

Or, if the file is inside src/day07/session3/api.py:
    uv run uvicorn src.day07.session3.api:app --reload

Required dependencies:
    uv add fastapi uvicorn databricks-connect pandas

This is test version. Surely needs tweeking and improvements, but it's a starting point for the Compliance Assistant API.   
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from databricks.connect import DatabricksSession


CATALOG = "accenture2026dbcks"
SCHEMA = "default"
TABLE = "eu_law_chunks"

TABLE_NAME = f"{CATALOG}.{SCHEMA}.{TABLE}"


app = FastAPI(
    title="EU Law Chunks API",
    description="API for loading EU regulation text chunks from Databricks.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_spark():
    """
    Create a Databricks Connect Spark session.
    """

    spark = (
        DatabricksSession.builder
        .serverless(True)
        .getOrCreate()
    )

    return spark


@app.get("/health")
def get_health():
    return {
        "status": "ok",
        "message": "API is running",
    }


@app.get("/eu_law_chunks")
def get_eu_law_chunks(
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Load chunks from the Databricks table.

    Example:
        /eu_law_chunks?limit=5
    """

    spark = get_spark()

    df = (
        spark.table(TABLE_NAME)
        .limit(limit)
        .toPandas()
    )

    return {
        "table": TABLE_NAME,
        "count": len(df),
        "chunks": df.to_dict(orient="records"),
    }


@app.get("/eu_law_chunks/{document_id}")
def get_chunks_by_document(
    document_id: str,
    limit: int = Query(default=10, ge=1, le=100),
):
    """
    Load chunks for one specific document.

    Examples:
        /eu_law_chunks/32016R0679
        /eu_law_chunks/32022R2554
        /eu_law_chunks/32015L2366
        /eu_law_chunks/32014L0065
        /eu_law_chunks/32024R1689
    """

    spark = get_spark()

    query = f"""
        SELECT
            document_id,
            document_title,
            filename,
            page_number,
            chunk_id,
            chunk_number,
            chunk_text
        FROM {TABLE_NAME}
        WHERE document_id = '{document_id}'
        LIMIT {limit}
    """

    df = spark.sql(query).toPandas()

    return {
        "table": TABLE_NAME,
        "document_id": document_id,
        "count": len(df),
        "chunks": df.to_dict(orient="records"),
    }


@app.get("/documents")
def get_documents():
    """
    Return the available EU law documents from the chunks table.
    """

    spark = get_spark()

    query = f"""
        SELECT DISTINCT
            document_id,
            document_title,
            filename
        FROM {TABLE_NAME}
        ORDER BY document_title
    """

    df = spark.sql(query).toPandas()

    return {
        "count": len(df),
        "documents": df.to_dict(orient="records"),
    }


@app.post("/login")
def login(username: str, password: str):
    """
    Simple example login endpoint.

    This is only for practice.
    Do not use hardcoded credentials in a real project.
    """

    if username == "admin" and password == "password":
        return {
            "message": "Login successful",
        }

    return {
        "message": "Invalid credentials",
    }