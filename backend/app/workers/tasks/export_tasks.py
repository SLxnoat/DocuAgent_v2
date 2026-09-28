"""Celery tasks for async PDF and HTML document compilation."""

from pathlib import Path
from app.workers.celery_app import celery
from app.schemas.document import DocumentSchema
from app.exporter.pdf_generator import PDFGenerator
from app.core.config import settings
from app.core.logging import logger


@celery.task(bind=True, name="tasks.generate_pdf_export")
def generate_pdf_export_task(self, document_data: dict, target_url: str):
    """Generate WeasyPrint PDF artifact asynchronously."""
    logger.info(f"Generating PDF for document {document_data.get('id')}")
    doc = DocumentSchema(**document_data)
    generator = PDFGenerator()
    
    out_filename = f"{doc.id}.pdf"
    out_path = settings.EXPORTS_DIR / out_filename
    
    generator.generate_pdf(
        document=doc,
        output_path=out_path,
        target_url=target_url,
        include_screenshots=True,
    )
    
    return {
        "document_id": doc.id,
        "pdf_path": str(out_path),
        "download_url": f"/api/v1/documents/{doc.id}/download?format=pdf",
    }
