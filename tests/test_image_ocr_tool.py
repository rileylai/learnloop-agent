from __future__ import annotations

import asyncio
import base64

from src.tools import (
    ImageOCRParserClient,
    ImageOCRParserClientError,
    ImageOCRTool,
    OCRImageInput,
    ParsedImageOCR,
    ToolContext,
)


class _FakeImageOCRParserClient(ImageOCRParserClient):
    def __init__(
        self,
        *,
        raw_text: str = "Extracted OCR text",
        should_fail: bool = False,
    ) -> None:
        self._raw_text = raw_text
        self._should_fail = should_fail

    def parse_images(self, *, images: list[OCRImageInput]) -> ParsedImageOCR:
        _ = images
        if self._should_fail:
            raise ImageOCRParserClientError("ocr failed")
        return ParsedImageOCR(raw_text=self._raw_text, image_count=2)


def test_image_ocr_tool_returns_extracted_text() -> None:
    tool = ImageOCRTool(_FakeImageOCRParserClient(raw_text="line-1\nline-2"))

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-1"),
            arguments={
                "images": [
                    {
                        "file_name": "img1.png",
                        "file_bytes_base64": base64.b64encode(b"image-1").decode("ascii"),
                    },
                    {
                        "file_name": "img2.png",
                        "file_bytes_base64": base64.b64encode(b"image-2").decode("ascii"),
                    },
                ]
            },
        )
    )

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["raw_text"] == "line-1\nline-2"
    assert result.structured_content["image_count"] == 2
    assert result.structured_content["char_count"] == len("line-1\nline-2")


def test_image_ocr_tool_rejects_empty_images() -> None:
    tool = ImageOCRTool(_FakeImageOCRParserClient())

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-2"),
            arguments={"images": []},
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "INVALID_ARGUMENT"


def test_image_ocr_tool_maps_client_error_to_ocr_failed() -> None:
    tool = ImageOCRTool(_FakeImageOCRParserClient(should_fail=True))

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-3"),
            arguments={
                "images": [
                    {
                        "file_name": "img1.png",
                        "file_bytes_base64": base64.b64encode(b"image-1").decode("ascii"),
                    }
                ]
            },
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "OCR_FAILED"
    assert result.error.message == "ocr failed"
