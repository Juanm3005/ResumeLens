"""Data-driven regression tests from the stage-one extraction dataset."""

import json
import unittest
from pathlib import Path

from resumelens import extract_resume


DATASET_PATH = Path(__file__).parent / "fixtures" / "stage1_extraction_dataset.json"
with DATASET_PATH.open(encoding="utf-8") as dataset_file:
    DATASET = json.load(dataset_file)

SKILL_CATEGORIES = (
    "programming_languages",
    "frameworks_libraries",
    "databases",
    "tools_and_technologies",
)
OTHER_QUALIFICATION_CATEGORIES = (
    "software_development",
    "machine_learning",
    "data_processing",
)
CONTACT_CATEGORIES = ("emails", "phones", "linkedin", "github", "websites")


class StageOneDatasetTests(unittest.TestCase):
    def test_dataset_has_at_least_twenty_cases_and_unique_ids(self):
        case_ids = [case["id"] for case in DATASET]
        self.assertGreaterEqual(len(DATASET), 20)
        self.assertEqual(len(case_ids), len(set(case_ids)))


def _dataset_test(case):
    def test_case(self):
        result = extract_resume(case["text"])
        expected_skills = case.get("skills", {})
        expected_contacts = case.get("contacts", {})

        for category in SKILL_CATEGORIES:
            actual = [match.value for match in result.skills[category]]
            self.assertEqual(
                actual,
                expected_skills.get(category, []),
                f"{case['id']}: unexpected {category}",
            )
        for category in OTHER_QUALIFICATION_CATEGORIES:
            actual = [match.value for match in result.other_qualifications[category]]
            self.assertEqual(
                actual,
                case.get("other_qualifications", {}).get(category, []),
                f"{case['id']}: unexpected other qualification {category}",
            )
        for category in CONTACT_CATEGORIES:
            actual = [match.value for match in result.contacts[category]]
            self.assertEqual(
                actual,
                expected_contacts.get(category, []),
                f"{case['id']}: unexpected contact field {category}",
            )
        self.assertEqual(
            [match.value for match in result.academic_degrees],
            case.get("degrees", []),
            f"{case['id']}: unexpected academic degrees",
        )
        self.assertEqual(
            [match.value for match in result.experience],
            case.get("experience", []),
            f"{case['id']}: unexpected experience",
        )
        self.assertEqual(
            [match.value for match in result.experience_sections],
            case.get("experience_sections", []),
            f"{case['id']}: unexpected experience sections",
        )

        # Every reported span must point to the exact raw substring in the input.
        for section in (
            result.contacts,
            result.skills,
            result.other_qualifications,
        ):
            for matches in section.values():
                for match in matches:
                    self.assertEqual(
                        case["text"][match.start : match.end],
                        match.value,
                        f"{case['id']}: invalid source offsets for {match.value!r}",
                    )
        for match in [
            *result.academic_degrees,
            *result.experience,
            *result.experience_sections,
        ]:
            self.assertEqual(
                case["text"][match.start : match.end],
                match.value,
                f"{case['id']}: invalid source offsets for {match.value!r}",
            )

    test_case.__name__ = f"test_case_{case['id']}"
    test_case.__doc__ = f"Stage-one extraction case: {case['id']}"
    return test_case


for _case in DATASET:
    setattr(StageOneDatasetTests, f"test_case_{_case['id']}", _dataset_test(_case))


if __name__ == "__main__":
    unittest.main()
