"""Local Chroma index managed through the LangChain integration."""

from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from .models import QARecord, RecordType, RetrievedChunk
from .source import record_to_chunk


class IndexUnavailableError(RuntimeError):
    """Indicate that a queryable collection does not exist yet."""

    pass


class QAIndex:
    """Build and query the QA-record vector collection."""

    def __init__(self, path: Path, collection_name: str, embeddings: Embeddings) -> None:
        """Open a persistent Chroma vector store with LangChain embeddings."""
        self.path = path
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.store = self._open_store()

    def _open_store(self) -> Chroma:
        """Create or open the configured collection using cosine distance."""
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.path),
            collection_metadata={"hnsw:space": "cosine"},
        )

    def _collection_count(self) -> int:
        """Count persisted IDs without exposing Chroma internals."""
        return len(self.store.get(include=[])["ids"])

    def rebuild(self, records: list[QARecord]) -> int:
        """Replace the collection and index all records."""
        self.store.delete_collection()
        self.store = self._open_store()
        documents = [Document(
            id=record.id,
            page_content=record_to_chunk(record),
            metadata=record.metadata(),
        ) for record in records]
        self.store.add_documents(documents=documents, ids=[record.id for record in records])
        return self._collection_count()

    def count(self) -> int:
        """Return the number of indexed chunks."""
        try:
            count = self._collection_count()
        except Exception as error:
            raise IndexUnavailableError("El índice no existe. Ejecutá primero build-index.") from error
        if count == 0:
            raise IndexUnavailableError("El índice no existe. Ejecutá primero build-index.")
        return count

    def search(
        self, question: str, record_type: RecordType, limit: int = 2,
        threshold: float = 0.45,
    ) -> list[RetrievedChunk]:
        """Retrieve the most similar chunks of a given type."""
        self.count()
        result = self.store.similarity_search_with_score(
            question,
            k=limit,
            filter={"type": record_type},
        )
        chunks: list[RetrievedChunk] = []
        for document, distance in result:
            score = max(0.0, 1.0 - float(distance))
            if score < threshold:
                continue
            clean = {str(key): str(value) for key, value in document.metadata.items()}
            chunks.append(RetrievedChunk(
                id=clean["id"], record_type=record_type, module=clean["module"],
                content=document.page_content, score=score, metadata=clean,
            ))
        return chunks
