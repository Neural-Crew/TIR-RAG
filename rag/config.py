from __future__ import annotations

import os

from dotenv import load_dotenv


def getenv(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    return value if value is not None else default


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.provider = getenv("RAG_PROVIDER", "openai")
        self.openai_api_key = getenv("OPENAI_API_KEY")
        self.mistral_api_key = getenv("MISTRAL_API_KEY")
        self.embedding_model = getenv("RAG_EMBEDDING_MODEL", "text-embedding-3-small")
        self.chat_model = getenv("RAG_CHAT_MODEL", "gpt-4o-mini")
        self.index_dir = getenv("RAG_INDEX_DIR", "./index")
        self.data_dir = getenv("RAG_DATA_DIR", "./data")
        self.chunk_size = int(getenv("RAG_CHUNK_SIZE", "1200"))
        self.chunk_overlap = int(getenv("RAG_CHUNK_OVERLAP", "200"))
        self.top_k = int(getenv("RAG_TOP_K", "4"))


settings = Settings()
