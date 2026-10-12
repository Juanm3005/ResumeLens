"""Stage 4: structured candidate-profile validation with a CFG and textX."""


from .dsl import (
    candidate_metamodel,
    parse_candidate_profile,
    parse_candidate_profile_file,
)

__all__ = [
    "candidate_metamodel",
    "parse_candidate_profile",
    "parse_candidate_profile_file",
]
