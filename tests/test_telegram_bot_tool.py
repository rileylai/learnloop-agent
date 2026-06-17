import asyncio

from src.tools import (
    TelegramBotClient,
    TelegramBotFileDownloadError,
    TelegramBotSendError,
    TelegramBotTool,
    ToolContext,
)


class _FailingTelegramClient(TelegramBotClient):
    def send_message(self, *, chat_id: str, text: str):
        _ = chat_id
        _ = text
        raise TelegramBotSendError(
            "Telegram request failed: https://api.telegram.org/bot123456:ABC/sendMessage "
            "Authorization=Bearer sk-live-secret raw_text='private source note'"
        )

    def download_file(self, *, file_id: str):
        _ = file_id
        raise TelegramBotFileDownloadError(
            "Telegram file download failed: https://api.telegram.org/file/bot123456:ABC/document/file.pdf "
            "source_text='private source note'"
        )


def test_telegram_bot_tool_redacts_sensitive_send_error_message() -> None:
    tool = TelegramBotTool(_FailingTelegramClient())

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-telegram-send"),
            arguments={
                "action": "send_message",
                "chat_id": "12345",
                "text": "hello",
            },
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "TELEGRAM_SEND_FAILED"
    assert result.error.message == (
        "Telegram request failed: https://api.telegram.org/bot[REDACTED]/sendMessage "
        "Authorization=[REDACTED] raw_text=[REDACTED_PRIVATE_TEXT]"
    )


def test_telegram_bot_tool_redacts_sensitive_download_error_message() -> None:
    tool = TelegramBotTool(_FailingTelegramClient())

    result = asyncio.run(
        tool.run(
            context=ToolContext(workflow_id="wf-telegram-download"),
            arguments={
                "action": "download_file",
                "file_id": "file-123",
            },
        )
    )

    assert result.is_error is True
    assert result.error is not None
    assert result.error.code == "TELEGRAM_FILE_DOWNLOAD_FAILED"
    assert result.error.message == (
        "Telegram file download failed: "
        "https://api.telegram.org/file/bot[REDACTED]/document/file.pdf "
        "source_text=[REDACTED_PRIVATE_TEXT]"
    )
