"""Jinja2 HTML Template Renderer for Documentation Guides."""

from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.schemas.document import DocumentSchema
from app.core.logging import logger

TEMPLATES_DIR = Path(__file__).parent / "templates"


class HTMLRenderer:
    """Renders structured document data into HTML via Jinja2."""

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_manual_html(
        self,
        document: DocumentSchema,
        target_url: str = "",
        include_screenshots: bool = True,
    ) -> str:
        """Render complete HTML string."""
        template = self.env.get_template("manual_template.html")
        css_file = TEMPLATES_DIR / "styles.css"
        css_styles = css_file.read_text(encoding="utf-8") if css_file.exists() else ""

        html = template.render(
            document=document,
            target_url=target_url,
            generated_date=datetime.utcnow().strftime("%B %d, %Y"),
            include_screenshots=include_screenshots,
            css_styles=css_styles,
        )
        return html
