# Simple PDF RAG Backend

Small FastAPI + LangChain service that ingests PDFs, builds a FAISS index, and answers questions with OpenAI or Mistral. Includes a minimal Streamlit UI.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your API key.

## Run

Start the API:

```powershell
uvicorn rag.app:app --reload
```

Ingest PDFs (from `./data` by default):

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest
```

Ask a question:

```powershell
$body = @{ question = "What is this dataset about?" } | ConvertTo-Json
Invoke-RestMethod -Method Post -ContentType "application/json" -Body $body http://127.0.0.1:8000/query
```

Optional UI:

```powershell
streamlit run streamlit_app.py
```
