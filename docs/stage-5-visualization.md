# Stage 5 — HTML visualization of the candidate profile

Once a candidate-profile document has been validated by the stage 4 grammar, ResumeLens uses its structured information to generate a short, standalone HTML page. The design follows the sample page provided with the assignment ([`outputVisualization.html`](../outputVisualization.html)): the same card layout, sections, and styles.

## Scope

- **Input:** a textX model of a **validated** candidate profile (stage 4). The page can be produced from a `.rlp` file or directly from résumé text (stages 1–4 run first).
- **Output:** one self-contained HTML file (inline CSS, no scripts, no external resources) that can be opened in any browser.
- **Guarantee:** the renderer never reads the résumé or the DSL text itself; it only walks the model. An invalid document raises a `TextXError` and no HTML is produced.

## Modules

| Module | Function | Input | Output |
| --- | --- | --- | --- |
| `visualization/template.html` | page skeleton and CSS (from `outputVisualization.html`) | — | — |
| `visualization/html.py` | `render_html(model)` | validated textX model | HTML text |
| | `render_html_from_dsl(source)` | DSL text | HTML text, or `TextXError` |
| | `render_html_from_resume(text)` | résumé text | HTML text |

Command line:

```powershell
python -m resumelens .\resume.txt --html                   # résumé → stages 1-4 → visualizations\resume.html
python -m resumelens .\profile.rlp --validate --html      # validated DSL → visualizations\profile.html
python -m resumelens .\resume.txt --html --html-dir .\out  # another folder → out\resume.html
python -m resumelens .\resume.txt --html -o .\page.html    # exact file
```

Generated pages go to the `visualizations/` folder (created if needed, and ignored by git because it holds candidate data), named after the input file; the command prints the path of the written page. `--html-dir` changes the folder and `-o` writes to an exact file instead.

`--html` cannot be combined with `--normalize` or `--dsl`. With `--validate`, an invalid document prints the error on stderr, writes nothing, and exits with code `1`.

## From the model to the page

| Page section | Model data | Shown when |
| --- | --- | --- |
| Header | `personal.name` | always |
| Personal Information | `contact` entries (email, phone, LinkedIn, GitHub, website as links), `personal.location`, `personal.role`, `experience.total` | at least one of them exists |
| Profile Summary | `personal.summary` | it exists |
| Education | `education.degrees` (title · institution) | the section exists |
| Experience | each `job`: `title` (`<h3>`), `organization · duration` (metadata line), `activity` list | the section exists |
| Normalized Technical Skills | `skills.groups`, one labeled row of tokens per category | always (with a message if empty) |
| Qualification Evaluation | one block per `accepted` profile: profile name, `ACCEPTED`, and its accepted sequence | always; with `none`, a single block saying no profile was accepted |

Profile names are displayed with their readable titles (`FULL_STACK_DEVELOPER` → *Full Stack Developer*, `DEVOPS_ENGINEER` → *DevOps Engineer*, …).

## Design decisions

1. **Template plus generated sections.** The page skeleton and the CSS live in `template.html` (a `string.Template` with `$title`, `$name`, and `$sections`). The sections are generated in Python because their number depends on the model (several jobs, several accepted profiles). The CSS only adds a few rules to the original: spacing between evaluation blocks and skill groups, and a narrow-screen rule.
2. **Empty sections are omitted** instead of showing empty headings, so a résumé with little information still produces a clean page.
3. **Every candidate value is escaped** with `html.escape`, including attribute values (`href`). A résumé containing `<script>` is shown as text, never executed.
4. **Links.** Emails become `mailto:` links, phones `tel:` links (without spaces), and URLs starting with `www.` get an `https://` prefix in the `href`.

## Examples

| DSL document | Generated page | Content |
| --- | --- | --- |
| [`examples/wednesday_addams.rlp`](../examples/wednesday_addams.rlp) | [`examples/wednesday_addams.html`](../examples/wednesday_addams.html) | Generated from [`wednesday_addams.txt`](../examples/wednesday_addams.txt); accepted by Full Stack Developer **and** Data Engineer, so the page shows two evaluation blocks. |
| [`examples/wednesday_addams_full.rlp`](../examples/wednesday_addams_full.rlp) | [`examples/wednesday_addams_full.html`](../examples/wednesday_addams_full.html) | Hand-written with the data of the assignment's sample page (location, role, summary, job title, organization); reproduces `outputVisualization.html`. |

## Tests

[`tests/test_visualization.py`](../tests/test_visualization.py) checks that:

- the full example shows every section and value of the assignment's sample page;
- there is one evaluation block per accepted profile;
- the example HTML files are exactly what the renderer produces;
- empty sections are omitted and the `none` classification is shown;
- candidate text and URLs are escaped;
- an invalid DSL document is not rendered;
- `--html` works from a résumé and, with `--validate`, from a DSL file, rejects invalid documents, and cannot be combined with `--dsl`.

## Limitations

- Fields that stage 1 does not extract yet (location, role, summary, job title, organization, institution) only appear when they are written in the DSL by hand.
- Only accepted profiles are shown, because the DSL only records accepted profiles.
- The output is HTML only; there is no Markdown renderer.
