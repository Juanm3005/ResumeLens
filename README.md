# ResumeLens

ResumeLens is an academic project that processes résumés written as plain text and checks whether their explicit qualifications match patterns defined for professional profiles. The project applies formal language models so that each stage has a well-defined function and verifiable results.

ResumeLens **does not rank candidates, recommend hires, or make employment decisions**. It only processes information written in the résumé and evaluates previously defined patterns.

## Project context and goal

Résumés present the same qualification in several ways: for example, `JavaScript`, `Javascript`, and `JS`; or `Scikit-learn`, `sklearn`, and `scikit learn`. They also organize education, experience, and skills in different formats. ResumeLens extracts those mentions, normalizes their variants, compares them with professional profiles, and validates a structured representation of the results.

The system must process four profiles using a single solution:

1. **Full Stack Developer**, the software engineering reference profile.
2. **Machine Learning Engineer**, the AI and data reference profile.
3. An additional software engineering profile defined by the team.
4. An additional AI or data profile defined by the team.

The two additional profiles chosen by the team are **DevOps Engineer** (software engineering) and **Data Engineer** (AI/data). Their patterns are described in [docs/stage-3-recognition.md](docs/stage-3-recognition.md).

## System overview

The complete project is organized into these stages:

| Stage | Model | Purpose | Status in this repository |
| --- | --- | --- | --- |
| 1. Extraction | Regular expressions with Python's `re` | Detect contact data, qualifications, education, and experience, keeping the original mentions. | Implemented and tested. |
| 2. Normalization | Finite-state transducers with `pyformlang` | Convert explicit qualification variants into canonical names. | Implemented and tested: two transducers (cleaning and alias → token) over a catalog of 46 tokens. |
| 3. Profile recognition | Finite automata with `pyformlang` | Check whether the ordered set of qualifications satisfies a profile pattern. | Implemented: one DFA for each of the four profiles. |
| 4. Structuring | Context-free grammar and `textX` | Validate a DSL representation of the information and the profile result. | Implemented and tested: EBNF grammar in `textX`, semantic checks, generator from stages 1–3. |
| 5. Visualization | HTML | Present the validated structured information. | Implemented and tested: standalone HTML page rendered from the validated model. |

The output of each stage feeds the next one. The pipeline implemented today is **UTF-8 text → extraction (literal mentions) → normalization (canonical tokens ordered by profile) → recognition (ACCEPTED / REJECTED per profile) → structuring (validated candidate-profile DSL listing every accepted profile) → visualization (HTML page)**.

## Status and scope of this delivery

**All five stages** are implemented:

- **Stage 1:** extraction with regular expressions, with a Python API, a command-line interface, pattern documentation, and a regression dataset.
- **Stage 2:** normalization with two `pyformlang` finite-state transducers generated from a single alias catalog, plus canonical ordering per profile.
- **Stage 3:** one deterministic finite automaton per profile (Full Stack, Machine Learning, DevOps, and Data Engineer).
- **Stage 4:** a candidate-profile DSL defined with a context-free grammar in `textX`, with lexical, syntactic, and semantic validation.
- **Stage 5:** an HTML visualization of the validated profile, based on the sample page of the assignment.

Each stage respects its boundary. Extraction keeps the text literally as written: `JS` is still `JS` in stage 1. The alias becomes `JAVASCRIPT` in stage 2, and only stage 3 decides whether the set of tokens satisfies a profile.

## Stage 1: extraction

### Goal and inputs

The extractor receives a Python string with the content of a résumé. The command-line interface reads UTF-8 plain-text files (`.txt`). Converting PDF, DOCX, or images to text is not part of this stage.

The assignment states that each relevant type of information must have a defined regular expression, an explanation of the pattern it recognizes, an implementation with the `re` module, and a place to store the results. This implementation covers those points with the catalog in [`src/resumelens/extraction/patterns.py`](src/resumelens/extraction/patterns.py), the execution in [`src/resumelens/extraction/extraction.py`](src/resumelens/extraction/extraction.py), and the `ExtractionResult` model. The details of each regex, the language it recognizes, and its limits are in [docs/stage-1-extraction.md](docs/stage-1-extraction.md).

### Detected information

| Type | Examples of recognized text | Output representation |
| --- | --- | --- |
| Emails | `alex@example.com`, `Jane.Doe+work@Example.org` | `contacts.emails` |
| Phone numbers | `+57 300 123 4567`, `2025550142` | `contacts.phones`; common numeric dates are filtered out. |
| Links | URLs starting with `http://`, `https://`, or `www.` | `contacts.linkedin`, `contacts.github`, or `contacts.websites`, depending on the host. |
| Programming languages | `JavaScript`, `JS`, `TypeScript`, `Python`, `C++`, `SQL` | `skills.programming_languages` |
| Frameworks and libraries | `React.js`, `NodeJS`, `Django`, `Pandas`, `sklearn`, `TensorFlow`, `PyTorch` | `skills.frameworks_libraries` |
| Databases | `Postgres`, `PostgreSQL`, `MySQL`, `MongoDB`, `SQL Server` | `skills.databases` |
| Tools and technologies | `Git`, `Docker`, `Kubernetes`, `REST API`, `AWS`, `Linux` | `skills.tools_and_technologies` |
| Other qualifications from the reference profiles | `web applications`, `backend services`, `predictive models`, `data-processing pipelines`, `Machine-learning model development` | `other_qualifications`, grouped by topic. |
| Education | `Bachelor of Science`, `B.Sc.`, `Master's degree`, `PhD` | `academic_degrees` |
| Experience duration | `3 years of experience`, `Experience: 2.5 years`, `4+ yrs professional experience` | `experience` |
| Experience block | Text under `Experience`, `Work Experience`, or `Professional Experience` | `experience_sections`, up to the next recognized heading. |

The catalog is explicit and bounded: it does not automatically detect any new technology or phrase. To extend coverage, add an alternative to the appropriate pattern, explain what text it recognizes, and add a test case.

### How the patterns run

1. `patterns.py` defines each pattern and, for skill categories, its group and description through `PatternDefinition`.
2. `extract_resume(text)` validates the input and applies the patterns with `re.finditer`, usually with `re.IGNORECASE`. Heading expressions use the inline flags `(?im)` for case-insensitive multiline search.
3. Each match is stored as `ExtractionMatch(value, start, end)`. `value` copies the original fragment exactly; `start` and `end` are Python offsets, and `end` is exclusive.
4. URLs are classified by host and trailing sentence punctuation is removed. Phone candidates shaped like common dates are discarded.
5. Experience durations are extracted with regex; experience blocks are captured between a work-experience heading and the next common résumé heading.
6. The result is grouped into `ExtractionResult`, with stable empty categories, and can be serialized with `to_dict()` or `to_json()`.

Matches are not canonicalized or used to evaluate profiles at this stage. For example, `Python` appearing in a résumé does not imply that the person has a given level of proficiency.

### Output shape

Each mention contains its text and the offsets needed to recover it from the input. Simplified, the JSON includes:

```json
{
  "contacts": {
    "emails": [{"value": "alex@example.com", "start": 7, "end": 23}],
    "phones": [],
    "linkedin": [],
    "github": [],
    "websites": []
  },
  "skills": {
    "programming_languages": [{"value": "JS", "start": 31, "end": 33}],
    "frameworks_libraries": [],
    "databases": [],
    "tools_and_technologies": []
  },
  "other_qualifications": {
    "software_development": [],
    "machine_learning": [],
    "data_processing": []
  },
  "academic_degrees": [],
  "experience": [],
  "experience_sections": []
}
```

The indices in the example are illustrative; for each real input they are computed from the source string. The extended documentation includes the complete expressions and their recognition rules.

### Known limitations

- The CLI accepts UTF-8 plain text; it does not extract text from PDF, DOCX, or images.
- The catalog covers explicit vocabulary. A technology, abbreviation, or description that is not included will not be extracted.
- Degree names, durations, and headings are mainly oriented to résumés in English; variants in other languages can be added.
- Phone numbers are identified by shape and are not validated against a national numbering plan.
- The experience block depends on recognized headings on their own line; a different format may require extending the heading catalog.
- Explicit matches are not proof of proficiency or a hiring recommendation.

## Stage 2: normalization

### Goal and inputs

Stage 2 converts the literal mentions in `skills` and `other_qualifications` (for example `JS`, `React.js`, `scikit learn`, `Machine-learning model development`) into canonical tokens (`JAVASCRIPT`, `REACT`, `SCIKIT_LEARN`, `ML_MODEL_DEVELOPMENT`). Contact data, degrees, and years of experience have no equivalences to normalize and are left out. The formal definition of each transducer (7-tuple), its diagrams, and the design decisions are in [docs/stage-2-normalization.md](docs/stage-2-normalization.md).

### How it works

1. **T1, cleaning transducer:** converts to uppercase and removes spaces and separators (`-`, `.`, `_`), keeping `+` and `#`. This way `React.js`, `ReactJS`, and `react js` all produce `REACTJS`.
2. **T2, alias-to-token transducer:** a *trie* over the cleaned keys that emits the canonical token only when it reads the end marker `⊣`, so prefixes such as `JAVA`/`JAVASCRIPT` or `SQL`/`SQLITE` are not confused.
3. Both transducers are generated from [`normalization/catalog.py`](src/resumelens/normalization/catalog.py), the single source of truth for the 46 tokens and their aliases. An ambiguous alias stops construction with a `ValueError`.
4. Tokens are deduplicated. Values that T2 does not recognize are reported in `unrecognized`. If a profile is given, tokens are ordered according to [`profiles.py`](src/resumelens/profiles.py), and those the profile does not cover are placed in `outside_profile`.

### Output shape

`normalize_text(text, profile)` returns a `NormalizationResult`. Simplified, for `JS, React.js, NodeJS, Postgres, Git, Docker` with the `full_stack` profile:

```json
{
  "mentions": [{"value": "JS", "start": 35, "end": 37, "source": "skills.programming_languages", "token": "JAVASCRIPT"}],
  "tokens": ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT", "DOCKER"],
  "unrecognized": [],
  "profile": "full_stack",
  "ordered_tokens": ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"],
  "outside_profile": ["DOCKER"]
}
```

### Stage 2 limitations

- T1's alphabet is ASCII; a value with a character outside it (for example a digit) is rejected.
- The catalog is closed: a technology that is not listed appears in `unrecognized`.

## Stage 3: profile recognition

### Goal and inputs

Stage 3 receives the canonical tokens from stage 2 and decides, for each profile, whether they form an accepted qualification pattern. Each profile is modeled with a **deterministic finite automaton (DFA)** built with `pyformlang` in [`src/resumelens/recognition/`](src/resumelens/recognition/). The formal definition `M = (Q, Σ, δ, q0, F)`, the justification of the automaton type, the transition diagrams, and the examples for each profile are in [docs/stage-3-recognition.md](docs/stage-3-recognition.md).

### How it works

1. Tokens are deduplicated and sorted according to the profile's canonical order (`profiles.py`). Those the profile does not cover are reported in `outside_profile` and never reach the automaton.
2. The sorted sequence is the word read by the DFA. There is one state per qualification group, self-loops to allow several tokens from the same group, and direct transitions to skip optional groups.
3. Σ is the full catalog of 46 canonical tokens. Any unexpected transition leads to the sink state `q_dead`, so δ is total and the automaton is deterministic.
4. If the run ends in the accepting state `q_V`, the result is `ACCEPTED`; otherwise, `REJECTED`. The result also includes the state path.

### Profile patterns

| Profile | Module | Pattern (canonical order) |
| --- | --- | --- |
| Full Stack Developer | `full_stack.py` | `(JAVASCRIPT\|TYPESCRIPT)+ (REACT\|ANGULAR\|VUE)+ BACKEND+ REST_API* DATABASE+ GIT+` |
| Machine Learning Engineer | `ml_engineer.py` | `PYTHON+ (PANDAS\|NUMPY)+ (SCIKIT_LEARN\|TENSORFLOW\|PYTORCH)+ ML_MODEL_DEVELOPMENT* (SQL\|POSTGRESQL)+ GIT+` |
| DevOps Engineer | `devops.py` | `LINUX+ PYTHON* DOCKER+ KUBERNETES* (AWS\|AZURE\|GCP)+ GIT+` |
| Data Engineer | `data_engineer.py` | `(PYTHON\|JAVA)+ SQL+ (PANDAS\|NUMPY)* DATABASE+ DATA_PROCESSING_PIPELINE* (AWS\|AZURE\|GCP)+ GIT+` |

`BACKEND` groups `NODE_JS`, `DJANGO`, `SPRING_BOOT`, `FLASK`, `FASTAPI`, and `EXPRESS`; `DATABASE` groups the seven database engines in the catalog. Groups marked with `*` are optional.

### Example

```python
from resumelens.recognition.ml_engineer import recognize_ml_engineer

result = recognize_ml_engineer(["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"])
print(result.verdict)  # ACCEPTED
print(result.path)     # ['q0', 'q_P', 'q_L', 'q_M', 'q_S', 'q_V']
```

Each module also provides `recognize_<profile>_text(text)`, which runs extraction, normalization, and recognition on the résumé text. With the example résumés, each one is accepted only by its own profile.

### Stage 3 limitations

- A résumé that mentions `SQL Server` also produces the `SQL` token in stage 1, so it satisfies the SQL group of ML Engineer and Data Engineer.
- The team's profiles only use the current catalog vocabulary; tools such as Jenkins, Terraform, Spark, or Airflow are not recognized yet.
- The verdict depends on explicit mentions and does not evaluate experience or proficiency.
- There are no automated tests specific to this stage yet, and no command-line option for recognition.

## Stage 4: candidate profile language

### Goal and inputs

Stage 4 represents the results of stages 1–3 in a domain-specific language: personal information, contact data, education, experience, normalized skills, and **one `accepted` block for every profile whose automaton accepted the résumé** (or `none`). The grammar is in [`src/resumelens/structuring/candidate_profile.tx`](src/resumelens/structuring/candidate_profile.tx); the EBNF, the terminals and non-terminals, the structural characteristics, and the validation rules are in [docs/stage-4-structuring.md](docs/stage-4-structuring.md).

### Example

```text
candidate {
    personal { name: "Wednesday Addams"; }
    experience {
        total: 3 years;
        job { activity: "3 years of experience developing web applications."; }
    }
    skills {
        languages: JAVASCRIPT;
        frameworks: REACT, NODE_JS;
        databases: POSTGRESQL;
        tools: GIT;
        qualifications: WEB_APPLICATIONS;
    }
    classification {
        accepted FULL_STACK_DEVELOPER {
            sequence: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT;
        }
    }
}
```

[`examples/wednesday_addams.rlp`](examples/wednesday_addams.rlp) is a complete example accepted by two profiles (Full Stack Developer and Data Engineer).

### Validation

Documents are rejected when they break a lexical rule (lower-case token, malformed email or URL, unquoted free text), a syntactic rule (missing `;` or braces, sections out of order, empty blocks, unknown profile), or a semantic rule checked after parsing: tokens must be in the stage 2 catalog, nothing may be declared twice, and each accepted `sequence` must use declared skills and be accepted, in canonical order, by the profile's stage 3 DFA.

### Stage 4 limitations

- The candidate's name is taken from the first line of the résumé when it looks like a name.
- Each experience section becomes a single job; `role`, `location`, `title`, `organization`, and institutions are part of the language but are not extracted yet.

## Stage 5: HTML visualization

The renderer in [`src/resumelens/visualization/`](src/resumelens/visualization/) turns a **validated** stage 4 model into a standalone HTML page with the layout and styles of the assignment's sample ([`outputVisualization.html`](outputVisualization.html)): header with the name, personal information and contact links, summary, education, experience, normalized skills by category, and one evaluation block for each accepted profile. Empty sections are omitted and every value is HTML-escaped. Details are in [docs/stage-5-visualization.md](docs/stage-5-visualization.md).

[`examples/wednesday_addams.html`](examples/wednesday_addams.html) shows a résumé accepted by two profiles; [`examples/wednesday_addams_full.html`](examples/wednesday_addams_full.html) is rendered from a hand-written DSL with the data of the sample page.

## Installation and usage

A virtual environment is recommended to isolate this project's dependencies. Python 3.10 or later is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

On macOS or Linux, the activation command is `source .venv/bin/activate`; the other commands are the same. If the PowerShell execution policy prevents activating the environment, use `.\.venv\Scripts\python.exe` directly instead of `python` in the commands.

### Run the whole pipeline at once

[`run_pipeline.py`](run_pipeline.py) takes a résumé text file and runs the five stages in a row: extraction, normalization, profile recognition, structuring, and visualization. With the environment active, from the project root:

```powershell
python run_pipeline.py .\examples\enid_sinclair.txt
```

Add `--open` to open the HTML page in the browser when it finishes, and `--out <folder>` to use a base folder other than `visualizations/`:

```powershell
python run_pipeline.py .\examples\enid_sinclair.txt --open
```

Every stage result is saved in `visualizations/<résumé name>/` (the folder is created if needed and ignored by git):

| File | Stage | Content |
|---|---|---|
| `1_extraction.json` | 1. Extraction | Contacts, skills, degrees, and experience found by the regular expressions |
| `2_normalization.json` | 2. Normalization | Skills converted to canonical tokens by the transducers |
| `3_recognition.json` | 3. Recognition | `ACCEPTED`/`REJECTED` verdict and path of each profile automaton |
| `4_profile.rlp` | 4. Structuring | Candidate-profile DSL, validated with textX |
| `5_visualization.html` | 5. Visualization | HTML page rendered from the validated model |

The console also prints a summary of each stage:

```text
[1] Extraction     -> visualizations\enid_sinclair\1_extraction.json
[2] Normalization  -> ['DOCKER', 'KUBERNETES', 'AWS', 'PYTHON', 'SCIKIT_LEARN', ...]
[3] FULL_STACK_DEVELOPER         REJECTED
[3] MACHINE_LEARNING_ENGINEER    REJECTED
[3] DEVOPS_ENGINEER              ACCEPTED
[3] DATA_ENGINEER                ACCEPTED
[4] Structuring    -> visualizations\enid_sinclair\4_profile.rlp (valid)
[5] Visualization  -> visualizations\enid_sinclair\5_visualization.html
```

To try another candidate, write a `.txt` with the same layout as [`examples/enid_sinclair.txt`](examples/enid_sinclair.txt): the name on the first line, then `Email:`, `Phone:`, links, the years of experience, and the `Education:`, `Experience:`, and `Technical Skills:` sections. If the generated profile fails validation, stage 4 prints the textX error and no HTML page is written.

### Command-line options by stage

With the environment active, save the résumé text as `resume.txt` and run:

```powershell
python -m resumelens .\resume.txt
```

To save the JSON to a file:

```powershell
python -m resumelens .\resume.txt --output .\extraction.json
```

`-o` can also be used instead of `--output`. To get the normalized tokens from stage 2, optionally ordered by a profile (`full_stack`, `ml_engineer`, `devops`, or `data_engineer`):

```powershell
python -m resumelens .\resume.txt --normalize
python -m resumelens .\resume.txt --normalize --profile ml_engineer
```

To generate the stage 4 candidate-profile DSL and to validate an existing DSL document:

```powershell
python -m resumelens .\resume.txt --dsl -o .\profile.rlp
python -m resumelens .\profile.rlp --validate
```

To generate the stage 5 HTML page, from a résumé or from a validated DSL document:

```powershell
python -m resumelens .\resume.txt --html
python -m resumelens .\profile.rlp --validate --html
```

The page is written to `visualizations/<input name>.html` (the folder is created if needed and ignored by git); use `--html-dir` to choose another folder or `-o` for an exact file.

The Python API covers the five stages:

```python
from resumelens import extract_resume
from resumelens.normalization import normalize_text
from resumelens.recognition.full_stack import recognize_full_stack_text

text = "Skills: JS, React.js, NodeJS, Postgres, Git."
print(extract_resume(text).to_json())              # stage 1
print(normalize_text(text, "full_stack").to_dict())  # stage 2
print(recognize_full_stack_text(text).verdict)     # stage 3: ACCEPTED

from resumelens.structuring import build_candidate_profile, parse_candidate_profile
source = build_candidate_profile(text)             # stage 4: DSL text
model = parse_candidate_profile(source)            # validated textX model
print([a.profile for a in model.classification.accepted])

from resumelens.visualization import render_html
html_page = render_html(model)                     # stage 5: HTML text
```

## Tests and verification

With `.venv` active, run the full suite:

```powershell
python -m unittest discover -s tests -v
```

The dataset [`tests/fixtures/stage1_extraction_dataset.json`](tests/fixtures/stage1_extraction_dataset.json) contains **94 regression cases** with unique IDs. For stage 1, the suite covers the Full Stack and Machine Learning examples from the assignment, categories and variants, boundaries that prevent partial matches, contact data, Unicode offsets, JSON serialization, and console and file output. For stage 2, [`tests/test_normalization.py`](tests/test_normalization.py) covers every catalog alias, case and separators, prefixes, `C++`/`C#`, rejection of unknown values, deduplication, profile ordering, and that every value in the stage 1 dataset is normalized. For stage 4, [`tests/test_structuring.py`](tests/test_structuring.py) covers valid documents, each lexical, syntactic, and semantic rejection rule, the generator on the assignment examples and on a résumé accepted by two profiles, and the `--dsl`/`--validate` options. For stage 5, [`tests/test_visualization.py`](tests/test_visualization.py) covers every section of the page, several accepted profiles, empty sections, escaping, and the `--html` option. In total, 148 tests run. Stage 3 does not have its own automated tests yet.

## Dependencies

- `pyformlang` (`>=1.0,<2`): required dependency declared in `pyproject.toml`; used for the stage 2 transducers and the stage 3 automata. It is installed with `python -m pip install -e .`.
- `textX` (`>=4,<5`): required dependency; parses and validates the stage 4 grammar.
- `setuptools`: the package build backend.
- Stage 1 only uses the standard library (`re`).

## Repository structure

```text
src/resumelens/
  __init__.py                  Public API (extraction)
  __main__.py                  Entry point for python -m resumelens
  cli.py                       Text input and JSON/DSL output (--normalize, --profile, --dsl, --validate, --html, --html-dir)
  profiles.py                  Groups and canonical order of the four profiles
  normalization_preview.py     Initial stage 2 demo (JavaScript aliases only)
  extraction/                  Stage 1
    extraction.py              Extraction and result structures
    patterns.py                Regular expression catalog
  normalization/               Stage 2
    catalog.py                 Canonical tokens and their aliases
    transducers.py             Transducers T1 (cleaning) and T2 (alias → token)
    pipeline.py                Normalization of the extraction and profile ordering
  recognition/                 Stage 3
    full_stack.py              Full Stack Developer DFA
    ml_engineer.py             Machine Learning Engineer DFA
    devops.py                  DevOps Engineer DFA
    data_engineer.py           Data Engineer DFA
    __init__.py                recognize_all(): the four DFAs over the same tokens
  structuring/                 Stage 4
    candidate_profile.tx       textX grammar of the candidate-profile DSL
    dsl.py                     Metamodel, semantic checks, parse functions
    builder.py                 Stages 1-3 results -> DSL text
  visualization/               Stage 5
    template.html              Page skeleton and CSS (from outputVisualization.html)
    html.py                    Validated model -> HTML page
examples/
  enid_sinclair.txt            Sample résumé accepted as DevOps and Data Engineer
  wednesday_addams.txt         Sample résumé
  wednesday_addams.rlp         DSL generated from it
  wednesday_addams.html        HTML rendered from it
  wednesday_addams_full.rlp    Hand-written DSL with the sample page's data
  wednesday_addams_full.html   HTML rendered from it
outputVisualization.html       Sample page provided with the assignment
run_pipeline.py                Runs stages 1-5 on a résumé and saves each result
pyproject.toml                 Installation configuration
tests/
  test_cli.py
  test_extraction.py
  test_normalization.py
  test_normalization_preview.py
  test_stage1_dataset.py
  test_structuring.py
  test_visualization.py
  fixtures/stage1_extraction_dataset.json
docs/
  stage-1-extraction.md
  stage-2-normalization.md
  stage-3-recognition.md
  stage-4-structuring.md
  stage-5-visualization.md
```
