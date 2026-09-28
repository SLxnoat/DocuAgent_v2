"""WeasyPrint PDF generation engine."""

from pathlib import Path
import weasyprint
from weasyprint import HTML, URLFetcher
from app.schemas.document import DocumentSchema
from app.exporter.html_renderer import HTMLRenderer, TEMPLATES_DIR
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ExportError


class SecureURLFetcher(URLFetcher):
    """Restricts WeasyPrint to local templates and storage dirs — prevents SSRF and LFI."""

    def fetch(self, url: str, **kwargs):
        if url.startswith("file://"):
            file_path = Path(url[7:])
            try:
                resolved = file_path.resolve()
                storage_ok = resolved.is_relative_to(settings.STORAGE_DIR.resolve())
                template_ok = resolved.is_relative_to(TEMPLATES_DIR.resolve())
                if storage_ok or template_ok:
                    return super().fetch(url, **kwargs)
            except Exception:
                pass
            logger.warning(f"Blocked unauthorized local file access in PDF generator: {url}")
            raise ValueError(f"Access to local file {url} is forbidden.")

        # Block all remote network fetches during PDF compilation
        logger.warning(f"Blocked remote network fetch in PDF generator: {url}")
        raise ValueError(f"Remote URL fetches are forbidden during PDF compilation: {url}")


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
            # Compile using WeasyPrint with secure url_fetcher
            HTML(
                string=html_content,
                base_url=str(settings.BASE_DIR),
                url_fetcher=SecureURLFetcher(),
            ).write_pdf(target=str(output_path))
            logger.info(f"Generated PDF export at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to compile PDF: {e}")
            raise ExportError(f"PDF compilation failed: {str(e)}")

