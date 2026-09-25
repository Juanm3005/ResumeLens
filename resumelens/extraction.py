"""Regex-based extraction for ResumeLens project stage 1."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse

from .patterns import (
    ACADEMIC_DEGREE_PATTERN,
    EMAIL_PATTERN,
    EXPERIENCE_PATTERNS,
    PHONE_PATTERN,
    SKILL_PATTERNS,
    URL_PATTERN,
)


@dataclass(frozen=True)
class ExtractionMatch:
    """One literal match in the original résumé text, with a half-open span."""

    value: str
    start: int
    end: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExtractionResult:
    """Extracted fields grouped by type, without canonicalization."""

    contacts: dict[str, list[ExtractionMatch]]
    skills: dict[str, list[ExtractionMatch]]
    academic_degrees: list[ExtractionMatch]
    experience: list[ExtractionMatch]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of all matches."""
        return {
            "contacts": {
                category: [match.to_dict() for match in matches]
                for category, matches in self.contacts.items()
            },
            "skills": {
                category: [match.to_dict() for match in matches]
                for category, matches in self.skills.items()
            },
            "academic_degrees": [match.to_dict() for match in self.academic_degrees],
            "experience": [match.to_dict() for match in self.experience],
        }

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the result as UTF-8-friendly JSON text."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


def _matches(pattern: str, text: str, *, flags: int = re.IGNORECASE) -> list[ExtractionMatch]:
    """Return all literal matches in source order."""
    return [
        ExtractionMatch(value=match.group(0), start=match.start(), end=match.end())
        for match in re.finditer(pattern, text, flags)
    ]


def _is_date(value: str) -> bool:
    """Avoid reporting common numeric dates as phone numbers."""
    return bool(re.fullmatch(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}", value.strip()))


def _extract_urls(text: str) -> dict[str, list[ExtractionMatch]]:
    categories = {"linkedin": [], "github": [], "websites": []}
    for match in re.finditer(URL_PATTERN, text):
        # Punctuation is usually part of the résumé sentence, not the URL.
        end = match.end()
        value = match.group(0).rstrip(".,;:!?")
        end -= len(match.group(0)) - len(value)
        if not value:
            continue

        host = urlparse(value if "://" in value else f"https://{value}").netloc.lower()
        item = ExtractionMatch(value=value, start=match.start(), end=end)
        if "linkedin.com" in host:
            categories["linkedin"].append(item)
        elif "github.com" in host:
            categories["github"].append(item)
        else:
            categories["websites"].append(item)
    return categories


def extract_resume(text: str) -> ExtractionResult:
    """Extract contacts, qualifications, education, and experience from text.

    Every ``value`` is copied from the source résumé. The function neither
    normalizes aliases (``JS`` stays ``JS``) nor makes profile decisions.
    ``start`` and ``end`` are Python string offsets with ``end`` excluded.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    contacts = {
        "emails": _matches(EMAIL_PATTERN, text),
        "phones": [
            match
            for match in _matches(PHONE_PATTERN, text)
            if not _is_date(match.value)
        ],
        **_extract_urls(text),
    }
    skills = {
        definition.category: _matches(definition.pattern, text)
        for definition in SKILL_PATTERNS
    }

    degree_matches = _matches(ACADEMIC_DEGREE_PATTERN, text)
    experience_matches = [
        match
        for pattern in EXPERIENCE_PATTERNS
        for match in _matches(pattern, text)
    ]
    experience_matches.sort(key=lambda match: (match.start, match.end))

    return ExtractionResult(
        contacts=contacts,
        skills=skills,
        academic_degrees=degree_matches,
        experience=experience_matches,
    )
