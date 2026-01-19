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

Start the front (other terminal)

```powershell
streamlit run streamlit_app.py
```
