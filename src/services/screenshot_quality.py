from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, List

if TYPE_CHECKING:
    from src.orchestrators.supplement_proposal_schema import SupplementProposalSchema


_URL_LINE_PATTERN = re.compile(
    r"^(?:(?:https?|ftp|file|chrome|edge|about):/{1,3}|www\.)\S+$",
    re.IGNORECASE,
)
_DOMAIN_LINE_PATTERN = re.compile(
    r"^(?:[a-z0-9-]+\.)+(?:com|net|org|io|dev|ai|app|co|tw|cn|jp|uk)(?:/\S*)?$",
    re.IGNORECASE,
)
_ASCII_TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_+#./:-]{1,}")
_CJK_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
_CJK_RUN_PATTERN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]{2,}")
_SENTENCE_PATTERN = re.compile(r"[.!?。！？]+")
_NUMBER_PATTERN = re.compile(
    r"(?<![A-Za-z])(?:\d+(?:[.,]\d+)?%?|v\d+(?:\.\d+)+)(?![A-Za-z])",
    re.IGNORECASE,
)
_TECHNICAL_ATOM_PATTERN = re.compile(
    r"`[^`\n]+`|https?://\S+|(?<!\w)--?[A-Za-z][A-Za-z0-9_-]*|"
    r"(?<!\w)[A-Za-z][A-Za-z0-9_]*(?:[./:#][A-Za-z0-9_./:#-]+)(?!\w)",
    re.IGNORECASE,
)

_BROWSER_CHROME_LINES = frozenset(
    {
        "back",
        "forward",
        "reload",
        "refresh",
        "home",
        "new tab",
        "search tabs",
        "bookmarks",
        "bookmark",
        "extensions",
        "share",
        "translate",
        "返回",
        "前進",
        "前进",
        "重新整理",
        "刷新",
        "首頁",
        "首页",
        "新分頁",
        "新分页",
        "分頁",
        "分页",
        "搜尋分頁",
        "搜索标签页",
        "書籤",
        "书签",
        "擴充功能",
        "扩展程序",
        "分享",
        "翻譯",
        "翻译",
    }
)

_TRADITIONAL_OUTPUT_REQUIRED = (
    ("会", "會"),
    ("后", "後"),
    ("内容", "內容"),
    ("处理", "處理"),
    ("准备", "準備"),
    ("任务", "任務"),
    ("延迟", "延遲"),
    ("服务", "服務"),
    ("系统", "系統"),
    ("学习", "學習"),
    ("总结", "總結"),
    ("实践", "實踐"),
    ("建议", "建議"),
    ("浏览器", "瀏覽器"),
    ("页面", "頁面"),
    ("数据", "資料"),
)
_GENERIC_SCREENSHOT_TITLES = frozenset(
    {
        "screenshot summary",
        "screenshot proposal",
        "screenshot supplement",
        "learning notes",
        "learning summary",
        "ocr summary",
        "image summary",
    }
)

# These words describe the relationship between a proposal and its source.
# They are intentionally limited to reporting/structural language. Content
# words still need a source token or an explicitly supported synonym.
_PROPOSAL_FRAME_TOKENS = frozenset(
    {
        "a",
        "after",
        "all",
        "also",
        "an",
        "and",
        "are",
        "as",
        "at",
        "before",
        "both",
        "by",
        "can",
        "command",
        "content",
        "describes",
        "described",
        "during",
        "each",
        "for",
        "from",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "section",
        "service",
        "screenshots",
        "source",
        "states",
        "summary",
        "text",
        "that",
        "the",
        "then",
        "these",
        "this",
        "those",
        "through",
        "to",
        "via",
        "was",
        "were",
        "with",
    }
)

# A small synonym lexicon makes the validator tolerant of ordinary
# paraphrase without turning it into a semantic judge. Unknown product names,
# commands, quantities, and claim words are still rejected below.
_SYNONYM_GROUPS = (
    (
        "describe",
        "describes",
        "described",
        "show",
        "shows",
        "shown",
        "state",
        "states",
        "explain",
        "explains",
        "explained",
        "indicate",
        "indicates",
        "mention",
        "mentions",
        "outline",
        "outlines",
        "summarize",
        "summarizes",
        "capture",
        "captures",
        "highlight",
        "highlights",
        "illustrate",
        "illustrates",
        "present",
        "presents",
        "focus",
        "focuses",
        "detail",
        "details",
    ),
    ("start", "starts", "started", "begin", "begins", "began", "launch", "launches", "launched"),
    ("available", "availability", "ready", "readiness"),
    ("process", "processes", "processed", "processing", "handle", "handles", "handled", "execute", "executes", "executed", "run", "runs", "running"),
    ("use", "uses", "using", "employ", "employs", "employed"),
    ("perform", "performs", "performed", "carry", "carries", "carried", "do", "does"),
    (
        "include",
        "includes",
        "included",
        "contain",
        "contains",
        "contained",
        "list",
        "lists",
    ),
    ("rollout", "rolling", "rollout"),
    ("new", "updated", "update", "updates"),
    ("job", "jobs", "task", "tasks", "work", "works"),
    ("step", "steps", "gradually", "incrementally", "sequence", "flow"),
    ("note", "notes", "point", "points", "item", "items"),
    ("source", "screen", "screenshot", "image", "document"),
    ("process", "workflow", "operation", "operations"),
    ("control", "controls", "determine", "determines", "coordinate", "coordinates"),
)
_SYNONYM_TO_CANONICAL = {
    token: group[0]
    for group in _SYNONYM_GROUPS
    for token in group
}

# Words such as "process" and "ready" can be introduced by a faithful
# summary even when the OCR used a different verb. They are not product or
# domain atoms, and therefore do not by themselves constitute source evidence.
_SAFE_PARAPHRASE_TOKENS = frozenset(
    {
        "begins",
        "better",
        "command",
        "captures",
        "contains",
        "document",
        "efficient",
        "first",
        "follows",
        "gradual",
        "highlights",
        "information",
        "key",
        "later",
        "main",
        "method",
        "overview",
        "primary",
        "process",
        "ready",
        "second",
        "shows",
        "service",
        "summarizes",
        "startup",
        "step",
        "steps",
        "topic",
        "topics",
        "updated",
        "way",
        "when",
        "once",
        "next",
        "finally",
    }
)

_ADVICE_PATTERN = re.compile(
    r"\b(?:should|recommend(?:ed|ation)?|consider|try|must|need(?:s)? to|"
    r"use|avoid|you can)\b|"
    r"(?:建議|建议|應該|应该|請|请|必須|必须|務必|务必|需要|可以|避免|推薦|推荐)"
)
_CONCLUSION_PATTERN = re.compile(
    r"\b(?:improv(?:e|es|ed|ement)|enhanc(?:e|es|ed|ement)|"
    r"reduc(?:e|es|ed|tion)|increas(?:e|es|ed)|decreas(?:e|es|ed)|"
    r"ensur(?:e|es|ed)|guarante(?:e|es|d)|prevent(?:s|ed)?|"
    r"caus(?:e|es|ed)|lead(?:s|ing)? to|result(?:s|ed)? in|"
    r"therefore|thus|faster|better|more efficient|important|benefit|advantage)\b|"
    r"(?:提升|改善|降低|增加|減少|减少|確保|确保|保證|保证|導致|导致|因此|所以|"
    r"更快|更有效率|重要|優點|优点|好處|好处)"
)


@dataclass(frozen=True)
class ScreenshotLanguage:
    code: str
    instruction: str


def detect_screenshot_language(text: str) -> ScreenshotLanguage:
    """Choose a stable output-language contract from OCR character classes."""

    normalized = unicodedata.normalize("NFKC", text)
    cjk_count = len(_CJK_PATTERN.findall(normalized))
    kana_count = sum(
        1
        for character in normalized
        if "HIRAGANA" in unicodedata.name(character, "")
        or "KATAKANA" in unicodedata.name(character, "")
    )
    hangul_count = sum(
        1 for character in normalized if "HANGUL" in unicodedata.name(character, "")
    )
    cyrillic_count = sum(
        1
        for character in normalized
        if "CYRILLIC" in unicodedata.name(character, "")
    )
    arabic_count = sum(
        1 for character in normalized if "ARABIC" in unicodedata.name(character, "")
    )
    latin_count = len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]", normalized))

    if cjk_count and kana_count > max(1, cjk_count // 5):
        return ScreenshotLanguage("ja", "Japanese")
    if hangul_count:
        return ScreenshotLanguage("ko", "Korean")
    if cjk_count:
        return ScreenshotLanguage(
            "zh-Hant",
            "Traditional Chinese (繁體中文)",
        )
    if cyrillic_count:
        return ScreenshotLanguage("ru", "Russian")
    if arabic_count:
        return ScreenshotLanguage("ar", "Arabic")
    if latin_count:
        return ScreenshotLanguage("en", "English")
    return ScreenshotLanguage(
        "en",
        "English unless the source clearly indicates another language",
    )


def preprocess_screenshot_ocr_text(raw_text: str) -> str:
    """Remove high-confidence browser chrome while preserving source OCR order."""

    cleaned_lines: List[str] = []
    for raw_line in raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
        if _is_browser_chrome_line(line):
            continue
        cleaned_lines.append(line)

    while cleaned_lines and cleaned_lines[0] == "":
        cleaned_lines.pop(0)
    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()
    return "\n".join(cleaned_lines)


def validate_screenshot_proposal(
    *,
    proposal: "SupplementProposalSchema",
    source_text: str,
) -> "SupplementProposalSchema":
    """Apply deterministic screenshot quality and source-grounding checks."""

    # Imported lazily to keep the OCR tool path independent from the
    # orchestrators package import order.
    from src.orchestrators.supplement_proposal_schema import (
        SupplementProposalValidationError,
    )

    if not 3 <= len(proposal.concepts) <= 30:
        raise SupplementProposalValidationError(
            "screenshot proposal concepts must contain 3 to 30 items"
        )
    if not 3 <= len(proposal.notes) <= 6:
        raise SupplementProposalValidationError(
            "screenshot proposal notes must contain 3 to 6 items"
        )
    if _normalize_for_grounding(proposal.title) in _GENERIC_SCREENSHOT_TITLES:
        raise SupplementProposalValidationError(
            "screenshot proposal title must be concrete and specific"
        )
    sentence_count = len(_SENTENCE_PATTERN.findall(proposal.summary))
    if sentence_count == 0:
        sentence_count = 1
    if sentence_count > 2:
        raise SupplementProposalValidationError(
            "screenshot proposal summary must contain 1 to 2 sentences"
        )

    language = detect_screenshot_language(source_text)
    _validate_output_language(proposal, language)

    # Re-apply the high-confidence OCR cleanup at the contract boundary. This
    # keeps callers from accidentally grounding a proposal in browser chrome.
    source_normalized = _normalize_for_grounding(
        preprocess_screenshot_ocr_text(source_text)
    )
    for label, value in _proposal_text_items(proposal):
        has_source_evidence = _has_source_evidence(
            value=value,
            source_normalized=source_normalized,
        )
        if not has_source_evidence:
            # Keep unsupported-advice diagnostics useful even when the advice
            # also contains a new, ungrounded content word.
            if _introduces_new_advice(
                value=value,
                source_normalized=source_normalized,
            ):
                raise SupplementProposalValidationError(
                    f"screenshot proposal {label} introduces unsupported advice"
                )
            raise SupplementProposalValidationError(
                f"screenshot proposal {label} is not supported by OCR source"
            )
        if _introduces_new_advice(
            value=value,
            source_normalized=source_normalized,
        ):
            raise SupplementProposalValidationError(
                f"screenshot proposal {label} introduces unsupported advice"
            )
        if _introduces_new_conclusion(
            value=value,
            source_normalized=source_normalized,
        ):
            raise SupplementProposalValidationError(
                f"screenshot proposal {label} introduces unsupported conclusion"
            )
    return proposal


def _proposal_text_items(proposal: SupplementProposalSchema) -> Iterable[tuple[str, str]]:
    yield "title", proposal.title
    yield "summary", proposal.summary
    for index, concept in enumerate(proposal.concepts):
        yield f"concepts[{index}]", concept
    for index, note in enumerate(proposal.notes):
        yield f"notes[{index}]", note


def _is_browser_chrome_line(line: str) -> bool:
    normalized = line.casefold().strip("|·•-—_ ")
    if normalized in _BROWSER_CHROME_LINES:
        return True
    if _URL_LINE_PATTERN.match(normalized) or _DOMAIN_LINE_PATTERN.match(normalized):
        return True
    if re.search(r"\b(?:https?|ftp|file|chrome|edge)://", normalized):
        return True
    if re.search(r"(?:地址列|網址列|網址|address bar|tab bar|navigation bar)", normalized):
        return True
    return False


def _normalize_for_grounding(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value).casefold()).strip()


def _meaningful_tokens(value: str) -> List[str]:
    tokens = [
        token.casefold().strip(".,!?;:()[]{}\"'")
        for token in _ASCII_TOKEN_PATTERN.findall(value)
    ]
    return [
        token
        for token in tokens
        if len(re.sub(r"\W", "", token)) >= 2
        or any(symbol in token for symbol in ("+", "#"))
    ]


def _has_source_evidence(*, value: str, source_normalized: str) -> bool:
    """Return whether a proposal item is source-grounded.

    This is deliberately a conservative lexical contract rather than an
    LLM judge. It permits common reporting words and a small synonym lexicon,
    while requiring an anchor from the OCR and exact preservation of numbers,
    commands, URLs, and technical atoms. That combination catches invented
    details without requiring every summary sentence to copy OCR wording.
    """

    normalized_value = _normalize_for_grounding(value)
    normalized_source = _normalize_for_grounding(source_normalized)

    source_numbers = set(_NUMBER_PATTERN.findall(normalized_source))
    value_numbers = set(_NUMBER_PATTERN.findall(normalized_value))
    if not value_numbers.issubset(source_numbers):
        return False

    source_atoms = _technical_atoms(normalized_source)
    value_atoms = _technical_atoms(normalized_value)
    if not value_atoms.issubset(source_atoms):
        return False

    source_tokens = _canonical_token_set(normalized_source)
    value_tokens = _canonical_tokens(normalized_value)
    frame_tokens = {
        _canonical_token(token) for token in _PROPOSAL_FRAME_TOKENS
    }
    content_tokens = [
        token
        for token in value_tokens
        if token not in frame_tokens
    ]
    safe_paraphrase_tokens = {
        _canonical_token(token) for token in _SAFE_PARAPHRASE_TOKENS
    }
    unknown_tokens = [
        token
        for token in content_tokens
        if token not in source_tokens and token not in safe_paraphrase_tokens
    ]
    if unknown_tokens:
        # New product names, commands, or domain nouns are not treated as
        # paraphrases merely because another source token is present.
        return False

    ascii_anchor = bool(set(content_tokens) & source_tokens)
    cjk_anchor = _has_cjk_anchor(
        value=normalized_value,
        source=normalized_source,
    )
    return ascii_anchor or cjk_anchor


def _canonical_token(token: str) -> str:
    normalized = token.casefold().strip(".,!?;:()[]{}\"'")
    if not normalized:
        return normalized
    if normalized in _SYNONYM_TO_CANONICAL:
        return _SYNONYM_TO_CANONICAL[normalized]
    if len(normalized) > 5 and normalized.endswith("ies"):
        return normalized[:-3] + "y"
    if len(normalized) > 5 and normalized.endswith("ing"):
        return normalized[:-3].rstrip("e")
    if len(normalized) > 4 and normalized.endswith("ed"):
        return normalized[:-2].rstrip("e")
    if len(normalized) > 4 and normalized.endswith("s"):
        return normalized[:-1]
    return normalized


def _canonical_tokens(value: str) -> List[str]:
    return [_canonical_token(token) for token in _meaningful_tokens(value)]


def _canonical_token_set(value: str) -> set[str]:
    return set(_canonical_tokens(value))


def _technical_atoms(value: str) -> set[str]:
    return {
        atom.casefold().strip(".,!?;:()[]{}\"'")
        for atom in _TECHNICAL_ATOM_PATTERN.findall(value)
        if atom.strip(".,!?;:()[]{}\"'")
    }


def _has_cjk_anchor(*, value: str, source: str) -> bool:
    value_runs = _CJK_RUN_PATTERN.findall(value)
    source_runs = _CJK_RUN_PATTERN.findall(source)
    if not value_runs or not source_runs:
        return False

    value_bigrams = {
        run[index : index + 2]
        for run in value_runs
        for index in range(len(run) - 1)
    }
    source_bigrams = {
        run[index : index + 2]
        for run in source_runs
        for index in range(len(run) - 1)
    }
    if value_bigrams & source_bigrams:
        return True

    # A two-character overlap still supports a short Traditional Chinese
    # concept when OCR punctuation or word segmentation differs.
    value_characters = set(_CJK_PATTERN.findall(value))
    source_characters = set(_CJK_PATTERN.findall(source))
    return len(value_characters & source_characters) >= 2


def _introduces_new_advice(*, value: str, source_normalized: str) -> bool:
    normalized_value = _normalize_for_grounding(value)
    normalized_source = _normalize_for_grounding(source_normalized)
    if not _ADVICE_PATTERN.search(normalized_value):
        return False
    return not _ADVICE_PATTERN.search(normalized_source)


def _introduces_new_conclusion(*, value: str, source_normalized: str) -> bool:
    normalized_value = _normalize_for_grounding(value)
    normalized_source = _normalize_for_grounding(source_normalized)
    if not _CONCLUSION_PATTERN.search(normalized_value):
        return False
    return not _CONCLUSION_PATTERN.search(normalized_source)


def _validate_output_language(
    proposal: SupplementProposalSchema,
    language: ScreenshotLanguage,
) -> None:
    from src.orchestrators.supplement_proposal_schema import (
        SupplementProposalValidationError,
    )

    natural_text = " ".join(
        [proposal.title, proposal.summary, *proposal.concepts, *proposal.notes]
    )
    if language.code != "zh-Hant":
        return
    if len(_CJK_PATTERN.findall(natural_text)) < 4:
        raise SupplementProposalValidationError(
            "Chinese screenshot proposal must use Traditional Chinese"
        )
    if not _CJK_PATTERN.search(proposal.title) or not _CJK_PATTERN.search(
        proposal.summary
    ):
        raise SupplementProposalValidationError(
            "Chinese screenshot proposal must use Traditional Chinese"
        )
    if any(not _CJK_PATTERN.search(note) for note in proposal.notes):
        raise SupplementProposalValidationError(
            "Chinese screenshot proposal must use Traditional Chinese"
        )
    for simplified, traditional in _TRADITIONAL_OUTPUT_REQUIRED:
        if simplified in natural_text:
            raise SupplementProposalValidationError(
                "Chinese screenshot proposal must use Traditional Chinese"
            )
