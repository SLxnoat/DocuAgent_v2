"""File storage utility for managing screenshots, exports, and document artifacts."""

import os
import aiofiles
from pathlib import Path
from typing import Optional, List
from app.core.config import settings
from app.core.logging import logger


class FileStore:
    """Handles local disk and artifact persistence."""

    @classmethod
    async def save_file(cls, relative_subpath: str, content: bytes) -> Path:
        """Persist binary file to storage dir."""
        destination = settings.STORAGE_DIR / relative_subpath
        destination.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(destination, "wb") as f:
            await f.write(content)
        logger.info(f"Saved file to {destination}")
        return destination

    @classmethod
    async def read_file(cls, relative_subpath: str) -> Optional[bytes]:
        """Read binary file content from storage."""
        target = settings.STORAGE_DIR / relative_subpath
        if not target.exists():
            return None
        async with aiofiles.open(target, "rb") as f:
            return await f.read()

    @classmethod
    def get_screenshot_files(cls, session_id: str) -> List[str]:
        """List all screenshot filenames for a given session."""
        session_folder = settings.SCREENSHOTS_DIR / session_id
        if not session_folder.exists():
            return []
        return sorted([f.name for f in session_folder.glob("*.png")])
