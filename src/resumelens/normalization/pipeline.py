"""Stage 2 pipeline: extracted values -> T1 -> T2 -> dedupe -> profile order."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..extraction import ExtractionResult, extract_resume
from ..profiles import PROFILES, sort_tokens
from .catalog import END
from .transducers import (
    build_alias_transducer,
    build_cleaning_transducer,
    run_transducer,
)


@dataclass(frozen=True)
class NormalizedMention:
    """One Stage 1 mention and the token it normalizes to (None if unknown)."""

    value: str
    start: int
    end: int
    source: str
    token: str | None


@dataclass
class NormalizationResult:
    mentions: list[NormalizedMention]
    tokens: list[str]  # unique canonical tokens, first-appearance order
    unrecognized: list[str]  # raw values the transducers rejected
    profile: str | None = None
    ordered_tokens: list[str] = field(default_factory=list)
    outside_profile: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_value(value: str) -> str | None:
    """Apply T1 then T2 to one literal value; ``None`` if not modeled."""
    cleaned = run_transducer(build_cleaning_transducer(), [*value, END])
    if cleaned is None:
        return None
    output = run_transducer(build_alias_transducer(), cleaned)
    return output[0] if output else None


def normalize_extraction(
    result: ExtractionResult, profile: str | None = None
) -> NormalizationResult:
    """Normalize skills and prose qualifications of a Stage 1 result."""
    if profile is not None and profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}; use {sorted(PROFILES)}")

    sources = [
        (f"skills.{category}", matches)
        for category, matches in result.skills.items()
    ] + [
        (f"other_qualifications.{category}", matches)
        for category, matches in result.other_qualifications.items()
    ]
    mentions = sorted(
        (
            NormalizedMention(
                m.value, m.start, m.end, source, normalize_value(m.value)
            )
            for source, matches in sources
            for m in matches
        ),
        key=lambda item: (item.start, item.end),
    )

    tokens = list(dict.fromkeys(m.token for m in mentions if m.token))
    unrecognized = list(dict.fromkeys(m.value for m in mentions if not m.token))
    normalized = NormalizationResult(mentions, tokens, unrecognized)
    if profile is not None:
        normalized.profile = profile
        normalized.ordered_tokens, normalized.outside_profile = sort_tokens(
            tokens, profile
        )
    return normalized


def normalize_text(text: str, profile: str | None = None) -> NormalizationResult:
    """Run Stage 1 extraction and Stage 2 normalization on résumé text."""
    return normalize_extraction(extract_resume(text), profile)