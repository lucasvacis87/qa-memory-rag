"""Índice local Chroma, idempotente y filtrado por tipo QA."""

from __future__ import annotations

from pathlib import Path

import chromadb

from .models import QARecord, RecordType, RetrievedChunk
from .providers import EmbeddingProvider
from .source import record_to_chunk


class IndexUnavailableError(RuntimeError):
    pass


class QAIndex:
    def __init__(self, path: Path, collection_name: str, embeddings: EmbeddingProvider) -> None:
        self.path = path
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.client = chromadb.PersistentClient(path=str(path))

    def rebuild(self, records: list[QARecord]) -> int:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        collection = self.client.create_collection(
            self.collection_name, metadata={"hnsw:space": "cosine"}
        )
        documents = [record_to_chunk(record) for record in records]
        collection.add(
            ids=[record.id for record in records],
            documents=documents,
            metadatas=[record.metadata() for record in records],
            embeddings=self.embeddings.embed(documents),
        )
        return collection.count()

    def count(self) -> int:
        try:
            return self.client.get_collection(self.collection_name).count()
        except Exception as error:
            raise IndexUnavailableError("El índice no existe. Ejecutá primero build-index.") from error

    def search(
        self, question: str, record_type: RecordType, limit: int = 2,
        threshold: float = 0.45,
    ) -> list[RetrievedChunk]:
        try:
            collection = self.client.get_collection(self.collection_name)
        except Exception as error:
            raise IndexUnavailableError("El índice no existe. Ejecutá primero build-index.") from error
        result = collection.query(
            query_embeddings=self.embeddings.embed([question]), n_results=limit,
            where={"type": record_type}, include=["documents", "metadatas", "distances"],
        )
        chunks: list[RetrievedChunk] = []
        for document, metadata, distance in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            score = max(0.0, 1.0 - float(distance))
            if score < threshold:
                continue
            clean = {str(key): str(value) for key, value in metadata.items()}
            chunks.append(RetrievedChunk(
                id=clean["id"], record_type=record_type, module=clean["module"],
                content=document, score=score, metadata=clean,
            ))
        return chunks
