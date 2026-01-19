from __future__ import annotations

from pathlib import Path
from typing import Iterable

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import settings


def _build_embeddings():
    provider = settings.provider.lower()
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when RAG_PROVIDER=openai")
        return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
    if provider == "mistral":
        from langchain_mistralai import MistralAIEmbeddings

        if not settings.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY is required when RAG_PROVIDER=mistral")
        return MistralAIEmbeddings(model=settings.embedding_model, api_key=settings.mistral_api_key)
    raise ValueError(f"Unsupported provider: {provider}")


def _build_chat_model():
    provider = settings.provider.lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when RAG_PROVIDER=openai")
        return ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key)
    if provider == "mistral":
        from langchain_mistralai import ChatMistralAI

        if not settings.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY is required when RAG_PROVIDER=mistral")
        return ChatMistralAI(model=settings.chat_model, api_key=settings.mistral_api_key)
    raise ValueError(f"Unsupported provider: {provider}")


def _load_documents(folder: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(folder.glob("*.pdf")):
        loader = PyPDFLoader(str(path))
        docs = loader.load()
        for doc in docs:
            doc.metadata = dict(doc.metadata or {})
            doc.metadata["source"] = path.name
        documents.extend(docs)
    return documents


def _split_documents(documents: Iterable[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(list(documents))


def ingest_folder(folder: Path, index_dir: Path) -> int:
    documents = _load_documents(folder)
    if not documents:
        return 0
    chunks = _split_documents(documents)
    embeddings = _build_embeddings()
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(index_dir))
    return len(chunks)


def _load_vector_store(index_dir: Path) -> FAISS:
    embeddings = _build_embeddings()
    return FAISS.load_local(str(index_dir), embeddings, allow_dangerous_deserialization=True)


def query_index(question: str, index_dir: Path, top_k: int) -> tuple[str, list[Document]]:
    vector_store = _load_vector_store(index_dir)
    docs = vector_store.similarity_search(question, k=top_k)

    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You answer questions as if you were an AI research specialist. If the context is insufficient, say so.",
            ),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ]
    )

    model = _build_chat_model()
    chain = prompt | model
    response = chain.invoke({"context": context, "question": question})
    return response.content, docs
