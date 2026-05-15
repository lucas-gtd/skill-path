from __future__ import annotations

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_cv_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = [chunk.strip() for chunk in splitter.split_text(text) if chunk.strip()]
    if not chunks:
        raise ValueError("The CV text could not be split into retrievable chunks.")
    return chunks


def retrieve_context(chunks: list[str], queries: list[str], top_k: int) -> str:
    documents = [Document(page_content=chunk) for chunk in chunks]
    retriever = BM25Retriever.from_documents(documents)
    retriever.k = max(top_k, 1)

    seen: set[str] = set()
    ordered_chunks: list[str] = []
    for query in queries:
        for document in retriever.invoke(query):
            content = document.page_content.strip()
            if content and content not in seen:
                seen.add(content)
                ordered_chunks.append(content)

    return "\n\n".join(ordered_chunks)
