"""RAG retrieval utilities (fase 1 - stub + estructura preparada).

Esta capa está diseñada para poder reemplazarse fácilmente en el futuro
por Azure AI Search u otro vector store. Mantén la interfaz estable.
"""
from __future__ import annotations
import os
import threading
import time
from dataclasses import dataclass
from typing import List, Sequence, Optional, Dict, Any

try:
    import numpy as np  # type: ignore
except ImportError:  # pragma: no cover
    np = None  # type: ignore

_EMBED_LOCK = threading.Lock()
_EMBED_MODEL = None  # lazy loaded sentence-transformers model
_MATRIX = None       # numpy matrix (n_chunks x dim)
_CHUNKS: List["ChunkMeta"] = []

DEFAULT_MODEL = os.environ.get("RAG_MODEL_SENTENCE", "all-MiniLM-L6-v2")
EMBED_CACHE_PATH = os.environ.get("RAG_EMBED_CACHE", "/app/rag_cache/embeddings.npz")
TOP_K_DEFAULT = int(os.environ.get("RAG_TOP_K", "5"))
MIN_SCORE = float(os.environ.get("RAG_MIN_SCORE", "0.25"))
BACKEND_KIND = os.environ.get("RAG_BACKEND", "local").lower()  # 'local' | 'azure'
AZURE_SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX", "educacion-docs")


@dataclass
class ChunkMeta:
    doc: str
    page: int
    text: str
    vector_index: int


def _lazy_load_model():  # pragma: no cover (IO heavy)
    global _EMBED_MODEL
    if _EMBED_MODEL is not None:
        return _EMBED_MODEL
    try:
        from sentence_transformers import SentenceTransformer  # heavy import local
    except ImportError:
        print("[RAG] sentence-transformers no instalado. BACKEND_KIND=local no podrá hacer retrieval.")
        return None
    try:
        _EMBED_MODEL = SentenceTransformer(DEFAULT_MODEL)
    except Exception as e:  # pragma: no cover
        print(f"[RAG] Error cargando modelo de embeddings: {e}")
        return None
    return _EMBED_MODEL


def _load_embeddings_if_available():  # pragma: no cover
    global _MATRIX, _CHUNKS
    if _MATRIX is not None:
        return
    if np is None:
        return
    if not os.path.exists(EMBED_CACHE_PATH):
        return
    try:
        data = np.load(EMBED_CACHE_PATH, allow_pickle=True)
        _MATRIX = data["embeddings"]
        meta_list = data["meta"].tolist()
        _CHUNKS = [ChunkMeta(**m) for m in meta_list]
    except Exception as e:  # pragma: no cover
        print(f"[RAG] No se pudo cargar cache de embeddings: {e}")


def ensure_ready():  # pragma: no cover
    with _EMBED_LOCK:
        if _MATRIX is None:
            _load_embeddings_if_available()


def embed_texts(texts: Sequence[str]):  # pragma: no cover
    model = _lazy_load_model()
    return model.encode(list(texts), normalize_embeddings=True)


def _search_local(query: str, top_k: Optional[int]) -> List[Dict[str, Any]]:
    ensure_ready()
    if np is None or _MATRIX is None or not _CHUNKS:
        return []
    top_k = top_k or TOP_K_DEFAULT
    model = _lazy_load_model()
    if model is None:
        return []
    q_vec = model.encode([query], normalize_embeddings=True)[0]
    sims = (_MATRIX @ q_vec).tolist()
    scored = []
    for chunk, score in zip(_CHUNKS, sims):
        if score < MIN_SCORE:
            continue
        scored.append({
            "score": float(score),
            "doc": chunk.doc,
            "page": chunk.page,
            "text": chunk.text,
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def _search_azure(query: str) -> List[Dict[str, Any]]:  # pragma: no cover
    """Stub Azure AI Search. Implementar cuando se provisionen recursos.

    Plan previsto:
      1. Generar embedding de la query (Azure OpenAI Embeddings) o usar vector query integrada si índice ya la soporta.
      2. Llamar a endpoint: POST {endpoint}/indexes/{index}/docs/search?api-version=2024-07-01
      3. Incluir en body: {"vectorQueries": [...], "top": K}
      4. Mapear campos: doc_title -> doc, page -> page, content -> text, score -> @search.score
    """
    if not (AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY):
        return []
    # Devuelve vacío hasta implementar integración real.
    return []


def search(query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
    if BACKEND_KIND == "azure":
        return _search_azure(query)
    return _search_local(query, top_k)


def format_context(chunks: List[Dict[str, Any]]) -> str:
    lines = []
    for c in chunks:
        preview = c["text"].strip().replace("\n", " ")
        if len(preview) > 400:
            preview = preview[:400] + "…"
        lines.append(f"[Fuente: {c['doc']} | Página {c['page']}]\n{preview}\n")
    return "\n".join(lines)
