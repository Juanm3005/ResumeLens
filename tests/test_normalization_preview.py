"""Integration check for the optional, deliberately small Stage 2 preview."""

import importlib.util
import unittest

from resumelens.normalization_preview import normalize_resume_skills


@unittest.skipUnless(
    importlib.util.find_spec("pyformlang"),
    "install the stage2-preview extra to run the Pyformlang FST test",
)
class NormalizationPreviewTests(unittest.TestCase):
    def test_extracted_skill_aliases_flow_through_the_fst(self):
        result = normalize_resume_skills(
            "Skills: JS, Javascript, JavaScript, Python, React.js."
        )

        self.assertEqual(
            result["programming_languages"],
            ["JAVASCRIPT", "JAVASCRIPT", "JAVASCRIPT", "Python"],
        )
        self.assertEqual(result["frameworks_libraries"], ["React.js"])


if __name__ == "__main__":
    unittest.main()
