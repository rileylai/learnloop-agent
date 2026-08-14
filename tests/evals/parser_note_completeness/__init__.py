"""Parser and note completeness benchmark contracts."""

from .normalized_document import (
    CAPABILITY_NAMES,
    ELEMENT_KINDS,
    SCHEMA_VERSION,
    ArtifactRole,
    ElementKind,
    IdentityStatus,
    NormalizedDocument,
    SourceType,
    TypedIdentity,
    canonical_normalized_document_bytes,
    normalized_document_sha256,
    validate_normalized_document,
)

__all__ = [
    "CAPABILITY_NAMES",
    "ELEMENT_KINDS",
    "SCHEMA_VERSION",
    "ArtifactRole",
    "ElementKind",
    "IdentityStatus",
    "NormalizedDocument",
    "SourceType",
    "TypedIdentity",
    "canonical_normalized_document_bytes",
    "normalized_document_sha256",
    "validate_normalized_document",
]
