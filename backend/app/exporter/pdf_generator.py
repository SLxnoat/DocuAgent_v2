"""WeasyPrint PDF generation engine."""

from pathlib import Path
from weasyprint import HTML
from app.schemas.document import DocumentSchema
from app.exporter.html_renderer import HTMLRenderer
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ExportError


class PDFGenerator:
    """Compiles HTML into high-quality PDF documents."""

    def __init__(self):
        self.html_renderer = HTMLRenderer()

    def generate_pdf(
        self,
        document: DocumentSchema,
        output_path: Path,
        target_url: str = "",
        include_screenshots: bool = True,
    ) -> Path:
        """Render document and compile to PDF file on disk."""
        try:
            html_content = self.html_renderer.render_manual_html(
                document=document,
                target_url=target_url,
                include_screenshots=include_screenshots,
            )

            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Compile using WeasyPrint
            HTML(string=html_content, base_url=str(settings.BASE_DIR)).write_pdf(target=str(output_path))
            logger.info(f"Generated PDF export at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to compile PDF: {e}")
            raise ExportError(f"PDF compilation failed: {str(e)}")
