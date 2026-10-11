"""Stage 3 DFA for the DevOps Engineer profile, built with pyformlang."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Sequence

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol

from ..normalization import normalize_text
from ..normalization.catalog import CATALOG
from ..profiles import DEVOPS, sort_tokens

PROFILE = "devops"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"


_GROUPS = dict(DEVOPS.groups)
O = _GROUPS["operating_system"]  # LINUX
P = _GROUPS["scripting"]  # PYTHON (optional group)
C = _GROUPS["containers"]  # DOCKER
K = _GROUPS["orchestration"]  # KUBERNETES (optional group)
N = _GROUPS["cloud"]  # AWS, AZURE, GCP
V = _GROUPS["version_control"]  # GIT

START = "q0"
DEAD = "q_dead"
FINAL = "q_V"
STATES = (START, "q_O", "q_P", "q_C", "q_K", "q_N", FINAL, DEAD)

TRANSITIONS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (START, O, "q_O"),
    ("q_O", O, "q_O"),
    ("q_O", P, "q_P"),
    ("q_O", C, "q_C"),  # PYTHON is optional
    ("q_P", P, "q_P"),
    ("q_P", C, "q_C"),
    ("q_C", C, "q_C"),
    ("q_C", K, "q_K"),
    ("q_C", N, "q_N"),  # KUBERNETES is optional
    ("q_K", K, "q_K"),
    ("q_K", N, "q_N"),
    ("q_N", N, "q_N"),
    ("q_N", V, FINAL),
    (FINAL, V, FINAL),
)


@lru_cache(maxsize=1)
def build_devops_dfa() -> DeterministicFiniteAutomaton:

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


def run_devops(sequence: Sequence[str]) -> list[str]:

    dfa = build_devops_dfa()
    state = State(START)
    path = [START]
    for token in sequence:
        targets = dfa(state, Symbol(token))  # [] for a token outside Σ
        state = targets[0] if targets else State(DEAD)
        path.append(str(state.value))
    return path


@dataclass(frozen=True)
class DevOpsResult:

    sequence: list[str]
    outside_profile: list[str]
    path: list[str]
    verdict: str
    profile: str = DEVOPS.name

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def recognize_devops(tokens: Sequence[str]) -> DevOpsResult:
    sequence, outside = sort_tokens(list(dict.fromkeys(tokens)), PROFILE)
    accepted = build_devops_dfa().accepts([Symbol(t) for t in sequence])
    return DevOpsResult(
        sequence, outside, run_devops(sequence),
        ACCEPTED if accepted else REJECTED,
    )


def recognize_devops_text(text: str) -> DevOpsResult:
    return recognize_devops(normalize_text(text).tokens)
