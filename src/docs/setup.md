# Project Setup Guide

## AI Regulatory Compliance Assistant

This document explains how to set up the development environment for the **AI Regulatory Compliance Assistant** project.

The purpose of this setup is to make sure that all team members can clone the repository, install the same dependencies, run the application locally, and follow the same development workflow.

---

## 1. Prerequisites

Before starting, make sure the following tools are installed on your computer:

* Git
* Python
* uv
* Visual Studio Code
* GitHub account

Optional tools that may be used later in the project:

* Docker Desktop
* Azure CLI
* Databricks CLI or Databricks SDK

---

## 2. Clone the Repository

Open a terminal and move to the folder where you want to store the project.

Example on Windows PowerShell:

```powershell
cd C:\Users\YOUR_USERNAME\ProjectAccenture
```

Clone the repository:

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
```

Enter the project folder:

```powershell
cd YOUR_REPOSITORY_NAME
```

Check that Git is working:

```powershell
git status
```

Expected result:

```text
On branch main
Your branch is up to date with 'origin/main'.
```

---

## 3. Project Structure

The project uses a clean Python structure with separate folders for API code, ingestion, processing, retrieval, RAG logic, tests, documentation, and data.

Recommended structure:

```text
ai-regulatory-compliance-assistant/
│
├── README.md
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env.example
│
├── src/
│   └── compliance_assistant/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   └── __init__.py
│       ├── ingestion/
│       │   └── __init__.py
│       ├── processing/
│       │   └── __init__.py
│       ├── retrieval/
│       │   └── __init__.py
│       ├── rag/
│       │   └── __init__.py
│       └── config/
│           └── __init__.py
│
├── tests/
│   └── __init__.py
│
├── docs/
│   └── setup.md
│
├── data/
│   ├── raw/
│   └── processed/
│
└── notebooks/
```

Folder explanation:

```text
src/compliance_assistant/     Main Python package
api/                          FastAPI routes and endpoints
ingestion/                    Data collection and regulatory source ingestion
processing/                   Document parsing, cleaning, chunking, metadata enrichment
retrieval/                    Search and retrieval logic
rag/                          Retrieval-Augmented Generation logic
config/                       Application configuration
tests/                        Unit tests
docs/                         Project documentation
data/raw/                     Raw downloaded documents
data/processed/               Processed AI-ready data
notebooks/                    Experimental notebooks
```

---

## 4. Install Dependencies with uv

This project uses `uv` for Python dependency and virtual environment management.

To install all project dependencies, run:

```powershell
uv sync
```

This command reads the following files:

```text
pyproject.toml
uv.lock
```

and creates a local virtual environment with the correct dependencies.

The virtual environment folder is usually:

```text
.venv/
```

This folder should not be committed to GitHub.

---

## 5. Add New Dependencies

When a new package is needed, use:

```powershell
uv add PACKAGE_NAME
```

Example:

```powershell
uv add fastapi
```

For development-only dependencies, use:

```powershell
uv add --dev PACKAGE_NAME
```

Example:

```powershell
uv add --dev pytest
```

After adding a dependency, `uv` updates:

```text
pyproject.toml
uv.lock
```

These files must be committed and pushed so that the other team member can install the same dependencies.

Example:

```powershell
git add pyproject.toml uv.lock
git commit -m "Update project dependencies"
git push
```

The other team member should then run:

```powershell
git pull
uv sync
```

---

## 6. Environment Variables

The project may later require API keys and service credentials for tools such as Azure OpenAI, Azure AI Search, and Databricks.

Real secrets must not be committed to GitHub.

Create a local `.env` file based on the example file:

```text
.env.example
```

Example `.env.example` content:

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
DATABRICKS_HOST=
DATABRICKS_TOKEN=
```

Each developer should create their own local `.env` file:

```text
.env
```

The `.env` file must stay private and should be ignored by Git.

---

## 7. Run the FastAPI Application

The project includes a basic FastAPI starter application.

The main application file is:

```text
src/compliance_assistant/main.py
```

To run the API locally, use:

```powershell
uv run uvicorn compliance_assistant.main:app --reload
```

If the command above gives an import error, use:

```powershell
uv run uvicorn src.compliance_assistant.main:app --reload
```

When the application starts successfully, the terminal should show something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Do not close the terminal while the application is running.

---

## 8. Test the Application in the Browser

Open the following URL:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{
  "message": "Compliance Assistant API is running"
}
```

Open the health check endpoint:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Open the automatic API documentation:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI page should appear and show the available API endpoints.

At this stage, the available endpoints are:

```text
GET /
GET /health
```

---

## 9. Git Workflow

The team should follow a simple Git workflow.

The `main` branch should contain stable code only.

Team members should not work directly on `main`.

For each task, create a new branch:

```powershell
git checkout -b feature/task-name
```

Example:

```powershell
git checkout -b feature/add-ingestion-module
```

After making changes:

```powershell
git status
git add .
git commit -m "Add ingestion module structure"
git push -u origin feature/add-ingestion-module
```

Then open a Pull Request on GitHub.

The other team member should review the Pull Request before merging it into `main`.

---

## 10. Updating the Local Repository

Before starting new work, always update your local repository:

```powershell
git checkout main
git pull
uv sync
```

Then create a new branch for your task:

```powershell
git checkout -b feature/new-task
```

---

## 11. Files That Should Not Be Committed

The following files and folders should not be pushed to GitHub:

```text
.venv/
.env
__pycache__/
*.pyc
.vscode/
.idea/
.DS_Store
Thumbs.db
```

Raw or large data files should also not be pushed unless specifically required.

Recommended `.gitignore` content:

```gitignore
.venv/
.env
__pycache__/
*.pyc

data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

.vscode/
.idea/
.DS_Store
Thumbs.db
```

---

## 12. Basic Development Rules

The team should follow these rules:

```text
1. Do not push directly to main.
2. Create a feature branch for each task.
3. Open a Pull Request before merging.
4. Review each other's code.
5. Use uv add when adding dependencies.
6. Commit pyproject.toml and uv.lock after dependency changes.
7. Do not commit .env, .venv, or secrets.
8. Keep commit messages short and clear.
9. Update documentation when setup steps change.
10. Run the application locally before pushing major changes.
```

---

## 13. Verifying That Setup Is Complete

The setup is complete when the following checks pass:

```text
Repository cloned successfully
uv sync runs without errors
FastAPI app starts successfully
http://127.0.0.1:8000/ works
http://127.0.0.1:8000/health works
http://127.0.0.1:8000/docs opens Swagger UI
pyproject.toml exists
uv.lock exists
.env.example exists
.gitignore exists
README.md exists
```

---

## 14. Troubleshooting

### Problem: uv is not recognized

Make sure `uv` is installed and available in your system PATH.

Check:

```powershell
uv --version
```

If it does not work, install `uv` again.

---

### Problem: ModuleNotFoundError when running FastAPI

Try this command instead:

```powershell
uv run uvicorn src.compliance_assistant.main:app --reload
```

Also make sure you are running the command from the project root folder.

The project root should contain:

```text
pyproject.toml
uv.lock
src/
```

---

### Problem: Dependency missing

Install it using:

```powershell
uv add PACKAGE_NAME
```

Then commit and push:

```powershell
git add pyproject.toml uv.lock
git commit -m "Add missing dependency"
git push
```

Other team members should then run:

```powershell
git pull
uv sync
```

---

### Problem: Git shows many unnecessary files

Check that `.gitignore` includes:

```gitignore
.venv/
.env
__pycache__/
*.pyc
```

If files were already added accidentally, remove them from Git tracking without deleting them locally:

```powershell
git rm -r --cached .venv
git rm --cached .env
git commit -m "Remove ignored local files from repository"
git push
```

---

## 15. Summary

This setup provides the foundation for the project.

It ensures that:

```text
The repository is organized.
The Python environment is reproducible.
Dependencies are managed with uv.
The FastAPI backend can run locally.
Secrets are handled safely.
Both team members can work with the same setup.
The team follows a clean Git workflow.
```

This completes the development environment setup required for the initial project phase.
