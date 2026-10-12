"""Stage 3 DFA for the Machine Learning Engineer profile, built with pyformlang."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Sequence

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

from ..normalization import normalize_text
from ..normalization.catalog import CATALOG
from ..profiles import ML_ENGINEER, sort_tokens

PROFILE = "ml_engineer"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"


_GROUPS = dict(ML_ENGINEER.groups)
P = _GROUPS["language"]  # PYTHON
L = _GROUPS["data_libraries"]  # PANDAS, NUMPY
M = _GROUPS["ml_frameworks"]  # SCIKIT_LEARN, TENSORFLOW, PYTORCH
E = _GROUPS["ml_practice"]  # ML_MODEL_DEVELOPMENT (optional group)
S = _GROUPS["sql"]  # SQL, POSTGRESQL
V = _GROUPS["version_control"]  # GIT

START = "q0"
DEAD = "q_dead"
FINAL = "q_V"
STATES = (START, "q_P", "q_L", "q_M", "q_E", "q_S", FINAL, DEAD)

TRANSITIONS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (START, P, "q_P"),
    ("q_P", P, "q_P"),
    ("q_P", L, "q_L"),
    ("q_L", L, "q_L"),
    ("q_L", M, "q_M"),
    ("q_M", M, "q_M"),
    ("q_M", E, "q_E"),
    ("q_M", S, "q_S"),  # ML_MODEL_DEVELOPMENT is optional
    ("q_E", E, "q_E"),
    ("q_E", S, "q_S"),
    ("q_S", S, "q_S"),
    ("q_S", V, FINAL),
    (FINAL, V, FINAL),
)


@lru_cache(maxsize=1)
def build_ml_engineer_dfa() -> DeterministicFiniteAutomaton:

    delta = {
        (source, token): target
        for source, tokens, target in TRANSITIONS
        for token in tokens
    }
    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state(State(START))
    dfa.add_final_state(State(FINAL))
    for source in STATES:
        for token in CATALOG:
            target = delta.get((source, token), DEAD)
            dfa.add_transition(State(source), Symbol(token), State(target))
    return dfa


def run_ml_engineer(sequence: Sequence[str]) -> list[str]:

    dfa = build_ml_engineer_dfa()
    state = State(START)
    path = [START]
    for token in sequence:
        targets = dfa(state, Symbol(token))  # [] for a token outside Σ
        state = targets[0] if targets else State(DEAD)
        path.append(str(state.value))
    return path


@dataclass(frozen=True)
class MLEngineerResult:

    sequence: list[str]
    outside_profile: list[str]
    path: list[str]
    verdict: str
    profile: str = ML_ENGINEER.name

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recognize_ml_engineer(tokens: Sequence[str]) -> MLEngineerResult:
    sequence, outside = sort_tokens(list(dict.fromkeys(tokens)), PROFILE)
    accepted = build_ml_engineer_dfa().accepts([Symbol(t) for t in sequence])
    return MLEngineerResult(
        sequence, outside, run_ml_engineer(sequence),
        ACCEPTED if accepted else REJECTED,
    )


def recognize_ml_engineer_text(text: str) -> MLEngineerResult:
    return recognize_ml_engineer(normalize_text(text).tokens)
