from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional

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
_CLAIM_SEPARATOR_PATTERN = re.compile(
    r"\n+|(?<=[.!?。！？；;])(?:\s+|$)"
)

SCREENSHOT_VALIDATOR_VERSION = "screenshot_grounding_v2"

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

_SIMPLIFIED_TO_TRADITIONAL = str.maketrans(
    {
        "后": "後",
        "简": "簡",
        "体": "體",
        "与": "與",
        "查": "查",
        "询": "詢",
        "优": "優",
        "化": "化",
        "数": "數",
        "据": "據",
        "处": "處",
        "迟": "遲",
        "启": "啟",
        "动": "動",
        "执": "執",
        "务": "務",
        "统": "統",
        "会": "會",
        "页": "頁",
        "浏": "瀏",
        "览": "覽",
        "器": "器",
        "学": "學",
        "习": "習",
        "总": "總",
        "结": "結",
        "实": "實",
        "践": "踐",
        "议": "議",
        "资": "資",
        "库": "庫",
        "检": "檢",
        "索": "索",
        "编": "編",
        "辑": "輯",
        "调": "調",
        "务": "務",
        "导": "導",
        "致": "致",
        "这": "這",
        "种": "種",
        "开": "開",
        "发": "發",
        "现": "現",
        "线": "線",
        "别": "別",
    }
)
_TITLE_CJK_ALIAS_GROUPS = {
    "index": ("索引",),
    "query": ("查詢",),
    "optimization": ("優化", "調校"),
    "tuning": ("調校", "優化"),
    "performance": ("效能", "性能"),
    "database": ("資料庫", "數據庫"),
    "recruitment": ("招募", "招聘"),
}
_TITLE_SAFE_TOKENS = frozenset(
    {
        "a",
        "an",
        "and",
        "for",
        "from",
        "in",
        "of",
        "on",
        "the",
        "to",
        "with",
        "via",
        "about",
        "guide",
        "notes",
        "overview",
        "summary",
        "topic",
        "key",
        "main",
        "based",
        "startup",
    }
)
_TITLE_CONNECTIVE_CJK = frozenset("與的和及之、")

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
        "explains",
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
    # Do not treat the ordinary verb "use" as advice by itself.  A
    # descriptive sentence such as "the section shows how to use SQL" is
    # still subject to source-evidence checks, but is not an instruction.
    # Imperative "use" remains advice when it starts a sentence.
    r"\b(?:should|recommend(?:ed|ation)?|consider|try|must|need(?:s)? to|"
    r"avoid|you can)\b|"
    r"(?:^|[.!?。！？]\s*)(?:use|try|avoid|consider)\b|"
    r"(?:建議|建议|應該|应该|請|请|必須|必须|務必|务必|需要|避免|推薦|推荐|"
    r"你可以|您可以)"
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


@dataclass(frozen=True)
class ScreenshotSourceSnapshot:
    """The exact cleaned OCR snapshot shared by prompt and validator."""

    text: str
    normalized_text: str
    source_normalized_char_count: int
    digest: str


@dataclass(frozen=True)
class ScreenshotGroundingDiagnostics:
    source_normalized_char_count: int
    candidate_field_char_count: int
    evidence_claim_count: int
    unsupported_claim_count: int
    validator_version: str
    source_snapshot_digest: str
    prompt_source_digest: str
    validation_source_digest: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "source_normalized_char_count": self.source_normalized_char_count,
            "candidate_field_char_count": self.candidate_field_char_count,
            "evidence_claim_count": self.evidence_claim_count,
            "unsupported_claim_count": self.unsupported_claim_count,
            "validator_version": self.validator_version,
            "source_snapshot_digest": self.source_snapshot_digest,
            "prompt_source_digest": self.prompt_source_digest,
            "validation_source_digest": self.validation_source_digest,
        }


@dataclass(frozen=True)
class ScreenshotProposalValidationResult:
    proposal: "SupplementProposalSchema"
    title_fallback_used: bool = False
    diagnostics: Optional[ScreenshotGroundingDiagnostics] = None


def build_screenshot_source_snapshot(raw_text: str) -> ScreenshotSourceSnapshot:
    """Build one bounded, deterministic OCR view for prompt and validation."""

    cleaned_text = preprocess_screenshot_ocr_text(raw_text).strip()
    normalized_text = _normalize_for_grounding(cleaned_text)
    digest = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
    return ScreenshotSourceSnapshot(
        text=cleaned_text,
        normalized_text=normalized_text,
        source_normalized_char_count=len(normalized_text),
        digest=digest,
    )


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
    cleaned_text = "\n".join(cleaned_lines)
    # Keep source ordering and line boundaries, but repair OCR spaces inside
    # CJK words before the generic grounding validator sees the source.
    return re.sub(
        r"(?<=[\u3400-\u4dbf\u4e00-\u9fff])\s+(?=[\u3400-\u4dbf\u4e00-\u9fff])",
        "",
        cleaned_text,
    )


def validate_screenshot_proposal(
    *,
    proposal: "SupplementProposalSchema",
    source_text: str,
) -> "SupplementProposalSchema":
    """Apply deterministic screenshot quality and source-grounding checks."""

    return _validate_screenshot_proposal(
        proposal=proposal,
        source_snapshot=build_screenshot_source_snapshot(source_text),
    )[0]


def _validate_screenshot_proposal(
    *,
    proposal: "SupplementProposalSchema",
    source_snapshot: ScreenshotSourceSnapshot,
) -> tuple["SupplementProposalSchema", ScreenshotGroundingDiagnostics]:
    """Validate claims against one exact OCR snapshot and return diagnostics."""

    # Imported lazily to keep the OCR tool path independent from the
    # orchestrators package import order.
    from src.orchestrators.supplement_proposal_schema import (
        SupplementProposalValidationError,
    )

    evidence_claim_count = 0
    unsupported_claim_count = 0

    def diagnostics(*, value: str, evidence: int, unsupported: int) -> Dict[str, object]:
        result = ScreenshotGroundingDiagnostics(
            source_normalized_char_count=source_snapshot.source_normalized_char_count,
            candidate_field_char_count=len(value),
            evidence_claim_count=evidence,
            unsupported_claim_count=unsupported,
            validator_version=SCREENSHOT_VALIDATOR_VERSION,
            source_snapshot_digest=source_snapshot.digest,
            prompt_source_digest=source_snapshot.digest,
            validation_source_digest=source_snapshot.digest,
        )
        return result.as_dict()

    def fail(
        message: str,
        *,
        field: Optional[str] = None,
        value: str = "",
        evidence: Optional[int] = None,
        unsupported: Optional[int] = None,
    ) -> None:
        raise SupplementProposalValidationError(
            message,
            field=field,
            diagnostics=diagnostics(
                value=value,
                evidence=evidence if evidence is not None else evidence_claim_count,
                unsupported=(
                    unsupported
                    if unsupported is not None
                    else unsupported_claim_count
                ),
            ),
        )

    if not 3 <= len(proposal.concepts) <= 30:
        fail(
            "screenshot proposal concepts must contain 3 to 30 items",
            field="concepts",
            value="\n".join(proposal.concepts),
        )
    if not 3 <= len(proposal.notes) <= 6:
        fail(
            "screenshot proposal notes must contain 3 to 6 items",
            field="notes",
            value="\n".join(proposal.notes),
        )
    if _normalize_title_text(proposal.title) in _GENERIC_SCREENSHOT_TITLES:
        fail(
            "screenshot proposal title must be concrete and specific",
            field="title",
            value=proposal.title,
            unsupported=1,
        )
    sentence_count = len(_SENTENCE_PATTERN.findall(proposal.summary))
    if sentence_count == 0:
        sentence_count = 1
    if sentence_count > 2:
        fail(
            "screenshot proposal summary must contain 1 to 2 sentences",
            field="summary",
            value=proposal.summary,
        )

    language = detect_screenshot_language(source_snapshot.text)
    try:
        _validate_output_language(proposal, language)
    except SupplementProposalValidationError as exc:
        raise SupplementProposalValidationError(
            exc.message,
            field=exc.field,
            diagnostics=diagnostics(
                value=" ".join(
                    [proposal.title, proposal.summary, *proposal.concepts, *proposal.notes]
                ),
                evidence=0,
                unsupported=0,
            ),
        ) from exc

    source_normalized = source_snapshot.normalized_text
    for label, value in _proposal_text_items(proposal):
        claims = [value] if label == "title" else _split_claims(value)
        for claim in claims:
            if label == "title":
                has_source_evidence = _has_title_source_anchor(
                    value=claim,
                    source_text=source_snapshot.text,
                )
            else:
                has_source_evidence = _has_source_evidence(
                    value=claim,
                    source_normalized=source_normalized,
                )

            if has_source_evidence:
                evidence_claim_count += 1
            else:
                unsupported_claim_count += 1

            if not label.startswith("concepts[") and _introduces_new_advice(
                value=claim,
                source_normalized=source_normalized,
            ):
                if has_source_evidence:
                    unsupported_claim_count += 1
                fail(
                    f"screenshot proposal {label} introduces unsupported advice",
                    field=label,
                    value=value,
                    evidence=evidence_claim_count,
                    unsupported=unsupported_claim_count,
                )
            if _introduces_new_conclusion(
                value=claim,
                source_normalized=source_normalized,
            ):
                if has_source_evidence:
                    unsupported_claim_count += 1
                fail(
                    f"screenshot proposal {label} introduces unsupported conclusion",
                    field=label,
                    value=value,
                    evidence=evidence_claim_count,
                    unsupported=unsupported_claim_count,
                )
            if not has_source_evidence:
                fail(
                    f"screenshot proposal {label} is not supported by OCR source",
                    field=label,
                    value=value,
                    evidence=evidence_claim_count,
                    unsupported=unsupported_claim_count,
                )

    return proposal, ScreenshotGroundingDiagnostics(
        source_normalized_char_count=source_snapshot.source_normalized_char_count,
        candidate_field_char_count=sum(
            len(value) for _, value in _proposal_text_items(proposal)
        ),
        evidence_claim_count=evidence_claim_count,
        unsupported_claim_count=unsupported_claim_count,
        validator_version=SCREENSHOT_VALIDATOR_VERSION,
        source_snapshot_digest=source_snapshot.digest,
        prompt_source_digest=source_snapshot.digest,
        validation_source_digest=source_snapshot.digest,
    )


def _split_claims(value: str) -> List[str]:
    return [claim.strip() for claim in _CLAIM_SEPARATOR_PATTERN.split(value) if claim.strip()]


def validate_screenshot_proposal_with_title_fallback(
    *,
    proposal: "SupplementProposalSchema",
    source_text: str,
    source_snapshot: Optional[ScreenshotSourceSnapshot] = None,
) -> ScreenshotProposalValidationResult:
    """Validate a screenshot proposal and repair only a grounded title failure.

    The fallback is intentionally after LLM parsing and before persistence. It
    never calls OCR or a provider. An unrelated title has no source anchor and
    still fails closed; only a title with enough source evidence to identify
    the topic may be replaced by the deterministic source-keyword title.
    """

    from src.orchestrators.supplement_proposal_schema import (
        SupplementProposalValidationError,
    )

    source_snapshot = source_snapshot or build_screenshot_source_snapshot(source_text)
    try:
        validated, diagnostics = _validate_screenshot_proposal(
            proposal=proposal,
            source_snapshot=source_snapshot,
        )
        return ScreenshotProposalValidationResult(
            proposal=validated,
            diagnostics=diagnostics,
        )
    except SupplementProposalValidationError as exc:
        if exc.field != "title" or not _has_partial_title_anchor(
            value=proposal.title,
            source_text=source_snapshot.text,
        ):
            raise

        fallback_title = build_screenshot_fallback_title(source_snapshot.text)
        fallback_proposal = proposal.model_copy(
            update={"title": fallback_title}
        )
        validated, diagnostics = _validate_screenshot_proposal(
            proposal=fallback_proposal,
            source_snapshot=source_snapshot,
        )
        return ScreenshotProposalValidationResult(
            proposal=validated,
            title_fallback_used=True,
            diagnostics=diagnostics,
        )


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


def _normalize_title_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).translate(
        _SIMPLIFIED_TO_TRADITIONAL
    ).casefold()
    normalized = normalized.translate(
        str.maketrans(
            {
                "（": "(",
                "）": ")",
                "【": "[",
                "】": "]",
                "「": "\"",
                "」": "\"",
                "『": "\"",
                "』": "\"",
            }
        )
    )
    normalized = re.sub(
        r"[^a-z0-9_+#./:\-\u3400-\u4dbf\u4e00-\u9fff]+",
        " ",
        normalized,
    )
    # OCR frequently inserts spaces inside a CJK word (for example
    # ``索 引`` or ``查 詢``). Keep Latin token boundaries intact while
    # joining only whitespace surrounded by CJK characters.
    normalized = re.sub(
        r"(?<=[\u3400-\u4dbf\u4e00-\u9fff])\s+(?=[\u3400-\u4dbf\u4e00-\u9fff])",
        "",
        normalized,
    )
    return re.sub(r"\s+", " ", normalized).strip()


def _title_cjk_ngrams(value: str) -> set[str]:
    normalized = _normalize_title_text(value)
    return {
        run[index : index + 2]
        for run in _CJK_RUN_PATTERN.findall(normalized)
        for index in range(len(run) - 1)
    }


def _title_aliases_present(value: str) -> set[str]:
    normalized = _normalize_title_text(value)
    return {
        canonical
        for canonical, aliases in _TITLE_CJK_ALIAS_GROUPS.items()
        if any(_normalize_title_text(alias) in normalized for alias in aliases)
    }


def _title_anchor_details(
    *,
    value: str,
    source_text: str,
) -> tuple[set[str], set[str], set[str], set[str]]:
    normalized_value = _normalize_title_text(value)
    normalized_source = _normalize_title_text(
        preprocess_screenshot_ocr_text(source_text)
    )
    source_tokens = _canonical_token_set(normalized_source)
    value_tokens = _canonical_tokens(normalized_value)
    value_aliases = _title_aliases_present(normalized_value)
    source_aliases = _title_aliases_present(normalized_source)
    for canonical, aliases in _TITLE_CJK_ALIAS_GROUPS.items():
        if canonical in source_tokens:
            source_aliases.add(canonical)
        if any(_normalize_title_text(alias) in normalized_source for alias in aliases):
            source_aliases.add(canonical)

    source_anchor_tokens = source_tokens | source_aliases
    allowed_tokens = {
        _canonical_token(token) for token in _TITLE_SAFE_TOKENS
    }
    allowed_tokens.update(source_aliases)
    unknown_tokens = {
        token
        for token in value_tokens
        if token not in source_anchor_tokens and token not in allowed_tokens
    }
    exact_or_alias = {
        token
        for token in value_tokens
        if token in source_anchor_tokens and token not in allowed_tokens
    }
    alias_overlap = value_aliases & source_aliases
    cjk_overlap = _title_cjk_ngrams(normalized_value) & _title_cjk_ngrams(
        normalized_source
    )
    return unknown_tokens, exact_or_alias, alias_overlap, cjk_overlap


def _has_title_source_anchor(*, value: str, source_text: str) -> bool:
    normalized_value = _normalize_title_text(value)
    normalized_source = _normalize_title_text(
        preprocess_screenshot_ocr_text(source_text)
    )
    if not normalized_value:
        return False
    if not set(_NUMBER_PATTERN.findall(normalized_value)).issubset(
        set(_NUMBER_PATTERN.findall(normalized_source))
    ):
        return False
    if not _technical_atoms(normalized_value).issubset(
        _technical_atoms(normalized_source)
    ):
        return False

    unknown_tokens, exact_or_alias, alias_overlap, cjk_overlap = _title_anchor_details(
        value=normalized_value,
        source_text=normalized_source,
    )
    if unknown_tokens:
        return False

    has_cjk = any(
        character not in _TITLE_CONNECTIVE_CJK
        for character in _CJK_PATTERN.findall(normalized_value)
    )
    if has_cjk and not cjk_overlap and not alias_overlap:
        return False
    anchor_count = len(exact_or_alias) + len(alias_overlap) + len(cjk_overlap)
    if anchor_count < 2:
        return False
    return bool(exact_or_alias or alias_overlap or cjk_overlap)


def _has_partial_title_anchor(*, value: str, source_text: str) -> bool:
    """Allow fallback only when the failed title is still on the source topic."""

    normalized_value = _normalize_title_text(value)
    normalized_source = _normalize_title_text(
        preprocess_screenshot_ocr_text(source_text)
    )
    unknown_tokens, exact_or_alias, alias_overlap, cjk_overlap = _title_anchor_details(
        value=normalized_value,
        source_text=normalized_source,
    )
    if unknown_tokens:
        return False
    if not set(_NUMBER_PATTERN.findall(normalized_value)).issubset(
        set(_NUMBER_PATTERN.findall(normalized_source))
    ):
        return False
    if not _technical_atoms(normalized_value).issubset(
        _technical_atoms(normalized_source)
    ):
        return False
    return bool(exact_or_alias or alias_overlap or cjk_overlap)


def build_screenshot_fallback_title(source_text: str) -> str:
    """Build a grounded title from OCR headings/keywords without an LLM."""

    cleaned_source = preprocess_screenshot_ocr_text(source_text)
    for raw_line in cleaned_source.splitlines():
        candidate = re.sub(r"\s+", " ", raw_line).strip(" -–—:;|")
        if not candidate or re.match(r"^\[image\s+\d+\]$", candidate, re.I):
            continue
        if len(candidate) > 100 or re.search(r"[.!?。！？]$", candidate):
            continue
        if _has_title_source_anchor(value=candidate, source_text=cleaned_source):
            return candidate

    source_lines = [line for line in cleaned_source.splitlines() if line.strip()]
    technical_terms: list[str] = []
    content_terms: list[str] = []
    cjk_terms: list[str] = []
    frame_tokens = {
        _canonical_token(token) for token in _PROPOSAL_FRAME_TOKENS
    }
    safe_tokens = {
        _canonical_token(token) for token in _SAFE_PARAPHRASE_TOKENS
    }
    for line in source_lines:
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_+#./:-]*", line):
            display_token = token.strip(".,!?;:")
            canonical = _canonical_token(token)
            if canonical in {
                _canonical_token(item) for item in technical_terms + content_terms
            }:
                continue
            if canonical not in frame_tokens and canonical not in safe_tokens:
                content_terms.append(display_token)
            if (
                any(character.isupper() for character in token[1:])
                or token.isupper()
                or any(symbol in token for symbol in ("#", "+", ".", "/", "-"))
            ):
                technical_terms.append(display_token)
        for run in _CJK_RUN_PATTERN.findall(line):
            if len(run) >= 2 and run not in cjk_terms:
                cjk_terms.append(run[:24])

    candidates: list[str] = []
    seen_candidates: set[str] = set()
    for candidate in technical_terms[:4] + content_terms[:4] + cjk_terms[:4]:
        candidate_key = _normalize_title_text(candidate)
        if candidate_key and candidate_key not in seen_candidates:
            seen_candidates.add(candidate_key)
            candidates.append(candidate)
    fallback = "、".join(candidates)
    if fallback:
        return fallback
    return "Screenshot source proposal"


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

    exact_ascii_anchors = set(content_tokens) & source_tokens
    ascii_anchor = bool(exact_ascii_anchors)
    cjk_anchor = _has_cjk_anchor(
        value=normalized_value,
        source=normalized_source,
    )
    # Mixed Traditional Chinese/English claims often add neutral reporting
    # words around two or more preserved technical/source terms. Requiring two
    # exact anchors for that shape allows faithful paraphrase without accepting
    # a new domain noun that merely sits beside one familiar term.
    if _CJK_PATTERN.search(normalized_value) and _CJK_PATTERN.search(normalized_source):
        return cjk_anchor or (
            bool(exact_ascii_anchors) and len(exact_ascii_anchors) >= 2
        )
    if ascii_anchor and len(exact_ascii_anchors) >= 2:
        return True
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
