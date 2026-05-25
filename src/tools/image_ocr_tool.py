from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, List

from src.tools.base import Tool
from src.tools.models import ToolContext, ToolResult, ToolSpec


@dataclass
class OCRImageInput:
    file_name: str
    file_bytes: bytes


@dataclass
class ParsedImageOCR:
    raw_text: str
    image_count: int


class ImageOCRParserClientError(Exception):
    pass


class ImageOCRParserClient:
    def parse_images(self, *, images: List[OCRImageInput]) -> ParsedImageOCR:
        raise NotImplementedError


class TesseractImageOCRParserClient(ImageOCRParserClient):
    def parse_images(self, *, images: List[OCRImageInput]) -> ParsedImageOCR:
        if not images:
            raise ImageOCRParserClientError("No images provided for OCR")

        try:
            import pytesseract
            from PIL import Image
        except ModuleNotFoundError as exc:
            raise ImageOCRParserClientError(
                "pytesseract or pillow dependency is missing"
            ) from exc

        extracted_sections: List[str] = []
        for index, image in enumerate(images, start=1):
            try:
                opened = Image.open(BytesIO(image.file_bytes))
            except Exception as exc:
                raise ImageOCRParserClientError(
                    f"Failed to open image '{image.file_name}': {exc}"
                ) from exc

            try:
                text = pytesseract.image_to_string(opened)
            except Exception as exc:
                raise ImageOCRParserClientError(
                    f"Failed to OCR image '{image.file_name}': {exc}"
                ) from exc

            normalized_text = text.strip()
            if not normalized_text:
                continue

            extracted_sections.append(
                f"[Image {index}: {image.file_name}]\n{normalized_text}"
            )

        raw_text = "\n\n".join(extracted_sections).strip()
        if not raw_text:
            raise ImageOCRParserClientError("No extractable text found in images")

        return ParsedImageOCR(raw_text=raw_text, image_count=len(images))


class ImageOCRTool(Tool):
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="image_ocr_parser",
            description="Extract normalized text from multiple images in input order.",
            input_schema={
                "type": "object",
                "required": ["images"],
                "properties": {
                    "images": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["file_name", "file_bytes_base64"],
                            "properties": {
                                "file_name": {"type": "string"},
                                "file_bytes_base64": {"type": "string"},
                            },
                        },
                    }
                },
            },
            output_schema={
                "type": "object",
                "required": ["raw_text", "image_count", "char_count"],
                "properties": {
                    "raw_text": {"type": "string"},
                    "image_count": {"type": "integer"},
                    "char_count": {"type": "integer"},
                },
            },
        )

    def __init__(self, parser_client: ImageOCRParserClient) -> None:
        self._parser_client = parser_client

    async def run(self, context: ToolContext, arguments: Dict[str, Any]) -> ToolResult:
        _ = context
        images_argument = arguments.get("images")
        if not isinstance(images_argument, list) or not images_argument:
            return ToolResult.failure(
                code="INVALID_ARGUMENT",
                message="images must be a non-empty list",
            )

        images: List[OCRImageInput] = []
        for index, item in enumerate(images_argument, start=1):
            if not isinstance(item, dict):
                return ToolResult.failure(
                    code="INVALID_ARGUMENT",
                    message=f"images[{index}] must be an object",
                )
            file_name = str(item.get("file_name", "")).strip()
            if not file_name:
                return ToolResult.failure(
                    code="INVALID_ARGUMENT",
                    message=f"images[{index}].file_name is required",
                )
            encoded = str(item.get("file_bytes_base64", "")).strip()
            if not encoded:
                return ToolResult.failure(
                    code="INVALID_ARGUMENT",
                    message=f"images[{index}].file_bytes_base64 is required",
                )
            try:
                file_bytes = base64.b64decode(encoded, validate=True)
            except (ValueError, binascii.Error) as exc:
                return ToolResult.failure(
                    code="INVALID_ARGUMENT",
                    message=f"images[{index}].file_bytes_base64 is invalid: {exc}",
                )
            if not file_bytes:
                return ToolResult.failure(
                    code="INVALID_ARGUMENT",
                    message=f"images[{index}] decoded to empty bytes",
                )
            images.append(OCRImageInput(file_name=file_name, file_bytes=file_bytes))

        try:
            parsed = self._parser_client.parse_images(images=images)
        except ImageOCRParserClientError as exc:
            return ToolResult.failure(
                code="OCR_FAILED",
                message=str(exc),
            )

        normalized_raw_text = parsed.raw_text.strip()
        if not normalized_raw_text:
            return ToolResult.failure(
                code="OCR_FAILED",
                message="No extractable text found in images",
            )

        return ToolResult.success(
            content=(
                f"parsed image_count={parsed.image_count} "
                f"char_count={len(normalized_raw_text)}"
            ),
            structured_content={
                "raw_text": normalized_raw_text,
                "image_count": parsed.image_count,
                "char_count": len(normalized_raw_text),
            },
        )
