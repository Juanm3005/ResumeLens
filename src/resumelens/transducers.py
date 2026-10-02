"""Character-level finite-state transducers for Stage 2 normalization."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import count

WS = "<WS>"  # marcador: uno o más caracteres de espacio en blanco
WHITESPACE = (" ", "\t", "\n", "\r")


@dataclass(frozen=True)
class TransducerSpec:
    canonical: str
    patterns: tuple[tuple[str, ...], ...]  # cada patrón: trozos literales y/o WS


def _spec(canonical: str, *patterns: tuple[str, ...]) -> TransducerSpec:
    return TransducerSpec(canonical, patterns or ((canonical.lower(),),))


ALIAS_SPECS = (
    _spec("JAVASCRIPT", ("js",), ("javascript",)),
    _spec("TYPESCRIPT", ("typescript",)),
    _spec("CPP", ("c++",)),
    _spec("C_SHARP", ("c#",)),
    _spec("REACT", ("react",), ("react.js",), ("reactjs",)),
    _spec("VUE", ("vue",), ("vue.js",)),
    _spec("NODE_JS", ("node.js",), ("nodejs",)),
    _spec("EXPRESS", ("express",), ("express.js",)),
    _spec("SPRING_BOOT", ("spring", WS, "boot")),
    _spec("SCIKIT_LEARN", ("scikit-learn",), ("scikit", WS, "learn"), ("sklearn",)),
    _spec("TENSORFLOW", ("tensorflow",), ("tensor", WS, "flow")),
    _spec("PYTORCH", ("pytorch",), ("py", WS, "torch")),
    _spec("POSTGRESQL", ("postgres",), ("postgresql",)),
    _spec("SQL_SERVER", ("sql", WS, "server")),
    _spec(
        "REST_API",
        ("rest", WS, "api"), ("rest", WS, "apis"),
        ("restful", WS, "api"), ("restful", WS, "apis"),
    ),
)

# Nombres sin alias: solo cambian a mayúsculas.
_PLAIN = (
    "Python Java Ruby PHP Kotlin Swift Rust SQL Angular Django Flask FastAPI "
    "Pandas NumPy MySQL SQLite MongoDB Redis Oracle Git Docker Kubernetes "
    "AWS Azure GCP Linux"
).split()
PLAIN_SPECS = tuple(_spec(name.upper()) for name in _PLAIN)

ALL_SPECS = ALIAS_SPECS + PLAIN_SPECS


def build_transducer(spec: TransducerSpec):
    """Build a deterministic character-level FST from a spec.

    Output is emitted on the first transition (from q0); the rest emit ε.
    Only paths that end in a final state yield output when translating.
    """
    from pyformlang.fst import FST

    fst = FST()
    fst.add_start_state("q0")
    ids, trie, finals = count(1), {}, set()

    def add(src, symbol, dst, out):
        fst.add_transition(src, symbol, dst, out)

    for pattern in spec.patterns:
        state = "q0"
        for chunk in pattern:
            if chunk == WS:
                key = (state, WS)
                if key not in trie:
                    nxt = f"q{next(ids)}"
                    trie[key] = nxt
                    for c in WHITESPACE:
                        add(state, c, nxt, [])
                        add(nxt, c, nxt, [])
                state = trie[key]
                continue
            for ch in chunk:
                key = (state, ch.lower())
                if key not in trie:
                    nxt = f"q{next(ids)}"
                    trie[key] = nxt
                    out = [spec.canonical] if state == "q0" else []
                    for variant in {ch.lower(), ch.upper()}:
                        add(state, variant, nxt, out)
                state = trie[key]
        finals.add(state)

    for state in finals:
        fst.add_final_state(state)
    return fst


@lru_cache(maxsize=None)
def get_transducer(canonical: str):
    spec = next(s for s in ALL_SPECS if s.canonical == canonical)
    return build_transducer(spec)


def transduce(canonical: str, raw: str) -> str | None:
    """Return the canonical token if the transducer accepts ``raw``."""
    outputs = list(get_transducer(canonical).translate(list(raw)))
    return "".join(outputs[0]) if outputs else None