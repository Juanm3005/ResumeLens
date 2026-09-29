import json
import unittest

from resumelens import extract_resume


def values(matches):
    return [match.value for match in matches]


class ExtractionTests(unittest.TestCase):
    def test_reference_full_stack_fragment_keeps_literal_skill_mentions(self):
        text = (
            "Wednesday Addams\n"
            "3 years of experience developing web applications.\n"
            "Technical Skills: JS, React.js, NodeJS, Postgres, Git."
        )

        result = extract_resume(text)

        self.assertEqual(values(result.skills["programming_languages"]), ["JS"])
        self.assertEqual(
            values(result.skills["frameworks_libraries"]), ["React.js", "NodeJS"]
        )
        self.assertEqual(values(result.skills["databases"]), ["Postgres"])
        self.assertEqual(values(result.skills["tools_and_technologies"]), ["Git"])
        self.assertEqual(values(result.experience), ["3 years of experience"])

    def test_reference_machine_learning_fragment_extracts_skills(self):
        text = (
            "Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git."
        )

        result = extract_resume(text)

        self.assertEqual(
            values(result.skills["programming_languages"]), ["Python", "SQL"]
        )
        self.assertEqual(
            values(result.skills["frameworks_libraries"]),
            ["Pandas", "NumPy", "Scikit-learn", "TensorFlow"],
        )
        self.assertEqual(values(result.skills["databases"]), [])
        self.assertEqual(values(result.skills["tools_and_technologies"]), ["Git"])

    def test_extracts_profile_relevant_qualifications_from_prose(self):
        text = (
            "2 years of experience developing predictive models and "
            "data-processing pipelines. Machine-learning model development."
        )

        result = extract_resume(text)

        self.assertEqual(
            values(result.other_qualifications["machine_learning"]),
            ["predictive models", "Machine-learning model development"],
        )
        self.assertEqual(
            values(result.other_qualifications["data_processing"]),
            ["data-processing pipelines"],
        )
        self.assertEqual(values(result.experience), ["2 years of experience"])

    def test_database_and_library_mentions_are_not_canonicalized(self):
        text = "PostgreSQL; sklearn; scikit learn; Tensor Flow; Py Torch; ReactJS."

        result = extract_resume(text)

        self.assertEqual(values(result.skills["databases"]), ["PostgreSQL"])
        self.assertEqual(
            values(result.skills["frameworks_libraries"]),
            ["sklearn", "scikit learn", "Tensor Flow", "Py Torch", "ReactJS"],
        )

    def test_extracts_contacts_and_skips_date_as_phone(self):
        text = (
            "Email: jane.doe+work@example.org; phone +57 300 123 4567. "
            "LinkedIn: https://www.linkedin.com/in/jane, "
            "GitHub: https://github.com/janedoe. Portfolio: www.janedoe.dev "
            "Graduated 2026-10-11."
        )

        result = extract_resume(text)

        self.assertEqual(values(result.contacts["emails"]), ["jane.doe+work@example.org"])
        self.assertEqual(values(result.contacts["phones"]), ["+57 300 123 4567"])
        self.assertEqual(
            values(result.contacts["linkedin"]),
            ["https://www.linkedin.com/in/jane"],
        )
        self.assertEqual(values(result.contacts["github"]), ["https://github.com/janedoe"])
        self.assertEqual(values(result.contacts["websites"]), ["www.janedoe.dev"])

    def test_extracts_degrees_and_both_experience_word_orders(self):
        text = "B.Sc. Computer Science; Master's degree. Experience: 2.5 years; 3 yrs of professional experience."

        result = extract_resume(text)

        self.assertEqual(values(result.academic_degrees), ["B.Sc.", "Master's degree"])
        self.assertEqual(
            values(result.experience),
            ["Experience: 2.5 years", "3 yrs of professional experience"],
        )

    def test_extracts_raw_experience_section_until_next_resume_heading(self):
        text = (
            "Professional Experience:\n"
            "Senior Software Engineer — Acme Corp (2023–2026)\n"
            "Built APIs with Python.\n\n"
            "Education:\nB.Sc. Computer Science"
        )

        result = extract_resume(text)
        section = result.experience_sections[0]

        self.assertEqual(
            section.value,
            "Senior Software Engineer — Acme Corp (2023–2026)\nBuilt APIs with Python.",
        )
        self.assertEqual(text[section.start : section.end], section.value)
        self.assertEqual(values(result.academic_degrees), ["B.Sc."])

    def test_match_offsets_point_to_exact_source_text(self):
        text = "María has JS and Git."
        result = extract_resume(text)
        skill = result.skills["programming_languages"][0]

        self.assertEqual(text[skill.start : skill.end], "JS")
        self.assertEqual(skill.value, "JS")

    def test_result_is_json_serializable_and_has_stable_empty_categories(self):
        result = extract_resume("No matching information.")
        decoded = json.loads(result.to_json())

        self.assertEqual(decoded["contacts"]["emails"], [])
        self.assertEqual(decoded["skills"]["programming_languages"], [])
        self.assertEqual(
            decoded["other_qualifications"]["machine_learning"], []
        )
        self.assertEqual(decoded["academic_degrees"], [])
        self.assertEqual(decoded["experience"], [])
        self.assertEqual(decoded["experience_sections"], [])

    def test_non_string_input_is_rejected(self):
        with self.assertRaises(TypeError):
            extract_resume(None)


if __name__ == "__main__":
    unittest.main()
