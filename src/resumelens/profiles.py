"""Profile configuration: canonical order of tokens per professional profile.

The order is application logic, not a string transformation, so it lives
outside the transducers. Adding a profile only requires a new ``ProfileSpec``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileSpec:
    name: str
    groups: tuple[tuple[str, tuple[str, ...]], ...]  # (group name, tokens)

    def rank(self, token: str) -> tuple[int, int] | None:
        for group_index, (_, tokens) in enumerate(self.groups):
            if token in tokens:
                return group_index, tokens.index(token)
        return None


FULL_STACK = ProfileSpec(
    "FULL_STACK_DEVELOPER",
    (
        ("frontend_language", ("JAVASCRIPT", "TYPESCRIPT")),
        ("frontend_framework", ("REACT", "ANGULAR", "VUE")),
        (
            "backend",
            ("NODE_JS", "DJANGO", "SPRING_BOOT", "FLASK", "FASTAPI", "EXPRESS"),
        ),
        ("api", ("REST_API",)),
        (
            "database",
            ("POSTGRESQL", "MYSQL", "SQLITE", "MONGODB", "REDIS", "ORACLE",
             "SQL_SERVER"),
        ),
        ("version_control", ("GIT",)),
    ),
)

ML_ENGINEER = ProfileSpec(
    "MACHINE_LEARNING_ENGINEER",
    (
        ("language", ("PYTHON",)),
        ("data_libraries", ("PANDAS", "NUMPY")),
        ("ml_frameworks", ("SCIKIT_LEARN", "TENSORFLOW", "PYTORCH")),
        ("ml_practice", ("ML_MODEL_DEVELOPMENT",)),
        ("sql", ("SQL", "POSTGRESQL")),
        ("version_control", ("GIT",)),
    ),
)

PROFILES: dict[str, ProfileSpec] = {
    "full_stack": FULL_STACK,
    "ml_engineer": ML_ENGINEER,
}


def sort_tokens(tokens: list[str], profile: str) -> tuple[list[str], list[str]]:
    """Return (tokens in the profile's canonical order, tokens outside it)."""
    spec = PROFILES[profile]
    ranked = [(spec.rank(token), token) for token in tokens]
    inside = sorted((r, t) for r, t in ranked if r is not None)
    outside = [t for r, t in ranked if r is None]
    return [t for _, t in inside], outside