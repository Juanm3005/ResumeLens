"""Regular-expression catalog used by the stage-one extractor.

Patterns recognize text only. They deliberately do not map aliases to a
canonical technology name; that belongs to the normalization stage.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PatternDefinition:
    """A regex, its output category, and a short description of its target."""

    category: str
    pattern: str
    description: str


# The order is stable for predictable output. Alternatives include textual
# variants as separate raw matches (for example, JS and JavaScript).
SKILL_PATTERNS = (
    PatternDefinition(
        "programming_languages",
        r"(?<![\w+#.])(?:JavaScript|Javascript|JS|TypeScript|Java|C\+\+|C#|Python|Ruby|PHP|Kotlin|Swift|Rust|SQL)(?![\w+#])",
        "Named programming and query languages, including the literal abbreviation JS.",
    ),
    PatternDefinition(
        "frameworks_libraries",
        r"(?<![\w.])(?:React(?:\.js|JS)?|Angular|Vue(?:\.js)?|Node(?:\.js|JS)|Django|Spring\s+Boot|Flask|FastAPI|Express(?:\.js)?|Pandas|NumPy|Scikit[- ]learn|scikit\s+learn|sklearn|Tensor\s*Flow|Py\s*Torch)(?!\w|\.(?:js))",
        "Framework and library names, including common written variants.",
    ),
    PatternDefinition(
        "databases",
        r"(?<![\w.])(?:PostgreSQL|Postgres|MySQL|SQLite|MongoDB|Redis|Oracle|SQL\s+Server)(?!\w)",
        "Named database products and systems.",
    ),
    PatternDefinition(
        "tools_and_technologies",
        r"(?<![\w.])(?:Git|Docker|Kubernetes|REST(?:ful)?\s+APIs?|AWS|Azure|GCP|Linux)(?!\w)",
        "Development tools, cloud platforms, operating systems, and REST APIs.",
    ),
)

# Explicit non-technology phrases from the supported reference profiles.
OTHER_QUALIFICATION_PATTERNS = (
    PatternDefinition(
        "software_development",
        r"(?<!\w)(?:web\s+applications?|backend\s+services?)(?!\w)",
        "Web application and backend service experience mentioned in prose.",
    ),
    PatternDefinition(
        "machine_learning",
        r"(?<!\w)(?:machine[- ]learning\s+model\s+development|predictive\s+models?)(?!\w)",
        "Machine-learning model development and predictive model experience.",
    ),
    PatternDefinition(
        "data_processing",
        r"(?<!\w)data[- ]processing\s+pipelines?(?!\w)",
        "Data-processing pipeline experience mentioned in prose.",
    ),
)

EMAIL_PATTERN = (
    r"(?<![\w.+-])[\w.!#$%&'*+/=?^_{}|~-]+@"
    r"[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?"
    r"(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+"
)

# Accept common international/national formatting and unseparated 10–15 digit
# numbers. extract_resume additionally rejects date-shaped candidates.
PHONE_PATTERN = (
    r"(?<!\w)(?:\+\d{1,3}[ .-]?)?"
    r"(?:\(?\d{2,4}\)?[ .-])?\d{3,4}[ .-]\d{3,4}(?!\w)"
    r"|(?<!\w)\+?\d{10,15}(?!\w)"
)

URL_PATTERN = r"(?i)\b(?:https?://|www\.)[^\s<>()]+"

ACADEMIC_DEGREE_PATTERN = (
    r"(?<!\w)(?:"
    r"Bachelor(?:'s)?(?:\s+(?:degree|of\s+(?:Science|Arts|Engineering)))?"
    r"|B\.?\s?Sc\.?|B\.?\s?A\.?|B\.?\s?Eng\.?"
    r"|Master(?:'s)?(?:\s+(?:degree|of\s+(?:Science|Arts|Engineering)))?"
    r"|M\.?\s?Sc\.?|M\.?\s?A\.?|M\.?\s?Eng\.?"
    r"|Ph\.?\s?D\.?|doctorate|associate(?:'s)?(?:\s+degree)?"
    r")(?!\w)"
)

EXPERIENCE_PATTERNS = (
    r"(?<!\w)\d+(?:\.\d+)?\s*\+?\s*(?:years?|yrs?)\s+"
    r"(?:of\s+)?(?:professional\s+)?experience(?!\w)",
    r"(?<!\w)experience\s*(?:of|:)?\s*\d+(?:\.\d+)?\s*\+?\s*"
    r"(?:years?|yrs?)(?!\w)",
)

# Extract the raw content under a conventional work-experience heading until
# the next common résumé section. This supplements duration-only matches.
EXPERIENCE_SECTION_HEADER_PATTERN = (
    r"(?im)^[ \t]*(?:(?:professional|work)[ \t]+)?experience"
    r"(?:[ \t]+history)?[ \t]*:?[ \t]*(?:\r?\n|$)"
)
OTHER_SECTION_HEADER_PATTERN = (
    r"(?im)^[ \t]*(?:education|academic(?:[ \t]+background)?|"
    r"technical[ \t]+skills|skills|projects?|certifications?|"
    r"contact(?:[ \t]+information)?|summary|profile|languages?|"
    r"publications?|awards?|references?|training)[ \t]*:?[ \t]*(?:\r?\n|$)"
)
