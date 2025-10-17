"""Ingest utilities (fase 1 - placeholder).

Proporciona funciones auxiliares que el futuro comando de management
`ingest_pdfs` utilizará para: leer PDFs, chunkear y generar embeddings,
guardando un cache en `EMBED_CACHE_PATH`.
"""
from __future__ import annotations
import os
from typing import List, Dict, Any

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None  # type: ignore

from .retrieval import embed_texts, EMBED_CACHE_PATH, ChunkMeta


def chunk_text(text: str, max_len: int = 700, overlap: int = 120):
    text = text.replace('\r', '')
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks: List[str] = []
    for para in paragraphs:
        if len(para) <= max_len:
            chunks.append(para)
        else:
            start = 0
            while start < len(para):
                end = start + max_len
                part = para[start:end]
                chunks.append(part)
                if end >= len(para):
                    break
                start = end - overlap
    return chunks


def ingest_documents(docs: List[Dict[str, Any]]):  # pragma: no cover
    """docs: list de { 'doc': nombre, 'page': page_int, 'text': contenido }"""
    if np is None:
        raise RuntimeError("numpy no disponible para ingest")
    # Generar embeddings
    embeddings = embed_texts([d['text'] for d in docs])
    meta_serializable = []
    for idx, d in enumerate(docs):
        meta_serializable.append({
            'doc': d['doc'],
            'page': d['page'],
            'text': d['text'],
            'vector_index': idx,
        })
    os.makedirs(os.path.dirname(EMBED_CACHE_PATH), exist_ok=True)
    np.savez_compressed(EMBED_CACHE_PATH, embeddings=embeddings, meta=meta_serializable)
    return len(docs)
