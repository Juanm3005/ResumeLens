"""Stage 2 tests: transducers, catalog consistency and profile ordering."""

import json
import unittest
from pathlib import Path

try:
    import pyformlang  # noqa: F401
except ImportError:  # pragma: no cover
    pyformlang = None

FIXTURE = Path(__file__).parent / "fixtures" / "stage1_extraction_dataset.json"


@unittest.skipIf(pyformlang is None, "pyformlang is not installed")
class NormalizationTests(unittest.TestCase):
    def setUp(self):
        from resumelens.normalization import normalize_value

        self.normalize = normalize_value

    def test_reference_examples_from_the_assignment(self):
        cases = {
            "JS": "JAVASCRIPT", "Javascript": "JAVASCRIPT",
            "React.js": "REACT", "ReactJS": "REACT",
            "NodeJS": "NODE_JS", "Node.js": "NODE_JS",
            "Postgres": "POSTGRESQL", "PostgreSQL": "POSTGRESQL",
            "pandas": "PANDAS", "sklearn": "SCIKIT_LEARN",
            "scikit learn": "SCIKIT_LEARN", "Scikit-learn": "SCIKIT_LEARN",
            "Tensor Flow": "TENSORFLOW", "TensorFlow": "TENSORFLOW",
            "Py Torch": "PYTORCH", "PyTorch": "PYTORCH",
        }
        for raw, token in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(self.normalize(raw), token)

    def test_every_catalog_alias_reaches_its_token(self):
        from resumelens.normalization.catalog import CATALOG

        for token, aliases in CATALOG.items():
            for alias in aliases:
                with self.subTest(alias=alias):
                    self.assertEqual(self.normalize(alias), token)

    def test_case_and_whitespace_are_irrelevant(self):
        self.assertEqual(self.normalize("jAvAsCrIpT"), "JAVASCRIPT")
        self.assertEqual(self.normalize("Spring \n  Boot"), "SPRING_BOOT")
        self.assertEqual(self.normalize("Machine-learning model development"),
                         "ML_MODEL_DEVELOPMENT")

    def test_prefix_aliases_do_not_interfere(self):
        self.assertEqual(self.normalize("Java"), "JAVA")
        self.assertEqual(self.normalize("JavaScript"), "JAVASCRIPT")
        self.assertEqual(self.normalize("SQL"), "SQL")
        self.assertEqual(self.normalize("SQLite"), "SQLITE")
        self.assertEqual(self.normalize("SQL Server"), "SQL_SERVER")

    def test_symbols_are_preserved(self):
        self.assertEqual(self.normalize("C++"), "C_PLUS_PLUS")
        self.assertEqual(self.normalize("C#"), "C_SHARP")

    def test_unknown_values_are_rejected_not_passed_through(self):
        for raw in ("Elixir", "Jav", "C", "JavaScript2", ""):
            with self.subTest(raw=raw):
                self.assertIsNone(self.normalize(raw))

    def test_t1_matches_pure_python_cleaning(self):
        from resumelens.normalization.catalog import CATALOG, END, clean_key
        from resumelens.normalization.transducers import (
            build_cleaning_transducer, run_transducer)

        t1 = build_cleaning_transducer()
        for aliases in CATALOG.values():
            for alias in aliases:
                with self.subTest(alias=alias):
                    self.assertEqual(
                        run_transducer(t1, [*alias, END]),
                        [*clean_key(alias), END])


@unittest.skipIf(pyformlang is None, "pyformlang is not installed")
class PipelineTests(unittest.TestCase):
    def test_assignment_example_is_normalized_and_sorted(self):
        from resumelens.normalization import normalize_text

        result = normalize_text("Git, NodeJS, JS, Postgres, React.js",
                                profile="full_stack")
        self.assertEqual(result.ordered_tokens,
                         ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"])
        self.assertEqual(result.unrecognized, [])

    def test_duplicates_collapse_and_order_is_input_independent(self):
        from resumelens.normalization import normalize_text

        a = normalize_text("JS, Javascript, Git", profile="full_stack")
        b = normalize_text("Git, JavaScript, JS", profile="full_stack")
        self.assertEqual(a.ordered_tokens, ["JAVASCRIPT", "GIT"])
        self.assertEqual(a.ordered_tokens, b.ordered_tokens)

    def test_ml_profile_order_and_outside_tokens(self):
        from resumelens.normalization import normalize_text

        result = normalize_text(
            "Git, SQL, TensorFlow, Pandas, Python, Docker", profile="ml_engineer")
        self.assertEqual(result.ordered_tokens,
                         ["PYTHON", "PANDAS", "TENSORFLOW", "SQL", "GIT"])
        self.assertEqual(result.outside_profile, ["DOCKER"])

    def test_unknown_profile_is_rejected(self):
        from resumelens.normalization import normalize_text

        with self.assertRaises(ValueError):
            normalize_text("JS", profile="nope")

    def test_all_stage1_fixture_values_are_recognized(self):
        from resumelens.normalization import normalize_text

        for case in json.loads(FIXTURE.read_text(encoding="utf-8")):
            with self.subTest(case=case["id"]):
                self.assertEqual(normalize_text(case["text"]).unrecognized, [])


class CatalogTests(unittest.TestCase):
    def test_catalog_is_unambiguous_and_has_46_tokens(self):
        from resumelens.normalization.catalog import CATALOG, alias_keys

        self.assertEqual(len(CATALOG), 46)
        alias_keys()  # raises ValueError on ambiguous aliases


if __name__ == "__main__":
    unittest.main()