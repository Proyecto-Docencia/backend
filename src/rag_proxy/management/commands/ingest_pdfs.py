from __future__ import annotations
import os
from pathlib import Path
from typing import List, Dict, Any

from django.core.management.base import BaseCommand, CommandParser

try:
    from pypdf import PdfReader  # type: ignore
except ImportError:  # pragma: no cover
    PdfReader = None  # type: ignore

from rag_proxy.ingest import chunk_text, ingest_documents


class Command(BaseCommand):
    help = "Ingesta PDFs para construir embeddings RAG (fase 1 local)."

    def add_arguments(self, parser: CommandParser) -> None:  # pragma: no cover
        parser.add_argument(
            "--dir",
            dest="directory",
            default=os.environ.get("RAG_PDFS_DIR", "./pdfs"),
            help="Directorio que contiene los PDFs a ingestar",
        )
        parser.add_argument(
            "--limit",
            dest="limit",
            type=int,
            default=None,
            help="Limitar número de PDFs (para pruebas)",
        )

    def handle(self, *args, **options):  # pragma: no cover (IO test manual)
        if PdfReader is None:
            self.stderr.write(self.style.ERROR("La librería pypdf no está instalada."))
            return

        directory = Path(options["directory"]).resolve()
        if not directory.exists():
            self.stderr.write(self.style.ERROR(f"Directorio no existe: {directory}"))
            return

        pdf_files = sorted([p for p in directory.rglob("*.pdf")])
        if not pdf_files:
            self.stderr.write(self.style.WARNING("No se encontraron PDFs"))
            return
        if options.get("limit"):
            pdf_files = pdf_files[: options["limit"]]

        all_docs: List[Dict[str, Any]] = []
        total_chunks = 0
        for pdf_path in pdf_files:
            try:
                reader = PdfReader(str(pdf_path))
            except Exception as e:  # pragma: no cover
                self.stderr.write(self.style.WARNING(f"No se pudo leer {pdf_path.name}: {e}"))
                continue
            for page_index, page in enumerate(reader.pages):
                try:
                    raw_text = page.extract_text() or ""
                except Exception:
                    raw_text = ""
                if not raw_text.strip():
                    continue
                chunks = chunk_text(raw_text)
                for ch in chunks:
                    all_docs.append({
                        "doc": pdf_path.name,
                        "page": page_index + 1,
                        "text": ch,
                    })
                total_chunks += len(chunks)
            self.stdout.write(self.style.NOTICE(f"Procesado {pdf_path.name}"))

        if not all_docs:
            self.stderr.write(self.style.WARNING("No se generaron chunks"))
            return

        self.stdout.write(f"Generando embeddings para {total_chunks} chunks...")
        try:
            count = ingest_documents(all_docs)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error generando embeddings: {e}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Ingesta completada. Chunks: {count}"))
