# Stage 1 — Extraction with regular expressions

## Goal and boundaries

This stage finds relevant fragments of a plain-text résumé using Python's `re`. The input domain is literal mentions: qualifications, contact data, education, and experience. It includes a bounded catalog of additional phrases that appear in the reference profiles, such as web application development, predictive models, and data-processing pipelines. No information that is not written is inferred. This stage does not decide whether two mentions are equivalent, does not normalize aliases, and does not recognize any profile.

The output unit is a match `(value, start, end)`. `value` is an exact slice of the source text, and `start`/`end` are Python offsets with an exclusive end. The offsets keep traceability, even when the input contains Unicode characters. For professional experience, both detected duration phrases and the literal content under common work headings are stored; this keeps the job title and its descriptions for the next stages.

## Pattern catalog

All technology, education, and experience patterns run with `re.IGNORECASE`. The content of each match keeps the résumé's original casing.

### Contact

| Field | Expression or rule | Recognized pattern |
| --- | --- | --- |
| Email | `(?<![\w.+-])[\w.!#$%&'*+/=?^_{}|~-]+@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+` | A local part with common characters, `@`, and a domain with at least two dot-separated labels. |
| Phone | `(?<!\w)(?:\+\d{1,3}[ .-]?)?(?:\(?\d{2,4}\)?[ .-])?\d{3,4}[ .-]\d{3,4}(?!\w)` or `(?<!\w)\+?\d{10,15}(?!\w)` | A number with an optional international prefix and separated groups, or a continuous number of 10–15 digits. A later check excludes common dates `YYYY-MM-DD`, `YYYY/MM/DD`, and `YYYY.MM.DD`. |
| URL | `(?i)\b(?:https?://|www\.)[^\s<>()]+` | A URL starting with `http://`, `https://`, or `www.` that continues until a space or delimiter. Trailing sentence punctuation is removed; a host equal to `linkedin.com`/`github.com` or one of their subdomains is classified as such. Similar domains, such as `notlinkedin.com`, remain websites. |

### Qualifications

The regexes are grouped in `SKILL_PATTERNS` in `src/resumelens/extraction/patterns.py`. The alternatives recognize explicit vocabularies and are stored as they appear.

| Category | Regular expression | Example matches |
| --- | --- | --- |
| `programming_languages` | `(?<![\w+#.])(?:JavaScript|Javascript|JS|TypeScript|Java|C\+\+|C#|Python|Ruby|PHP|Kotlin|Swift|Rust|SQL)(?![\w+#])` | `JS`, `Javascript`, `Python`, `SQL`, `C++` |
| `frameworks_libraries` | `(?<![\w.])(?:React(?:\.js|JS)?|Angular|Vue(?:\.js)?|Node(?:\.js|JS)|Django|Spring\s+Boot|Flask|FastAPI|Express(?:\.js)?|Pandas|NumPy|Scikit[- ]learn|scikit\s+learn|sklearn|Tensor\s*Flow|Py\s*Torch)(?!\w|\.(?:js))` | `React.js`, `ReactJS`, `NodeJS`, `scikit learn`, `sklearn`, `Tensor Flow`, `Py Torch` |
| `databases` | `(?<![\w.])(?:PostgreSQL|Postgres|MySQL|SQLite|MongoDB|Redis|Oracle|SQL\s+Server)(?!\w)` | `Postgres`, `PostgreSQL`, `MongoDB`, `SQL Server` |
| `tools_and_technologies` | `(?<![\w.])(?:Git|Docker|Kubernetes|REST(?:ful)?\s+APIs?|AWS|Azure|GCP|Linux)(?!\w)` | `Git`, `Docker`, `REST API`, `RESTful APIs`, `AWS` |

### Other qualifications from the reference profiles

The following bounded regexes detect experience and qualification phrases included in the Full Stack and Machine Learning profiles of the assignment. They are grouped under `other_qualifications` to keep them separate from technology names:

| Group | Regular expression | Examples |
| --- | --- | --- |
| `software_development` | `(?<!\w)(?:web\s+applications?|backend\s+services?)(?!\w)` | `web applications`, `backend services` |
| `machine_learning` | `(?<!\w)(?:machine[- ]learning\s+model\s+development|predictive\s+models?)(?!\w)` | `Machine-learning model development`, `predictive models` |
| `data_processing` | `(?<!\w)data[- ]processing\s+pipelines?(?!\w)` | `data-processing pipelines`, `Data processing pipeline` |

The catalog is limited to explicitly written phrases and can grow by adding patterns and test cases. It does not classify the candidate.

Lookbehind/lookahead boundaries (`(?<!...)`, `(?!...)`) prevent matches inside longer words. Alternatives (`|`) accept several names; `?` makes a part optional; `\s` accepts whitespace. A bounded catalog avoids accepting any arbitrary word as a technology. It can be extended by adding alternatives to the appropriate category and cases to `tests/test_extraction.py`.

### Education

Applied expression:

```regex
(?<!\w)(?:Bachelor(?:'s)?(?:\s+(?:degree|of\s+(?:Science|Arts|Engineering)))?|B\.?\s?Sc\.?|B\.?\s?A\.?|B\.?\s?Eng\.?|Master(?:'s)?(?:\s+(?:degree|of\s+(?:Science|Arts|Engineering)))?|M\.?\s?Sc\.?|M\.?\s?A\.?|M\.?\s?Eng\.?|Ph\.?\s?D\.?|doctorate|associate(?:'s)?(?:\s+degree)?)(?!\w)
```

It recognizes common names and abbreviations for bachelor's, master's, doctoral, and associate degrees, for example `Bachelor of Science`, `M.Sc.`, and `PhD`. It does not extract universities, majors, or dates. The current vocabulary is oriented to mentions in English.

### Professional experience

Two patterns are used to support both orders:

```regex
(?<!\w)\d+(?:\.\d+)?\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?experience(?!\w)
(?<!\w)experience\s*(?:of|:)?\s*\d+(?:\.\d+)?\s*\+?\s*(?:years?|yrs?)(?!\w)
```

They recognize an integer or decimal number of years, with an optional `+`, and the term `year`/`years` or `yr`/`yrs` related to `experience`. For example: `3 years of experience`, `3 yrs professional experience`, and `Experience: 2.5 years`. They do not compute dates or convert months to years.

In addition, to keep the job title and its descriptions, the block under a work heading is captured. The start regex is:

```regex
(?im)^[ \t]*(?:(?:professional|work)[ \t]+)?experience(?:[ \t]+history)?[ \t]*:?[ \t]*(?:\r?\n|$)
```

It recognizes, at the start of a line and case-insensitively, `Experience`, `Work Experience`, `Professional Experience`, and the variant with `History`, optionally followed by a colon. The block ends before the next line that matches the section-heading regex:

```regex
(?im)^[ \t]*(?:education|academic(?:[ \t]+background)?|technical[ \t]+skills|skills|projects?|certifications?|contact(?:[ \t]+information)?|summary|profile|languages?|publications?|awards?|references?|training)[ \t]*:?[ \t]*(?:\r?\n|$)
```

This regex recognizes common headings such as `Education`, `Technical Skills`, `Projects`, and `Certifications`. `re.finditer` finds the start and `re.search` finds the next heading; the content between them is kept as `experience_sections` with offsets into the original text. Headings must be on their own line so the boundaries are unambiguous.

## Output structure

`extract_resume(text)` returns an `ExtractionResult`. `to_dict()`/`to_json()` produce these keys:

- `contacts`: `emails`, `phones`, `linkedin`, `github`, `websites`.
- `skills`: `programming_languages`, `frameworks_libraries`, `databases`, `tools_and_technologies`.
- `other_qualifications`: `software_development`, `machine_learning`, `data_processing`.
- `academic_degrees` and `experience`.
- `experience_sections`, with the text under headings such as `Experience`, `Work Experience`, or `Professional Experience`, up to the next detected common heading.

Each element is an object with `value`, `start`, and `end`. Categories without results are included as empty lists to keep a stable structure.

## Running and verification

Install the package in editable mode from the repository root:

```powershell
python -m pip install -e .
```

The command-line interface reads a UTF-8 `.txt` file and prints JSON; it can also write it with `--output`:

```powershell
python -m resumelens .\resume.txt --output .\extraction.json
python -m unittest discover -s tests -v
```

The tests check qualification examples from the assignment, literal variants, email/phone/URLs, the date filter, degrees, experience, prose qualifications, offsets, JSON, and both CLI destinations. In addition, `tests/fixtures/stage1_extraction_dataset.json` contains **94 regression cases**. Each record includes an identifier, input text, and expected results; omitted keys must be empty. `tests/test_stage1_dataset.py` turns each record into an individual test, validates every category, and checks that each offset recovers the literal fragment.

## Known limitations

- Only UTF-8 plain text is read; there is no text extraction from PDF, DOCX, or images.
- Coverage depends on the pattern vocabulary: a technology that is not included will not be detected.
- Academic degrees and experience expressions recognize English vocabulary; résumés in Spanish need additional patterns.
- Block extraction depends on common section headings in English. A different format may not delimit the block and requires adding recognized headings.
- Phone numbers are detected by shape and are not validated against a national plan. The filter avoids common date formats, but does not guarantee that every remaining number is a phone number.
- Extracted mentions are not evidence of proficiency and are not used to recommend, rank, or discard candidates.
