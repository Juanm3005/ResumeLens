"""Stage 4 metamodel: parse and validate candidate-profile DSL documents.

The grammar (``candidate_profile.tx``) enforces the lexical and syntactic
rules. The checks below enforce what a context-free grammar cannot express:
tokens must belong to the Stage 2 catalog, nothing may be repeated, and every
accepted profile must really be accepted by its Stage 3 automaton.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from textx import TextXSemanticError, get_location, metamodel_from_file

from ..normalization.catalog import CATALOG
from ..recognition import ACCEPTED, RECOGNIZERS

GRAMMAR = Path(__file__).with_name("candidate_profile.tx")


def _error(message: str, obj) -> TextXSemanticError:
    return TextXSemanticError(message, **get_location(obj))


def _check_skill_group(group) -> None:
    for token in group.tokens:
        if token not in CATALOG:
            raise _error(f"unknown qualification token {token!r}", group)


def _check_contact(contact) -> None:
    seen = set()
    for entry in contact.entries:
        key = (type(entry).__name__, getattr(entry, "kind", ""), entry.value)
        if key in seen:
            raise _error(f"duplicated contact entry {entry.value!r}", entry)
        seen.add(key)


def _check_duration(duration) -> None:
    if duration.value <= 0:
        raise _error("duration must be greater than zero", duration)


def _check_profile(model, _metamodel) -> None:
    skills: set[str] = set()
    categories: set[str] = set()
    for group in model.skills.groups:
        if group.category in categories:
            raise _error(f"skill category {group.category!r} declared twice", group)
        categories.add(group.category)
        for token in group.tokens:
            if token in skills:
                raise _error(f"skill {token!r} declared twice", group)
            skills.add(token)

    profiles: set[str] = set()
    for accepted in model.classification.accepted:
        if accepted.profile in profiles:
            raise _error(f"profile {accepted.profile} declared twice", accepted)
        profiles.add(accepted.profile)

        missing = [token for token in accepted.sequence if token not in skills]
        if missing:
            raise _error(
                f"{accepted.profile} sequence uses tokens not declared in skills: "
                + ", ".join(missing),
                accepted,
            )
        result = RECOGNIZERS[accepted.profile](accepted.sequence)
        if (
            result.verdict != ACCEPTED
            or result.outside_profile
            or result.sequence != list(accepted.sequence)
        ):
            raise _error(
                f"sequence is not accepted by the {accepted.profile} automaton "
                f"(expected canonical order: {', '.join(result.sequence) or '-'}; "
                f"verdict: {result.verdict})",
                accepted,
            )


@lru_cache(maxsize=1)
def candidate_metamodel():
    """Build (once) the textX metamodel with its semantic checks."""
    metamodel = metamodel_from_file(str(GRAMMAR), autokwd=True)
    metamodel.register_obj_processors({
        "SkillGroup": _check_skill_group,
        "ContactInfo": _check_contact,
        "Duration": _check_duration,
    })
    metamodel.register_model_processor(_check_profile)
    return metamodel


def parse_candidate_profile(source: str):
    """Parse and validate DSL text; raise ``TextXError`` if it is invalid."""
    return candidate_metamodel().model_from_str(source)


def parse_candidate_profile_file(path: str | Path):
    """Parse and validate a DSL file; raise ``TextXError`` if it is invalid."""
    return candidate_metamodel().model_from_file(str(path))
