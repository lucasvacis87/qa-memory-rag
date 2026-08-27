"""Índice local Chroma administrado mediante la integración de LangChain."""

from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from .models import QARecord, RecordType, RetrievedChunk
from .source import record_to_chunk


class IndexUnavailableError(RuntimeError):
    """Indica que todavía no existe una colección consultable."""

    pass


class QAIndex:
    """Construye y consulta la colección vectorial de registros QA."""

    def __init__(self, path: Path, collection_name: str, embeddings: Embeddings) -> None:
        """Abre un vector store Chroma persistente con embeddings LangChain."""
        self.path = path
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.store = self._open_store()

    def _open_store(self) -> Chroma:
        """Crea o abre la colección configurada usando distancia coseno."""
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.path),
            collection_metadata={"hnsw:space": "cosine"},
        )

    def _collection_count(self) -> int:
        """Cuenta IDs persistidos sin exponer detalles internos de Chroma."""
        return len(self.store.get(include=[])["ids"])

    def rebuild(self, records: list[QARecord]) -> int:
        """Reemplaza la colección e indexa todos los registros."""
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
        """Devuelve la cantidad de chunks indexados."""
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
        """Recupera los chunks más similares de un tipo determinado."""
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
