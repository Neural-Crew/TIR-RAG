import os

import requests
import streamlit as st


def _api_url() -> str:
    return os.getenv("RAG_API_URL", "http://127.0.0.1:8000")


st.set_page_config(page_title="RAG Finder", page_icon="🔎", layout="centered")
st.title("RAG Finder")
st.caption("Lightweight UI for PDF RAG: ingest once, then ask.")

api_url = _api_url().rstrip("/")

with st.sidebar:
    st.subheader("Connection")
    api_url = st.text_input("API base URL", value=api_url)
    st.caption("Example: http://127.0.0.1:8000")

    if st.button("Ingest PDFs", use_container_width=True):
        with st.spinner("Building index..."):
            try:
                resp = requests.post(f"{api_url}/ingest", timeout=300)
                resp.raise_for_status()
                data = resp.json()
                st.success(f"Indexed {data.get('chunks', 0)} chunks.")
            except requests.RequestException as exc:
                st.error(f"Failed to ingest: {exc}")

question = st.text_input("Ask a question")
top_k = st.slider("Top K chunks", min_value=1, max_value=10, value=4)

if st.button("Search", type="primary") and question.strip():
    with st.spinner("Searching..."):
        try:
            payload = {"question": question, "top_k": top_k}
            resp = requests.post(f"{api_url}/query", json=payload, timeout=300)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            st.error(f"Query failed: {exc}")
        else:
            st.subheader("Answer")
            st.write(data.get("answer", ""))

            st.subheader("Sources")
            for idx, item in enumerate(data.get("sources", []), start=1):
                source = item.get("source", "unknown")
                page = item.get("page", "?")
                snippet = item.get("snippet", "")
                st.markdown(f"**{idx}. {source} (p. {page})**")
                st.write(snippet)
