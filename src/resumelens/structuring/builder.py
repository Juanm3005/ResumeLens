"""Stage 4 generator: Stage 1-3 results -> candidate-profile DSL text.

The generated document is always re-parsed with the textX metamodel, so a
profile that leaves this module has been validated by the grammar.
"""

from __future__ import annotations

import re

from ..extraction import ExtractionMatch, extract_resume
from ..normalization import normalize_extraction
from ..recognition import ACCEPTED, recognize_all
from .dsl import parse_candidate_profile

UNKNOWN_NAME = "Unknown candidate"

# The résumé's first line, when it is two to five capitalized words.
NAME_PATTERN = re.compile(
    r"[A-ZÁÉÍÓÚÑ][a-záéíóúñü'.-]+(?:[ \t]+[A-ZÁÉÍÓÚÑ][a-záéíóúñü'.-]+){1,4}"
)
DURATION_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(\+)?\s*(?:years?|yrs?)", re.IGNORECASE
)
BULLET_PREFIX = re.compile(r"^[\s\-*•·–]+")

# Stage 1 source category -> DSL skill category.
SKILL_CATEGORIES = {
    "skills.programming_languages": "languages",
    "skills.frameworks_libraries": "frameworks",
    "skills.databases": "databases",
    "skills.tools_and_technologies": "tools",
}
CATEGORY_ORDER = ("languages", "frameworks", "databases", "tools", "qualifications")
LINK_KINDS = (("linkedin", "linkedin"), ("github", "github"), ("websites", "website"))


def quote(value: str) -> str:
    """Render ``value`` as a DSL ``STRING`` on a single line."""
    value = " ".join(value.split())
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _unique(matches: list[ExtractionMatch]) -> list[str]:
    return list(dict.fromkeys(match.value for match in matches))


def _candidate_name(text: str) -> str:
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return first_line if NAME_PATTERN.fullmatch(first_line) else UNKNOWN_NAME


def _duration(value: str) -> str | None:
    match = DURATION_PATTERN.search(value)
    if not match:
        return None
    amount = float(match.group(1))
    unit = "year" if amount == 1 and not match.group(2) else "years"
    return f"{amount:g}{match.group(2) or ''} {unit}"


def _line_of(text: str, match: ExtractionMatch) -> str:
    start = text.rfind("\n", 0, match.start) + 1
    end = text.find("\n", match.end)
    return text[start:end if end != -1 else len(text)].strip()


def _experience(text: str, extraction):
    """Return (total duration, jobs); each job is (duration, activities).

    Each experience section becomes a job. Durations written outside the
    sections (e.g. in a summary line) give the total; without sections, each
    of those lines becomes a job of its own.
    """
    jobs, outside = [], list(extraction.experience)
    for section in extraction.experience_sections:
        inside = [m for m in outside if section.start <= m.start < section.end]
        outside = [m for m in outside if m not in inside]
        activities = [
            BULLET_PREFIX.sub("", line).strip()
            for line in section.value.splitlines()
        ]
        jobs.append((
            _duration(inside[0].value) if inside else None,
            [line for line in activities if line],
        ))
    if not jobs:
        jobs = [(None, [_line_of(text, m)]) for m in outside]
    total = _duration(outside[0].value) if outside else None
    return total, jobs


def _block(keyword: str, lines: list[str], indent: str = "    ") -> list[str]:
    return [f"{indent}{keyword} {{", *(f"{indent}    {line}" for line in lines),
            f"{indent}}}"]


def build_candidate_profile(text: str) -> str:
    """Run Stages 1-3 on résumé text and render the validated DSL document."""
    extraction = extract_resume(text)
    normalized = normalize_extraction(extraction)
    results = recognize_all(normalized.tokens)

    body = _block("personal", [f"name: {quote(_candidate_name(text))};"])

    contact = [f"email: {value};" for value in _unique(extraction.contacts["emails"])]
    contact += [
        f"phone: {' '.join(value.split())};"
        for value in _unique(extraction.contacts["phones"])
    ]
    for category, kind in LINK_KINDS:
        contact += [f"{kind}: {value};" for value in _unique(extraction.contacts[category])]
    if contact:
        body += _block("contact", contact)

    degrees = _unique(extraction.academic_degrees)
    if degrees:
        body += _block("education", [f"degree: {quote(d)};" for d in degrees])

    total, jobs = _experience(text, extraction)
    if jobs:
        lines = [f"total: {total};"] if total else []
        for duration, activities in jobs:
            fields = [f"duration: {duration};"] if duration else []
            fields += [f"activity: {quote(a)};" for a in activities]
            lines += _block("job", fields, indent="")
        body += _block("experience", lines)

    groups: dict[str, list[str]] = {category: [] for category in CATEGORY_ORDER}
    for mention in normalized.mentions:
        if mention.token is None:
            continue
        category = SKILL_CATEGORIES.get(mention.source, "qualifications")
        if not any(mention.token in tokens for tokens in groups.values()):
            groups[category].append(mention.token)
    body += _block("skills", [
        f"{category}: {', '.join(tokens)};"
        for category, tokens in groups.items() if tokens
    ])

    accepted = [r for r in results if r.verdict == ACCEPTED]
    classification = []
    for result in accepted:
        classification += _block(
            f"accepted {result.profile}",
            [f"sequence: {', '.join(result.sequence)};"],
            indent="",
        )
    body += _block("classification", classification or ["none;"])

    source = "\n".join(["candidate {", *body, "}"]) + "\n"
    parse_candidate_profile(source)  # generated profiles must be valid
    return source
