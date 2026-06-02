from fastapi import FastAPI

app = FastAPI(
    title="AI Regulatory Compliance Assistant",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Compliance Assistant API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}