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
    EXPERIENCE_SECTION_HEADER_PATTERN,
    OTHER_SECTION_HEADER_PATTERN,
    OTHER_QUALIFICATION_PATTERNS,
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
    other_qualifications: dict[str, list[ExtractionMatch]]
    academic_degrees: list[ExtractionMatch]
    experience: list[ExtractionMatch]
    experience_sections: list[ExtractionMatch]

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
            "other_qualifications": {
                category: [match.to_dict() for match in matches]
                for category, matches in self.other_qualifications.items()
            },
            "academic_degrees": [match.to_dict() for match in self.academic_degrees],
            "experience": [match.to_dict() for match in self.experience],
            "experience_sections": [
                match.to_dict() for match in self.experience_sections
            ],
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

        host = urlparse(value if "://" in value else f"https://{value}").hostname or ""
        host = host.lower()
        item = ExtractionMatch(value=value, start=match.start(), end=end)
        if host == "linkedin.com" or host.endswith(".linkedin.com"):
            categories["linkedin"].append(item)
        elif host == "github.com" or host.endswith(".github.com"):
            categories["github"].append(item)
        else:
            categories["websites"].append(item)
    return categories


def _extract_experience_sections(text: str) -> list[ExtractionMatch]:
    """Capture literal content under common experience headings."""
    sections = []
    for header in re.finditer(EXPERIENCE_SECTION_HEADER_PATTERN, text):
        body_start = header.end()
        next_heading = re.search(OTHER_SECTION_HEADER_PATTERN, text[body_start:])
        body_end = (
            body_start + next_heading.start() if next_heading else len(text)
        )
        raw_body = text[body_start:body_end]
        value = raw_body.strip()
        if not value:
            continue

        leading_whitespace = len(raw_body) - len(raw_body.lstrip())
        start = body_start + leading_whitespace
        sections.append(ExtractionMatch(value=value, start=start, end=start + len(value)))
    return sections


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
    other_qualifications = {
        definition.category: _matches(definition.pattern, text)
        for definition in OTHER_QUALIFICATION_PATTERNS
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
        other_qualifications=other_qualifications,
        academic_degrees=degree_matches,
        experience=experience_matches,
        experience_sections=_extract_experience_sections(text),
    )
