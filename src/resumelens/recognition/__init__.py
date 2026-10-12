"""Stage 3: profile qualification pattern recognition with finite automata."""

from __future__ import annotations

from typing import Any, Callable, Sequence

from .data_engineer import recognize_data_engineer
from .devops import recognize_devops
from .full_stack import ACCEPTED, REJECTED, recognize_full_stack
from .ml_engineer import recognize_ml_engineer

# Profile name (as used in Stage 4) -> recognizer, in evaluation order.
RECOGNIZERS: dict[str, Callable[[Sequence[str]], Any]] = {
    "FULL_STACK_DEVELOPER": recognize_full_stack,
    "MACHINE_LEARNING_ENGINEER": recognize_ml_engineer,
    "DEVOPS_ENGINEER": recognize_devops,
    "DATA_ENGINEER": recognize_data_engineer,
}


def recognize_all(tokens: Sequence[str]) -> list[Any]:
    """Run the four profile DFAs over the same normalized tokens."""
    return [recognize(tokens) for recognize in RECOGNIZERS.values()]


__all__ = ["ACCEPTED", "REJECTED", "RECOGNIZERS", "recognize_all"]
