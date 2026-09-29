"""Small Stage 2 proof of concept built with Pyformlang's finite-state transducer."""

from __future__ import annotations

from functools import lru_cache

from .extraction import extract_resume


_JAVASCRIPT_ALIASES = ("JS", "Javascript", "JavaScript")
_JAVASCRIPT_CANONICAL = "JAVASCRIPT"


@lru_cache(maxsize=1)
def build_javascript_transducer():
    """Build an FST for a small, explicit subset of Stage 2 aliases.

    Pyformlang remains an optional dependency so the Stage 1 extractor stays
    dependency-free. The import is intentionally delayed until this demo runs.
    """
    from pyformlang.fst import FST

    transducer = FST()
    transducer.add_start_state("q0")
    transducer.add_final_state("qf")
    for alias in _JAVASCRIPT_ALIASES:
        transducer.add_transition(
            "q0", alias, "qf", [_JAVASCRIPT_CANONICAL]
        )
    return transducer


def normalize_qualification(value: str) -> str:
    """Normalize a supported alias; preserve unmodeled text unchanged."""
    translations = list(build_javascript_transducer().translate([value]))
    if not translations:
        return value
    return "".join(translations[0])


def normalize_resume_skills(text: str) -> dict[str, list[str]]:
    """Run Stage 1 extraction, then the demonstration FST over extracted skills."""
    extracted = extract_resume(text)
    return {
        category: [normalize_qualification(match.value) for match in matches]
        for category, matches in extracted.skills.items()
    }
