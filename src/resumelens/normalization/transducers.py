"""Stage 2 finite-state transducers built with pyformlang.

T1 (cleaning): letters -> uppercase, separators -> epsilon, ``+``/``#`` kept.
T2 (aliases):  a trie over cleaned aliases; the canonical token is emitted
               only when the end marker is consumed, so ``JAVA`` and
               ``JAVASCRIPT`` do not interfere.
The output of T1 is the input of T2 (sequential composition T2 ∘ T1).
"""

from __future__ import annotations

from functools import lru_cache
from string import ascii_uppercase
from typing import Sequence

from pyformlang.fst import FST

from .catalog import END, KEPT_SYMBOLS, SEPARATORS, alias_keys

MAX_OUTPUT = 128  # pyformlang may cap output length by default


@lru_cache(maxsize=1)
def build_cleaning_transducer() -> FST:
    """T1: one looping state, final state reached by the end marker."""
    fst = FST()
    fst.add_start_state("q0")
    fst.add_final_state("qf")
    for letter in ascii_uppercase:
        fst.add_transition("q0", letter, "q0", [letter])
        fst.add_transition("q0", letter.lower(), "q0", [letter])
    for symbol in KEPT_SYMBOLS:
        fst.add_transition("q0", symbol, "q0", [symbol])
    for separator in SEPARATORS:
        fst.add_transition("q0", separator, "q0", [])
    fst.add_transition("q0", END, "qf", [END])
    return fst


@lru_cache(maxsize=1)
def build_alias_transducer() -> FST:
    """T2: trie of cleaned aliases; emits the token on the end marker."""
    fst = FST()
    fst.add_start_state("q0")
    fst.add_final_state("qf")
    state_of = {"": "q0"}
    for key, token in sorted(alias_keys().items()):
        prefix = ""
        for char in key:
            target = prefix + char
            if target not in state_of:
                state_of[target] = f"p:{target}"
                fst.add_transition(state_of[prefix], char, state_of[target], [])
            prefix = target
        fst.add_transition(state_of[key], END, "qf", [token])
    return fst


def run_transducer(fst: FST, symbols: Sequence[str]) -> list[str] | None:
    """Return the first translation of ``symbols`` or ``None`` if rejected."""
    try:
        outputs = fst.translate(list(symbols), max_length=MAX_OUTPUT)
    except TypeError:  # versions without the max_length parameter
        outputs = fst.translate(list(symbols))
    for output in outputs:
        return list(output)
    return None