"""Stage 4 tests: candidate-profile DSL generation and validation with textX."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

try:
    import textx  # noqa: F401
except ImportError:  # pragma: no cover
    textx = None

EXAMPLES = Path(__file__).parent.parent / "examples"

WEDNESDAY = """Wednesday Addams
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git.
"""

MARY_JANE = """Mary Jane Watson
2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git.
"""

VALID = """// minimal hand-written profile
candidate {
    personal {
        name: "Alex Doe";
        role: "Backend developer";
    }
    contact {
        email: alex@example.com;
        phone: +57 300 123 4567;
        linkedin: https://www.linkedin.com/in/alex;
    }
    education {
        degree: "Bachelor of Science" at "Universidad Icesi";
    }
    experience {
        total: 4+ years;
        job {
            title: "Developer";
            organization: "ACME";
            duration: 2.5 years;
            activity: "Built \\"REST\\" services.";
        }
        job {
            activity: "Maintained Linux servers.";
        }
    }
    skills {
        languages: JAVASCRIPT;
        frameworks: REACT, NODE_JS;
        databases: POSTGRESQL;
        tools: GIT;
    }
    classification {
        accepted FULL_STACK_DEVELOPER {
            sequence: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT;
        }
    }
}
"""


@unittest.skipIf(textx is None, "textX is not installed")
class CandidateProfileGrammarTests(unittest.TestCase):
    def setUp(self):
        from textx.exceptions import TextXSemanticError, TextXSyntaxError

        from resumelens.structuring import parse_candidate_profile

        self.parse = parse_candidate_profile
        self.syntax_error = TextXSyntaxError
        self.semantic_error = TextXSemanticError

    def assertRejected(self, source, error, message=None):
        with self.assertRaises(error) as context:
            self.parse(source)
        if message:
            self.assertIn(message, str(context.exception))

    def test_valid_profile_builds_the_model(self):
        model = self.parse(VALID)
        self.assertEqual(model.personal.name, "Alex Doe")
        self.assertEqual(model.personal.role, "Backend developer")
        self.assertEqual(
            [entry.value for entry in model.contact.entries],
            ["alex@example.com", "+57 300 123 4567",
             "https://www.linkedin.com/in/alex"],
        )
        self.assertEqual(model.contact.entries[2].kind, "linkedin")
        self.assertEqual(model.education.degrees[0].institution, "Universidad Icesi")
        self.assertEqual(model.experience.total.value, 4)
        self.assertTrue(model.experience.total.atLeast)
        self.assertEqual(len(model.experience.jobs), 2)
        self.assertEqual(model.experience.jobs[0].duration.value, 2.5)
        self.assertEqual(model.experience.jobs[0].activities,
                         ['Built "REST" services.'])
        self.assertEqual([g.category for g in model.skills.groups],
                         ["languages", "frameworks", "databases", "tools"])
        self.assertEqual(model.classification.accepted[0].profile,
                         "FULL_STACK_DEVELOPER")

    def test_optional_sections_can_be_omitted(self):
        model = self.parse(
            'candidate { personal { name: "A B"; } skills { } '
            "classification { none; } }"
        )
        self.assertIsNone(model.contact)
        self.assertIsNone(model.experience)
        self.assertTrue(model.classification.none)
        self.assertEqual(model.classification.accepted, [])

    def test_several_accepted_profiles(self):
        model = self.parse(
            'candidate { personal { name: "A B"; } skills { '
            "languages: PYTHON, SQL; frameworks: PANDAS, NUMPY, SCIKIT_LEARN; "
            "databases: POSTGRESQL; tools: AWS, GIT; "
            "qualifications: DATA_PROCESSING_PIPELINE; } classification { "
            "accepted MACHINE_LEARNING_ENGINEER { sequence: PYTHON, PANDAS, "
            "NUMPY, SCIKIT_LEARN, SQL, GIT; } "
            "accepted DATA_ENGINEER { sequence: PYTHON, SQL, PANDAS, NUMPY, "
            "POSTGRESQL, DATA_PROCESSING_PIPELINE, AWS, GIT; } } }"
        )
        self.assertEqual(
            [a.profile for a in model.classification.accepted],
            ["MACHINE_LEARNING_ENGINEER", "DATA_ENGINEER"],
        )

    def test_lexical_errors_are_rejected(self):
        cases = {
            "lowercase token": ("languages: JAVASCRIPT;", "languages: javascript;"),
            "bad email": ("alex@example.com", "alex.example.com"),
            "bad url": ("https://www.linkedin.com/in/alex", "linkedin.com/in/alex"),
            "bad unit": ("2.5 years", "2.5 decades"),
            "unquoted name": ('"Alex Doe"', "Alex Doe"),
            "unknown profile": ("FULL_STACK_DEVELOPER", "WEB_DEVELOPER"),
        }
        for label, (old, new) in cases.items():
            with self.subTest(label):
                self.assertRejected(VALID.replace(old, new), self.syntax_error)

    def test_syntax_errors_are_rejected(self):
        cases = {
            "missing semicolon": ('name: "Alex Doe";', 'name: "Alex Doe"'),
            "missing name": ('name: "Alex Doe";', ""),
            "empty contact block": (
                "email: alex@example.com;\n        phone: +57 300 123 4567;\n"
                "        linkedin: https://www.linkedin.com/in/alex;", ""
            ),
            "keyword prefix": ("job {", "jobs {"),
            "empty classification": (
                "accepted FULL_STACK_DEVELOPER {\n            sequence: JAVASCRIPT, "
                "REACT, NODE_JS, POSTGRESQL, GIT;\n        }", ""
            ),
        }
        for label, (old, new) in cases.items():
            with self.subTest(label):
                self.assertIn(old, VALID)
                self.assertRejected(VALID.replace(old, new), self.syntax_error)
        # Sections have a fixed order: education after skills is invalid.
        education = ('    education {\n        degree: "Bachelor of Science" '
                     'at "Universidad Icesi";\n    }\n')
        self.assertIn(education, VALID)
        moved = VALID.replace(education, "").replace(
            "    classification {", education + "    classification {")
        self.assertRejected(moved, self.syntax_error)

    def test_semantic_errors_are_rejected(self):
        cases = {
            "unknown token": ("tools: GIT;", "tools: GIT, JQUERY;",
                              "unknown qualification token 'JQUERY'"),
            "duplicated skill": ("tools: GIT;", "tools: GIT, REACT;",
                                 "skill 'REACT' declared twice"),
            "duplicated category": ("tools: GIT;", "tools: GIT;\n tools: AWS;",
                                    "declared twice"),
            "duplicated contact": ("email: alex@example.com;",
                                   "email: alex@example.com; email: alex@example.com;",
                                   "duplicated contact entry"),
            "zero duration": ("2.5 years", "0 years", "greater than zero"),
            "sequence uses undeclared skill": (
                "frameworks: REACT, NODE_JS;", "frameworks: NODE_JS;",
                "not declared in skills: REACT"),
            "sequence rejected by the automaton": (
                "sequence: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT;",
                "sequence: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL;",
                "not accepted by the FULL_STACK_DEVELOPER automaton"),
            "sequence out of canonical order": (
                "sequence: JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT;",
                "sequence: REACT, JAVASCRIPT, NODE_JS, POSTGRESQL, GIT;",
                "expected canonical order"),
            "wrong profile for the sequence": (
                "accepted FULL_STACK_DEVELOPER", "accepted DEVOPS_ENGINEER",
                "DEVOPS_ENGINEER automaton"),
        }
        for label, (old, new, message) in cases.items():
            with self.subTest(label):
                self.assertIn(old, VALID)
                self.assertRejected(VALID.replace(old, new), self.semantic_error,
                                    message)

    def test_duplicated_accepted_profile_is_rejected(self):
        block = ("accepted FULL_STACK_DEVELOPER {\n            sequence: JAVASCRIPT, "
                 "REACT, NODE_JS, POSTGRESQL, GIT;\n        }")
        self.assertRejected(VALID.replace(block, block + "\n" + block),
                            self.semantic_error, "declared twice")


@unittest.skipIf(textx is None, "textX is not installed")
class CandidateProfileBuilderTests(unittest.TestCase):
    def setUp(self):
        from resumelens.structuring import (
            build_candidate_profile,
            parse_candidate_profile,
        )

        self.build = build_candidate_profile
        self.parse = parse_candidate_profile

    def accepted(self, text):
        model = self.parse(self.build(text))
        return {a.profile: list(a.sequence) for a in model.classification.accepted}

    def test_full_stack_reference_example(self):
        model = self.parse(self.build(WEDNESDAY))
        self.assertEqual(model.personal.name, "Wednesday Addams")
        self.assertEqual(model.experience.total.value, 3)
        self.assertEqual(
            self.accepted(WEDNESDAY),
            {"FULL_STACK_DEVELOPER":
                ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]},
        )

    def test_ml_reference_example(self):
        self.assertEqual(
            self.accepted(MARY_JANE),
            {"MACHINE_LEARNING_ENGINEER":
                ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW",
                 "SQL", "GIT"]},
        )

    def test_resume_accepted_by_several_profiles(self):
        text = (EXAMPLES / "wednesday_addams.txt").read_text(encoding="utf-8")
        self.assertEqual(
            set(self.accepted(text)), {"FULL_STACK_DEVELOPER", "DATA_ENGINEER"}
        )

    def test_example_file_matches_the_generator(self):
        text = (EXAMPLES / "wednesday_addams.txt").read_text(encoding="utf-8")
        expected = (EXAMPLES / "wednesday_addams.rlp").read_text(encoding="utf-8")
        self.assertEqual(self.build(text), expected)

    def test_contacts_education_and_experience_sections(self):
        text = (
            "Alex Doe\nalex@example.com | https://github.com/alex\n"
            "Experience:\n- Built APIs, 2 years of experience.\n"
            "Education:\nMaster's degree\n"
            "Skills: Linux, Docker, AWS, Git.\n"
        )
        model = self.parse(self.build(text))
        self.assertEqual([e.value for e in model.contact.entries],
                         ["alex@example.com", "https://github.com/alex"])
        self.assertEqual(model.contact.entries[1].kind, "github")
        self.assertEqual(model.education.degrees[0].title, "Master's degree")
        job = model.experience.jobs[0]
        self.assertEqual(job.duration.value, 2)
        self.assertEqual(job.activities, ["Built APIs, 2 years of experience."])
        self.assertIsNone(model.experience.total)
        self.assertEqual(self.accepted(text),
                         {"DEVOPS_ENGINEER": ["LINUX", "DOCKER", "AWS", "GIT"]})

    def test_no_accepted_profile(self):
        model = self.parse(self.build("Skills: Ruby"))
        self.assertEqual(model.personal.name, "Unknown candidate")
        self.assertTrue(model.classification.none)

    def test_quotes_in_free_text_are_escaped(self):
        text = 'Experience:\nBuilt the "Clue Board" app.\nSkills:\nGit'
        model = self.parse(self.build(text))
        self.assertEqual(model.experience.jobs[0].activities,
                         ['Built the "Clue Board" app.'])


@unittest.skipIf(textx is None, "textX is not installed")
class CandidateProfileCommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        from resumelens.cli import main

        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_dsl_then_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            resume = Path(directory, "resume.txt")
            profile = Path(directory, "profile.rlp")
            resume.write_text(WEDNESDAY, encoding="utf-8")

            code, _, _ = self.run_cli(str(resume), "--dsl", "-o", str(profile))
            self.assertEqual(code, 0)
            self.assertIn("accepted FULL_STACK_DEVELOPER",
                          profile.read_text(encoding="utf-8"))

            code, out, _ = self.run_cli(str(profile), "--validate")
        self.assertEqual(code, 0)
        self.assertIn("valid candidate profile", out)

    def test_validate_reports_invalid_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory, "bad.rlp")
            profile.write_text("candidate { }", encoding="utf-8")
            code, _, err = self.run_cli(str(profile), "--validate")
        self.assertEqual(code, 1)
        self.assertIn("invalid candidate profile", err)


if __name__ == "__main__":
    unittest.main()
