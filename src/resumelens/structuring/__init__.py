"""Stage 4: structured candidate-profile validation with a CFG and textX."""

from .builder import build_candidate_profile
from .dsl import (
    candidate_metamodel,
    parse_candidate_profile,
    parse_candidate_profile_file,
)

__all__ = [
    "build_candidate_profile",
    "candidate_metamodel",
    "parse_candidate_profile",
    "parse_candidate_profile_file",
]
