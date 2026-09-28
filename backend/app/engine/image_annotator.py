"""Image Annotation and Visual Asset Processing Engine for DocuAgent AI."""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.core.config import settings
from app.core.logging import logger
from app.core.security import sanitize_identifier


class ImageAnnotator:
    """Processes, annotates, crops, and enhances screenshots captured during recording sessions."""

    def __init__(self, session_id: str):
        self.session_id = sanitize_identifier(session_id, "session_id")
        self.session_dir = settings.SCREENSHOTS_DIR / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self._font = self._load_font(size=18)
        self._badge_font = self._load_font(size=16)

    def _load_font(self, size: int = 18) -> ImageFont.ImageFont:
        """Attempt to load a clean TTF font, falling back to default PIL bitmap font."""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "DejaVuSans-Bold.ttf",
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def process_step_image(
        self,
        step_number: int,
        step_data: Dict[str, Any],
        raw_traces: List[Dict[str, Any]],
        highlight_color: str = "#ef4444",
    ) -> Optional[Dict[str, Any]]:
        """Main entry point: generates annotated screenshot and focus crop thumbnail for a step."""
        # 1. Locate best screenshot file for this step
        raw_image_path, target_box, is_sensitive = self._resolve_step_source_image(step_data, raw_traces)
        if not raw_image_path or not raw_image_path.exists():
            logger.debug(f"No source screenshot found on disk for step #{step_number}")
            return None

        try:
            with Image.open(raw_image_path).convert("RGBA") as img:
                orig_w, orig_h = img.size

                # 2. Redact PII if input is sensitive
                if is_sensitive and target_box:
                    self._redact_bounding_box(img, target_box)

                # 3. Create Focus Crop Thumbnail (400x260)
                focus_crop_url = None
                if target_box:
                    crop_filename = f"step_{step_number:03d}_crop.jpg"
                    crop_path = self.session_dir / crop_filename
                    crop_img = self._create_focus_crop(img, target_box, crop_w=420, crop_h=260)
                    if crop_img:
                        crop_img.convert("RGB").save(crop_path, format="JPEG", quality=85)
                        focus_crop_url = f"/storage/screenshots/{self.session_id}/{crop_filename}"

                # 4. Draw Callout Badges & Highlight Outlines on Full Viewport
                annotated_filename = f"step_{step_number:03d}_annotated.jpg"
                annotated_path = self.session_dir / annotated_filename
                
                annotated_img = img.copy()
                if target_box:
                    self._draw_element_callout(
                        image=annotated_img,
                        box=target_box,
                        step_number=step_number,
                        color_hex=highlight_color,
                    )

                annotated_img.convert("RGB").save(annotated_path, format="JPEG", quality=88)
                annotated_url = f"/storage/screenshots/{self.session_id}/{annotated_filename}"

                return {
                    "step_number": step_number,
                    "raw_screenshot_url": f"/storage/screenshots/{self.session_id}/{raw_image_path.name}",
                    "annotated_screenshot_url": annotated_url,
                    "focus_crop_url": focus_crop_url,
                    "dimensions": {"width": orig_w, "height": orig_h},
                    "target_bounding_box": target_box,
                    "callout_badge": step_number,
                    "has_pii_redaction": is_sensitive,
                }
        except Exception as e:
            logger.warning(f"Failed to process and annotate step #{step_number} image: {e}")
            return None

    def _resolve_step_source_image(
        self,
        step_data: Dict[str, Any],
        raw_traces: List[Dict[str, Any]],
    ) -> Tuple[Optional[Path], Optional[Dict[str, float]], bool]:
        """Find the most appropriate raw screenshot and bounding box for a procedural step."""
        raw_action_ids = step_data.get("raw_action_ids") or []
        step_screenshot_path = step_data.get("screenshot_path") or step_data.get("screenshot_url")

        # Find matching trace object
        matched_trace = None
        for trace in raw_traces:
            if raw_action_ids and trace.get("id") in raw_action_ids:
                matched_trace = trace
                break
            if step_screenshot_path and trace.get("screenshot_url") == step_screenshot_path:
                matched_trace = trace
                break

        if not matched_trace:
            # Only fall back to first trace in single-step sessions.
            # In multi-step sessions a wrong fallback would attach step 1's
            # screenshot to every subsequent step.
            if len(raw_traces) == 1:
                matched_trace = raw_traces[0]

        if not matched_trace:
            return None, None, False

        # Extract file path
        trace_shot = matched_trace.get("screenshot_path")
        if trace_shot:
            file_path = Path(trace_shot)
        elif matched_trace.get("screenshot_url"):
            rel = matched_trace.get("screenshot_url").replace("/storage/screenshots/", "")
            file_path = settings.SCREENSHOTS_DIR / rel
        else:
            file_path = None

        # Extract bounding box & sensitive flag
        target_el = matched_trace.get("target_element") or {}
        bounding_box = target_el.get("bounding_box")
        input_type = (target_el.get("input_type") or "").lower()
        is_sensitive = input_type in ("password", "token", "secret", "cvv")

        return file_path, bounding_box, is_sensitive

    def _draw_element_callout(
        self,
        image: Image.Image,
        box: Dict[str, float],
        step_number: int,
        color_hex: str = "#ef4444",
    ):
        """Draw neon outline box, shadow glow, and numbered callout badge."""
        draw = ImageDraw.Draw(image)
        x = int(box.get("x", box.get("left", 0)))
        y = int(box.get("y", box.get("top", 0)))
        w = int(box.get("width", 0))
        h = int(box.get("height", 0))

        if w <= 0 or h <= 0:
            return

        # 1. Draw glowing highlight rectangle
        outline_width = 3
        draw.rectangle(
            [x - 2, y - 2, x + w + 2, y + h + 2],
            outline=color_hex,
            width=outline_width,
        )

        # 2. Draw Numbered Step Badge (pill or circle) at top-left of element
        badge_radius = 14
        badge_cx = max(badge_radius + 4, x - 4)
        badge_cy = max(badge_radius + 4, y - 4)

        # Badge shadow
        draw.ellipse(
            [badge_cx - badge_radius - 1, badge_cy - badge_radius - 1, badge_cx + badge_radius + 1, badge_cy + badge_radius + 1],
            fill="#0f172a",
        )
        # Badge fill (accent color)
        draw.ellipse(
            [badge_cx - badge_radius, badge_cy - badge_radius, badge_cx + badge_radius, badge_cy + badge_radius],
            fill=color_hex,
        )

        # Badge text (Step Number)
        text = str(step_number)
        bbox = self._badge_font.getbbox(text) if hasattr(self._badge_font, "getbbox") else (0, 0, 8, 12)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = badge_cx - text_w // 2
        text_y = badge_cy - text_h // 2 - 1

        draw.text((text_x, text_y), text, fill="#ffffff", font=self._badge_font)

    def _create_focus_crop(
        self,
        image: Image.Image,
        box: Dict[str, float],
        crop_w: int = 420,
        crop_h: int = 260,
    ) -> Optional[Image.Image]:
        """Crop and center viewport around target element with balanced padding."""
        x = int(box.get("x", box.get("left", 0)))
        y = int(box.get("y", box.get("top", 0)))
        w = int(box.get("width", 0))
        h = int(box.get("height", 0))

        if w <= 0 or h <= 0:
            return None

        # Element center
        cx = x + w // 2
        cy = y + h // 2

        img_w, img_h = image.size

        # Compute crop box centered at (cx, cy)
        left = max(0, cx - crop_w // 2)
        top = max(0, cy - crop_h // 2)
        right = min(img_w, left + crop_w)
        bottom = min(img_h, top + crop_h)

        # Adjust if hitting right/bottom edges
        if right - left < crop_w:
            left = max(0, right - crop_w)
        if bottom - top < crop_h:
            top = max(0, bottom - crop_h)

        crop = image.crop((left, top, right, bottom))
        return crop

    def _redact_bounding_box(self, image: Image.Image, box: Dict[str, float]):
        """Apply a heavy blur and privacy overlay directly over sensitive coordinates."""
        x = int(box.get("x", box.get("left", 0)))
        y = int(box.get("y", box.get("top", 0)))
        w = int(box.get("width", 0))
        h = int(box.get("height", 0))

        if w <= 0 or h <= 0:
            return

        box_tuple = (x, y, x + w, y + h)
        try:
            cropped_sensitive = image.crop(box_tuple)
            blurred = cropped_sensitive.filter(ImageFilter.GaussianBlur(radius=15))
            # Pass the alpha channel as mask so RGBA compositing is correct.
            mask = blurred.split()[3] if blurred.mode == "RGBA" else None
            image.paste(blurred, box_tuple[:2], mask)

            # Draw privacy stripe pattern overlay
            draw = ImageDraw.Draw(image)
            draw.rectangle(box_tuple, fill=(15, 23, 42, 180), outline="#ef4444", width=1)
            draw.text((x + 6, y + (h // 2) - 6), "•••••••• [REDACTED]", fill="#94a3b8", font=self._badge_font)
        except Exception as e:
            logger.debug(f"Failed to redact bounding box: {e}")
