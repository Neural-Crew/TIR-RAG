from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import settings
from .rag_service import ingest_folder, query_index

app = FastAPI(title="Simple RAG Backend")


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]


@app.post("/ingest")
def ingest() -> dict:
    data_dir = Path(settings.data_dir)
    index_dir = Path(settings.index_dir)
    if not data_dir.exists():
        raise HTTPException(status_code=400, detail=f"Data folder not found: {data_dir}")
    chunk_count = ingest_folder(data_dir, index_dir)
    return {"chunks": chunk_count, "index_dir": str(index_dir)}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    index_dir = Path(settings.index_dir)
    if not index_dir.exists():
        raise HTTPException(status_code=400, detail="Index not found. Run /ingest first.")
    top_k = request.top_k or settings.top_k
    answer, docs = query_index(request.question, index_dir, top_k=top_k)
    sources = [
        {
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page"),
            "snippet": doc.page_content[:300],
        }
        for doc in docs
    ]
    return QueryResponse(answer=answer, sources=sources)
