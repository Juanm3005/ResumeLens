"""Canonical qualification catalog: the single source of truth for Stage 2.

``CATALOG`` maps each canonical token to the written variants (aliases) that
Stage 1 can emit. The transducers, tests and documentation derive from it.
"""

from __future__ import annotations

END = "⊣"  # end-of-string marker appended to every input word
SEPARATORS = (" ", "\t", "\r", "\n", "-", ".", "_")
KEPT_SYMBOLS = ("+", "#")  # significant in C++ and C#

CATALOG: dict[str, tuple[str, ...]] = {
    # Programming languages
    "JAVASCRIPT": ("JavaScript", "Javascript", "JS"),
    "TYPESCRIPT": ("TypeScript",),
    "JAVA": ("Java",),
    "C_PLUS_PLUS": ("C++",),
    "C_SHARP": ("C#",),
    "PYTHON": ("Python",),
    "RUBY": ("Ruby",),
    "PHP": ("PHP",),
    "KOTLIN": ("Kotlin",),
    "SWIFT": ("Swift",),
    "RUST": ("Rust",),
    "SQL": ("SQL",),
    # Frameworks and libraries
    "REACT": ("React", "React.js", "ReactJS"),
    "ANGULAR": ("Angular",),
    "VUE": ("Vue", "Vue.js"),
    "NODE_JS": ("Node.js", "NodeJS"),
    "DJANGO": ("Django",),
    "SPRING_BOOT": ("Spring Boot",),
    "FLASK": ("Flask",),
    "FASTAPI": ("FastAPI",),
    "EXPRESS": ("Express", "Express.js"),
    "PANDAS": ("Pandas",),
    "NUMPY": ("NumPy",),
    "SCIKIT_LEARN": ("Scikit-learn", "scikit learn", "sklearn"),
    "TENSORFLOW": ("TensorFlow", "Tensor Flow"),
    "PYTORCH": ("PyTorch", "Py Torch"),
    # Databases
    "POSTGRESQL": ("PostgreSQL", "Postgres"),
    "MYSQL": ("MySQL",),
    "SQLITE": ("SQLite",),
    "MONGODB": ("MongoDB",),
    "REDIS": ("Redis",),
    "ORACLE": ("Oracle",),
    "SQL_SERVER": ("SQL Server",),
    # Tools and technologies
    "GIT": ("Git",),
    "DOCKER": ("Docker",),
    "KUBERNETES": ("Kubernetes",),
    "REST_API": ("REST API", "REST APIs", "RESTful API", "RESTful APIs"),
    "AWS": ("AWS",),
    "AZURE": ("Azure",),
    "GCP": ("GCP",),
    "LINUX": ("Linux",),
    # Prose qualifications (other_qualifications in Stage 1)
    "ML_MODEL_DEVELOPMENT": (
        "machine-learning model development",
        "machine learning model development",
    ),
    "PREDICTIVE_MODELS": ("predictive model", "predictive models"),
    "DATA_PROCESSING_PIPELINE": (
        "data-processing pipeline",
        "data-processing pipelines",
        "data processing pipeline",
        "data processing pipelines",
    ),
    "WEB_APPLICATIONS": ("web application", "web applications"),
    "BACKEND_SERVICES": ("backend service", "backend services"),
}


def clean_key(alias: str) -> str:
    """Pure-Python mirror of T1: uppercase and drop separators."""
    return "".join(
        char.upper() for char in alias if char not in SEPARATORS
    )


def alias_keys() -> dict[str, str]:
    """Return ``{cleaned alias: canonical token}``; reject ambiguous aliases."""
    keys: dict[str, str] = {}
    for token, aliases in CATALOG.items():
        for alias in (*aliases, token):
            key = clean_key(alias)
            if keys.setdefault(key, token) != token:
                raise ValueError(
                    f"alias {alias!r} maps to both {keys[key]} and {token}"
                )
    return keys