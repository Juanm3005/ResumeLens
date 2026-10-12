# Stage 4 — Candidate profile language with a context-free grammar and textX

This stage defines a domain-specific language (DSL) that represents, in a structured and verifiable way, everything ResumeLens knows about a candidate after stages 1–3: personal information, contact data, education, experience, normalized skills, and **every profile the candidate was accepted for**. The grammar is context-free, written for `textX`, and lives in [`src/resumelens/structuring/candidate_profile.tx`](../src/resumelens/structuring/candidate_profile.tx).

## Scope

- **Input:** résumé text. The builder runs stage 1 (extraction), stage 2 (normalization), and stage 3 (the four DFAs) and renders the results as a DSL document.
- **Output:** a DSL document (`.rlp`, *ResumeLens Profile*) that has been parsed and validated by the textX metamodel, plus the Python object model textX builds from it.
- **Validation:** any DSL document—generated or hand-written—can be validated. Documents that break the lexical, syntactic, or semantic rules are rejected with the line and column of the error.
- **Out of scope:** the HTML/Markdown visualization (stage 5) consumes the validated model; it is not part of this stage.

## Modules

| Module | Function | Input | Output |
| --- | --- | --- | --- |
| `structuring/candidate_profile.tx` | textX grammar (CFG) | — | — |
| `structuring/dsl.py` | `candidate_metamodel()` | — | textX metamodel with semantic checks (cached) |
| | `parse_candidate_profile(source)` | DSL text | model object, or `TextXSyntaxError` / `TextXSemanticError` |
| | `parse_candidate_profile_file(path)` | path to a `.rlp` file | same as above |
| `structuring/builder.py` | `build_candidate_profile(text)` | résumé text | validated DSL text |
| `recognition/__init__.py` | `recognize_all(tokens)` | canonical tokens | the four stage 3 results |

Command line:

```powershell
python -m resumelens .\resume.txt --dsl -o .\profile.rlp   # generate (and validate)
python -m resumelens .\profile.rlp --validate              # validate an existing document
```

`--validate` exits with code `0` for a valid document and `1` (with the error on stderr) for an invalid one.

## Example

The résumé [`examples/wednesday_addams.txt`](../examples/wednesday_addams.txt) produces [`examples/wednesday_addams.rlp`](../examples/wednesday_addams.rlp). It satisfies two profiles, so the classification block lists both:

```text
candidate {
    personal {
        name: "Wednesday Addams";
    }
    contact {
        email: wednesday.addams@example.com;
        phone: +57 300 123 4567;
        github: https://github.com/wednesday-addams;
    }
    education {
        degree: "Bachelor of Science";
    }
    experience {
        total: 3 years;
        job {
            activity: "Developed web applications for organizing investigation notes.";
            activity: "Implemented backend services using Node.js and REST APIs.";
            activity: "Built data-processing pipelines in Python with Pandas on AWS.";
        }
    }
    skills {
        languages: PYTHON, JAVASCRIPT, SQL;
        frameworks: NODE_JS, PANDAS, REACT;
        databases: POSTGRESQL;
        tools: REST_API, AWS, GIT;
        qualifications: WEB_APPLICATIONS, DATA_PROCESSING_PIPELINE, BACKEND_SERVICES;
    }
    classification {
        accepted FULL_STACK_DEVELOPER {
            sequence: JAVASCRIPT, REACT, NODE_JS, REST_API, POSTGRESQL, GIT;
        }
        accepted DATA_ENGINEER {
            sequence: PYTHON, SQL, PANDAS, POSTGRESQL, DATA_PROCESSING_PIPELINE, AWS, GIT;
        }
    }
}
```

When no profile accepts the résumé, the block is `classification { none; }`.

## Grammar in EBNF

Notation: `'x'` is a literal terminal, `?` optional, `*` zero or more, `+` one or more, `|` alternative, `( )` grouping. Terminals defined by regular expressions are written in `UPPER_CASE`.

```ebnf
CandidateProfile = 'candidate' '{'
                       PersonalInfo
                       ContactInfo?
                       Education?
                       Experience?
                       Skills
                       Classification
                   '}' ;

PersonalInfo     = 'personal' '{'
                       'name' ':' STRING ';'
                       ( 'location' ':' STRING ';' )?
                       ( 'role' ':' STRING ';' )?
                       ( 'summary' ':' STRING ';' )?
                   '}' ;

ContactInfo      = 'contact' '{' ContactEntry+ '}' ;
ContactEntry     = EmailEntry | PhoneEntry | LinkEntry ;
EmailEntry       = 'email' ':' EMAIL ';' ;
PhoneEntry       = 'phone' ':' PHONE ';' ;
LinkEntry        = LinkKind ':' URL ';' ;
LinkKind         = 'linkedin' | 'github' | 'website' ;

Education        = 'education' '{' Degree+ '}' ;
Degree           = 'degree' ':' STRING ( 'at' STRING )? ';' ;

Experience       = 'experience' '{'
                       ( 'total' ':' Duration ';' )?
                       Job+
                   '}' ;
Job              = 'job' '{'
                       ( 'title' ':' STRING ';' )?
                       ( 'organization' ':' STRING ';' )?
                       ( 'duration' ':' Duration ';' )?
                       ( 'activity' ':' STRING ';' )*
                   '}' ;
Duration         = NUMBER '+'? DURATION_UNIT ;

Skills           = 'skills' '{' SkillGroup* '}' ;
SkillGroup       = SkillCategory ':' TokenList ';' ;
SkillCategory    = 'languages' | 'frameworks' | 'databases' | 'tools'
                 | 'qualifications' ;
TokenList        = TOKEN ( ',' TOKEN )* ;

Classification   = 'classification' '{' ( AcceptedProfile+ | 'none' ';' ) '}' ;
AcceptedProfile  = 'accepted' ProfileName '{' 'sequence' ':' TokenList ';' '}' ;
ProfileName      = 'FULL_STACK_DEVELOPER' | 'MACHINE_LEARNING_ENGINEER'
                 | 'DEVOPS_ENGINEER' | 'DATA_ENGINEER' ;
```

Lexical terminals:

```ebnf
TOKEN         = /[A-Z][A-Z0-9]*(_[A-Z0-9]+)*/ ;
EMAIL         = /[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}/ ;
PHONE         = /\+?[0-9][0-9() .-]{5,}[0-9]/ ;
URL           = /(?:https?:\/\/|www\.)[^\s;]+/ ;
DURATION_UNIT = /(?:years?|months?)\b/ ;
STRING        = '"' ( any character except '"' and '\' | '\' any character )* '"' ;   (textX built-in)
NUMBER        = integer or decimal number ;                                          (textX built-in)
COMMENT       = '//' … end of line | '/*' … '*/' ;                                   (ignored)
```

Whitespace and comments may appear between any two terminals and are discarded.

### Non-terminals

`CandidateProfile` (start symbol), `PersonalInfo`, `ContactInfo`, `ContactEntry`, `EmailEntry`, `PhoneEntry`, `LinkEntry`, `LinkKind`, `Education`, `Degree`, `Experience`, `Job`, `Duration`, `Skills`, `SkillGroup`, `SkillCategory`, `TokenList`, `Classification`, `AcceptedProfile`, `ProfileName`.

### Terminals

- **Keywords:** `candidate`, `personal`, `name`, `location`, `role`, `summary`, `contact`, `email`, `phone`, `linkedin`, `github`, `website`, `education`, `degree`, `at`, `experience`, `total`, `job`, `title`, `organization`, `duration`, `activity`, `skills`, `languages`, `frameworks`, `databases`, `tools`, `qualifications`, `classification`, `accepted`, `sequence`, `none`, and the four profile names.
- **Punctuation:** `{`, `}`, `:`, `;`, `,`, `+`.
- **Lexical classes (regular expressions):** `TOKEN`, `EMAIL`, `PHONE`, `URL`, `DURATION_UNIT`, `STRING`, `NUMBER`.

The textX metamodel is created with `autokwd=True`, so keywords only match whole words (`jobs` is not read as `job` followed by `s`).

## Structural characteristics

1. **Block structure.** Every section is a keyword followed by a `{ … }` block, and blocks nest (`experience` → `job`, `classification` → `accepted`). Balanced, nested braces are the classic construct that a regular language cannot describe but a context-free grammar can, which is why this stage uses a CFG instead of another regular expression.
2. **Fixed section order.** `personal → contact → education → experience → skills → classification`. A fixed order keeps the grammar unambiguous and LL-parsable: each section is chosen by its first keyword.
3. **Mandatory and optional sections.** `personal`, `skills`, and `classification` are mandatory—every profile has a name (or `"Unknown candidate"`), a (possibly empty) skill set, and a classification result. `contact`, `education`, and `experience` are optional because a résumé may not contain them, but when present they must have at least one entry.
4. **Repeated elements.** Contact entries, degrees, jobs, activities within a job, skill groups, tokens within a group, and accepted profiles are all repeatable (`+`/`*`), as the assignment requires for multiple experiences, education records, and skills.
5. **Several accepted profiles.** `Classification` is either one or more `AcceptedProfile` blocks or the explicit marker `none`. Each accepted block carries the canonical word (`sequence`) that its DFA accepted, so the document keeps the evidence for the verdict.
6. **Two kinds of values.** Free text written by the candidate (names, activities, degree titles) is always a quoted `STRING`. Data with a known shape (emails, phones, URLs, canonical tokens, durations) is unquoted and must match its lexical class, so malformed data is rejected by the lexer instead of being accepted as arbitrary text.
7. **Alignment with previous stages.** `TOKEN` is the alphabet of stage 2/3 (`JAVASCRIPT`, `NODE_JS`, …); `ProfileName` uses the same names as `ProfileSpec.name`.

## Validation

Validation happens in three layers. The first two are the grammar; the third is implemented in `dsl.py` as textX object/model processors, because it needs information a context-free grammar cannot express (a closed vocabulary, uniqueness across the document, and agreement with an automaton).

| Layer | Rule | Example rejected input | Error |
| --- | --- | --- | --- |
| Lexical | Tokens are upper-case identifiers | `languages: javascript;` | `TextXSyntaxError: Expected Token` |
| Lexical | Email/URL/phone/duration shapes | `email: alex.example.com;`, `total: 2 decades;` | `TextXSyntaxError` |
| Lexical | Free text must be quoted | `name: Alex Doe;` | `TextXSyntaxError` |
| Syntactic | Missing `;`, `{`, `}` or mandatory field | `name: "Alex Doe"` (no `;`) | `TextXSyntaxError` |
| Syntactic | Section order | `education` after `skills` | `TextXSyntaxError` |
| Syntactic | Non-empty blocks | `contact { }`, `classification { }` | `TextXSyntaxError` |
| Syntactic | Known profile names | `accepted WEB_DEVELOPER { … }` | `TextXSyntaxError` |
| Semantic | Tokens belong to the stage 2 catalog | `tools: JQUERY;` | `unknown qualification token 'JQUERY'` |
| Semantic | No repeated skill, category, contact or accepted profile | `tools: GIT, REACT;` when `REACT` is already declared | `skill 'REACT' declared twice` |
| Semantic | Durations are positive | `duration: 0 years;` | `duration must be greater than zero` |
| Semantic | An accepted sequence only uses declared skills | `sequence: …, VUE, …` without `VUE` in `skills` | `… not declared in skills: VUE` |
| Semantic | The sequence is accepted by the profile's DFA, in canonical order, with no tokens outside the profile | `accepted DEVOPS_ENGINEER { sequence: PYTHON, AWS, GIT; }` | `sequence is not accepted by the DEVOPS_ENGINEER automaton (…)` |

The last rule ties the DSL to stage 3: `dsl.py` re-runs the corresponding `pyformlang` automaton over the declared sequence, so a document cannot claim a profile that the automaton rejects.

## How the builder fills the document

| DSL element | Source |
| --- | --- |
| `personal.name` | First non-empty line of the résumé, if it is two to five capitalized words; otherwise `"Unknown candidate"`. |
| `contact` | Stage 1 `contacts` (emails, phones, LinkedIn/GitHub/other URLs), deduplicated. |
| `education` | Stage 1 `academic_degrees`, deduplicated. |
| `experience.job` | One job per stage 1 experience section; its lines (without bullets) become `activity` entries and a duration found inside the section becomes `duration`. Without sections, each line with an experience duration becomes a job. |
| `experience.total` | The first experience duration written outside the experience sections. |
| `skills` | Stage 2 tokens grouped by the stage 1 category they came from (`skills.programming_languages` → `languages`, …, `other_qualifications.*` → `qualifications`), in order of appearance. |
| `classification` | Every stage 3 result with verdict `ACCEPTED`, with its canonical sequence; `none` if there is none. |

`location`, `role`, `summary`, `title`, `organization`, and `at "<institution>"` are part of the language but are not produced by the builder yet, because stage 1 does not extract them. They can be written by hand and are validated like everything else.

The builder always parses the document it produces before returning it, so its output is valid by construction.

## Tests

[`tests/test_structuring.py`](../tests/test_structuring.py) covers:

- a hand-written document using every construct, checking the resulting object model;
- omission of optional sections and the `none` classification;
- documents with several accepted profiles;
- lexical, syntactic, and semantic rejections (one sub-test per rule in the table above);
- the builder on the two reference résumés of the assignment (Full Stack and ML Engineer), a résumé accepted by two profiles, a résumé accepted by none, contact/education/experience sections, and escaping of quotes;
- that `examples/wednesday_addams.rlp` is exactly what the builder generates;
- the `--dsl` and `--validate` command-line options.

## Limitations

- The candidate's name is a heuristic over the first line; résumés that start with a heading get `"Unknown candidate"`.
- Experience sections are not split into individual jobs: each section becomes one job.
- Free-text values are collapsed to a single line (newlines and repeated spaces become one space).
- Only accepted profiles are represented; rejected profiles are not listed in the document.
