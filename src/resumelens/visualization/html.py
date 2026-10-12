"""Stage 5: HTML visualization of a validated candidate-profile model.

The renderer only reads the textX model returned by Stage 4, so whatever it
shows has already passed the grammar and the semantic checks. Every value
written by the candidate is HTML-escaped.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from string import Template

from ..structuring.builder import build_candidate_profile
from ..structuring.dsl import parse_candidate_profile

TEMPLATE = Template(Path(__file__).with_name("template.html").read_text(encoding="utf-8"))

PROFILE_TITLES = {
    "FULL_STACK_DEVELOPER": "Full Stack Developer",
    "MACHINE_LEARNING_ENGINEER": "Machine Learning Engineer",
    "DEVOPS_ENGINEER": "DevOps Engineer",
    "DATA_ENGINEER": "Data Engineer",
}
SKILL_TITLES = {
    "languages": "Programming languages",
    "frameworks": "Frameworks and libraries",
    "databases": "Databases",
    "tools": "Tools and technologies",
    "qualifications": "Other qualifications",
}
CONTACT_TITLES = {
    "EmailEntry": "Email",
    "PhoneEntry": "Phone",
    "linkedin": "LinkedIn",
    "github": "GitHub",
    "website": "Website",
}


def _duration(duration) -> str:
    return f"{duration.value:g}{'+' if duration.atLeast else ''} {duration.unit}"


def _field(label: str, value: str) -> list[str]:
    return ["<p>", f"    <strong>{label}:</strong>", f"    {value}", "</p>", ""]


def _contact_value(entry) -> str:
    kind = type(entry).__name__
    value = escape(entry.value)
    if kind == "EmailEntry":
        return f'<a href="mailto:{value}">{value}</a>'
    if kind == "PhoneEntry":
        return f'<a href="tel:{escape("".join(entry.value.split()))}">{value}</a>'
    href = entry.value if "://" in entry.value else f"https://{entry.value}"
    return f'<a href="{escape(href)}">{value}</a>'


def _section(comment: str, title: str, body: list[str]) -> list[str]:
    while body and body[-1] == "":
        body.pop()
    return [
        "",
        f"<!-- {comment} -->",
        '<div class="section">',
        f"    <h2>{title}</h2>",
        "",
        *(f"    {line}" if line else "" for line in body),
        "</div>",
    ]


def _personal(model) -> list[str]:
    body = []
    for entry in model.contact.entries if model.contact else []:
        label = CONTACT_TITLES[getattr(entry, "kind", None) or type(entry).__name__]
        body += _field(label, _contact_value(entry))
    if model.personal.location:
        body += _field("Location", escape(model.personal.location))
    if model.personal.role:
        body += _field("Current role", escape(model.personal.role))
    if model.experience and model.experience.total:
        body += _field("Total experience", _duration(model.experience.total))
    return _section("Personal information", "Personal Information", body) if body else []


def _summary(model) -> list[str]:
    if not model.personal.summary:
        return []
    return _section("Professional summary", "Profile Summary",
                    ["<p>", f"    {escape(model.personal.summary)}", "</p>"])


def _education(model) -> list[str]:
    if not model.education:
        return []
    items = []
    for degree in model.education.degrees:
        text = escape(degree.title)
        if degree.institution:
            text += f" · {escape(degree.institution)}"
        items.append(f"    <li>{text}</li>")
    return _section("Education", "Education", ["<ul>", *items, "</ul>"])


def _experience(model) -> list[str]:
    if not model.experience:
        return []
    body = []
    for job in model.experience.jobs:
        if job.title:
            body.append(f"<h3>{escape(job.title)}</h3>")
        metadata = [escape(job.organization)] if job.organization else []
        if job.duration:
            metadata.append(_duration(job.duration))
        if metadata:
            body += ['<p class="metadata">', f"    {' · '.join(metadata)}", "</p>"]
        if job.activities:
            body.append("<ul>")
            body += [f"    <li>{escape(activity)}</li>" for activity in job.activities]
            body.append("</ul>")
        body.append("")
    return _section("Experience", "Experience", body)


def _skill_spans(tokens) -> list[str]:
    return [
        '<div class="skills">',
        *(f'    <span class="skill">{token}</span>' for token in tokens),
        "</div>",
    ]


def _skills(model) -> list[str]:
    if not model.skills.groups:
        body = ["<p>No qualification from the catalog was recognized.</p>"]
    else:
        body = []
        for group in model.skills.groups:
            body += [
                '<div class="skill-group">',
                f'    <p class="metadata"><strong>{SKILL_TITLES[group.category]}</strong></p>',
                *(f"    {line}" for line in _skill_spans(group.tokens)),
                "</div>",
            ]
    return _section("Skills after FST normalization", "Normalized Technical Skills", body)


def _evaluation(model) -> list[str]:
    body = []
    for accepted in model.classification.accepted:
        title = PROFILE_TITLES[accepted.profile]
        body += [
            '<div class="evaluation">',
            "",
            *(f"    {line}" if line else "" for line in _field("Profile evaluated", title)),
            *(
                f"    {line}" if line else ""
                for line in _field("Qualification pattern",
                                   '<span class="accepted">ACCEPTED</span>')
            ),
            "    <p>",
            "        The normalized qualifications satisfy an accepted",
            f"        {title} pattern.",
            "    </p>",
            "",
            '    <p class="metadata"><strong>Accepted sequence:</strong></p>',
            *(f"    {line}" for line in _skill_spans(accepted.sequence)),
            "",
            "</div>",
        ]
    if not body:
        body = [
            '<div class="evaluation">',
            "    <p>",
            "        <strong>Qualification pattern:</strong>",
            '        <span class="accepted">NO ACCEPTED PROFILE</span>',
            "    </p>",
            "    <p>",
            "        The normalized qualifications do not satisfy the pattern of",
            "        any of the four supported profiles.",
            "    </p>",
            "</div>",
        ]
    return _section("Result produced by the finite automata",
                    "Qualification Evaluation", body)


def render_html(model) -> str:
    """Render a validated Stage 4 model as a standalone HTML page."""
    lines = [
        *_personal(model),
        *_summary(model),
        *_education(model),
        *_experience(model),
        *_skills(model),
        *_evaluation(model),
    ]
    name = escape(model.personal.name)
    return TEMPLATE.substitute(
        title=name,
        name=name,
        sections="\n".join(f"    {line}" if line else "" for line in lines) + "\n",
    )


def render_html_from_dsl(source: str) -> str:
    """Validate DSL text and render it; raise ``TextXError`` if invalid."""
    return render_html(parse_candidate_profile(source))


def render_html_from_resume(text: str) -> str:
    """Run Stages 1-4 on résumé text and render the resulting profile."""
    return render_html_from_dsl(build_candidate_profile(text))
