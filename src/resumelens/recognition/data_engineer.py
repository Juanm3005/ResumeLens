"""Stage 3 DFA for the Data Engineer profile, built with pyformlang."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Sequence

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

from ..normalization import normalize_text
from ..normalization.catalog import CATALOG
from ..profiles import DATA_ENGINEER, sort_tokens

PROFILE = "data_engineer"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"


_GROUPS = dict(DATA_ENGINEER.groups)
L = _GROUPS["language"]  # PYTHON, JAVA
Q = _GROUPS["query_language"]  # SQL
H = _GROUPS["data_libraries"]  # PANDAS, NUMPY (optional group)
D = _GROUPS["database"]  # POSTGRESQL, MYSQL, SQLITE, MONGODB, REDIS, ORACLE, SQL_SERVER
P = _GROUPS["pipelines"]  # DATA_PROCESSING_PIPELINE (optional group)
N = _GROUPS["cloud"]  # AWS, AZURE, GCP
V = _GROUPS["version_control"]  # GIT

START = "q0"
DEAD = "q_dead"
FINAL = "q_V"
STATES = (START, "q_L", "q_Q", "q_H", "q_D", "q_P", "q_N", FINAL, DEAD)

TRANSITIONS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (START, L, "q_L"),
    ("q_L", L, "q_L"),
    ("q_L", Q, "q_Q"),
    ("q_Q", Q, "q_Q"),
    ("q_Q", H, "q_H"),
    ("q_Q", D, "q_D"),  # PANDAS / NUMPY are optional
    ("q_H", H, "q_H"),
    ("q_H", D, "q_D"),
    ("q_D", D, "q_D"),
    ("q_D", P, "q_P"),
    ("q_D", N, "q_N"),  # DATA_PROCESSING_PIPELINE is optional
    ("q_P", P, "q_P"),
    ("q_P", N, "q_N"),
    ("q_N", N, "q_N"),
    ("q_N", V, FINAL),
    (FINAL, V, FINAL),
)


@lru_cache(maxsize=1)
def build_data_engineer_dfa() -> DeterministicFiniteAutomaton:

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


def run_data_engineer(sequence: Sequence[str]) -> list[str]:

    dfa = build_data_engineer_dfa()
    state = State(START)
    path = [START]
    for token in sequence:
        targets = dfa(state, Symbol(token))  # [] for a token outside Σ
        state = targets[0] if targets else State(DEAD)
        path.append(str(state.value))
    return path


@dataclass(frozen=True)
class DataEngineerResult:

    sequence: list[str]
    outside_profile: list[str]
    path: list[str]
    verdict: str
    profile: str = DATA_ENGINEER.name

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recognize_data_engineer(tokens: Sequence[str]) -> DataEngineerResult:
    sequence, outside = sort_tokens(list(dict.fromkeys(tokens)), PROFILE)
    accepted = build_data_engineer_dfa().accepts([Symbol(t) for t in sequence])
    return DataEngineerResult(
        sequence, outside, run_data_engineer(sequence),
        ACCEPTED if accepted else REJECTED,
    )


def recognize_data_engineer_text(text: str) -> DataEngineerResult:
    return recognize_data_engineer(normalize_text(text).tokens)
