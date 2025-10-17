# RAG (Retrieval-Augmented Generation) - Fase 1

Este backend incluye una primera implementación local de RAG reutilizando Gemini como modelo generativo.

## Flujo
1. Ingesta de PDFs → se generan *chunks* y embeddings.
2. Los embeddings se guardan en un archivo comprimido (`EMBED_CACHE_PATH`).
3. El endpoint `POST /api/rag/` realiza retrieval (cosine) y construye un prompt contextual para Gemini.
4. Si no hay contexto relevante, se hace fallback sin documentos (`fallback_sin_contexto = true`).

## Variables de entorno relevantes
| Variable | Descripción | Default |
|----------|-------------|---------|
| ENABLE_RAG | Activa/desactiva el endpoint RAG | `0` (desactivado por defecto) |
| RAG_PDFS_DIR | Directorio con PDFs para ingesta | `./pdfs` |
| RAG_EMBED_CACHE | Ruta donde se guarda cache de embeddings | `/app/rag_cache/embeddings.npz` |
| RAG_MODEL_SENTENCE | Modelo sentence-transformers | `all-MiniLM-L6-v2` |
| RAG_TOP_K | Nº de chunks máximo en respuesta | `5` |
| RAG_MIN_SCORE | Umbral de similitud (cosine) | `0.25` |

## Ingesta de PDFs (modo local con dependencias instaladas)
Coloca tus PDFs en el directorio configurado (por ejemplo `backend/pdfs/`) y ejecuta:

### Build con RAG habilitado (instala dependencias pesadas)
```bash
docker build -t proyecto-backend-rag --build-arg ENABLE_RAG=1 backend
```

### Build sin RAG (imagen más liviana)
```bash
docker build -t proyecto-backend-core backend
```

### Ejecutar ingesta (sólo si la imagen se construyó con RAG)
```bash
docker run --rm -v $(pwd)/backend/pdfs:/app/pdfs proyecto-backend-rag \
  python manage.py ingest_pdfs --dir /app/pdfs
```

Esto generará el archivo de cache con embeddings. **Reinicia** el contenedor/backend después para que el endpoint los cargue en memoria.

## Endpoint RAG
`POST /api/rag/`

Payload:
```json
{ "mensaje_usuario": "¿Cómo introducir fracciones?", "top_k": 5 }
```

Respuesta (ejemplo simplificado):
```json
{
  "respuesta_ia": "...",
  "fuentes": [
    {"doc": "Capitulo2.pdf", "page": 4, "score": 0.71, "preview": "Las fracciones ..."}
  ],
  "fallback_sin_contexto": false,
  "latencia_ms": 640,
  "enabled": true
}
```

## Buenas prácticas (próximas fases)
- Migrar a Azure AI Search para manejo de miles de chunks.
- Añadir campo `metadata` al modelo `Chat` si se quiere auditoría de fuentes usadas.
- Implementar anonimización de datos sensibles si aplica.
- Agregar re-rank híbrido (BM25 + vector) cuando escale.

## Notas
- Esta fase NO modifica el endpoint de chat existente (`/api/chat/crear/`).
- Si `ENABLE_RAG=0`, el endpoint devuelve 503.
