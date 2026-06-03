# Chroma Cloud Getting Started (example)

This small project demonstrates using Chroma Cloud via the `chromadb` Python package.

Steps performed by the provided `ingest_query.py`:
- Load Chroma connection info from `.env` (created by `chroma db connect ... --env-file`).
- Create (or get) a collection named `chroma-getting-started`.
- Ingest three documents with deterministic embeddings.
- Run a vector query and print results.

Before running:
1. Create a venv and install requirements: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. Install `chromadb` CLI is included in the package. Use `chroma profile show` to check profile or `chroma login` to authenticate.
3. Create a DB and connect it to this folder:
   - `chroma db create chroma-getting-started`
   - `chroma db connect chroma-getting-started --env-file` (this will create `.env` here)
4. Then run: `python ingest_query.py`
