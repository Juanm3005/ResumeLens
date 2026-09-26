import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from resumelens.cli import main


class CommandLineTests(unittest.TestCase):
    def test_writes_json_to_standard_output(self):
        with tempfile.TemporaryDirectory() as directory:
            resume = Path(directory, "resume.txt")
            resume.write_text("Skills: Python, Git.", encoding="utf-8")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                exit_code = main([str(resume)])

        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(
            [item["value"] for item in payload["skills"]["programming_languages"]],
            ["Python"],
        )

    def test_writes_json_file_when_output_is_given(self):
        with tempfile.TemporaryDirectory() as directory:
            resume = Path(directory, "resume.txt")
            output = Path(directory, "result.json")
            resume.write_text("Email: alex@example.com", encoding="utf-8")

            exit_code = main([str(resume), "--output", str(output)])

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(
            [item["value"] for item in payload["contacts"]["emails"]],
            ["alex@example.com"],
        )


if __name__ == "__main__":
    unittest.main()
