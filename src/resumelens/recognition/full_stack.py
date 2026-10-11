"""Stage 3 DFA for the Full Stack Developer profile, built with pyformlang."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Sequence

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

from ..normalization import normalize_text
from ..normalization.catalog import CATALOG
from ..profiles import FULL_STACK, sort_tokens

PROFILE = "full_stack"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"


_GROUPS = dict(FULL_STACK.groups)
L = _GROUPS["frontend_language"]  # JAVASCRIPT, TYPESCRIPT
F = _GROUPS["frontend_framework"]  # REACT, ANGULAR, VUE
B = _GROUPS["backend"]  # NODE_JS, DJANGO, SPRING_BOOT, FLASK, FASTAPI, EXPRESS
A = _GROUPS["api"]  # REST_API (optional group)
D = _GROUPS["database"]  # POSTGRESQL, MYSQL, SQLITE, MONGODB, REDIS, ORACLE, SQL_SERVER
V = _GROUPS["version_control"]  # GIT

START = "q0"
DEAD = "q_dead"
FINAL = "q_V"
STATES = (START, "q_L", "q_F", "q_B", "q_A", "q_D", FINAL, DEAD)

TRANSITIONS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (START, L, "q_L"),
    ("q_L", L, "q_L"),
    ("q_L", F, "q_F"),
    ("q_F", F, "q_F"),
    ("q_F", B, "q_B"),
    ("q_B", B, "q_B"),
    ("q_B", A, "q_A"),
    ("q_B", D, "q_D"),  # REST_API is optional
    ("q_A", A, "q_A"),
    ("q_A", D, "q_D"),
    ("q_D", D, "q_D"),
    ("q_D", V, FINAL),
    (FINAL, V, FINAL),
)


@lru_cache(maxsize=1)
def build_full_stack_dfa() -> DeterministicFiniteAutomaton:

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


def run_full_stack(sequence: Sequence[str]) -> list[str]:

    dfa = build_full_stack_dfa()
    state = State(START)
    path = [START]
    for token in sequence:
        targets = dfa(state, Symbol(token))  # [] for a token outside Σ
        state = targets[0] if targets else State(DEAD)
        path.append(str(state.value))
    return path


@dataclass(frozen=True)
class FullStackResult:

    sequence: list[str]
    outside_profile: list[str]
    path: list[str]
    verdict: str
    profile: str = FULL_STACK.name

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recognize_full_stack(tokens: Sequence[str]) -> FullStackResult:
    sequence, outside = sort_tokens(list(dict.fromkeys(tokens)), PROFILE)
    accepted = build_full_stack_dfa().accepts([Symbol(t) for t in sequence])
    return FullStackResult(
        sequence, outside, run_full_stack(sequence),
        ACCEPTED if accepted else REJECTED,
    )


def recognize_full_stack_text(text: str) -> FullStackResult:
    return recognize_full_stack(normalize_text(text).tokens)
