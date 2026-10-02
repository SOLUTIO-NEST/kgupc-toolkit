import json
import tempfile
import unittest
from pathlib import Path

from kgupc_toolkit.statements import example_files, prepare_statements, render_fragment, sample_layout


class StatementTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / "problems"
        self.problem = self.directory / "A"
        self.sections = self.problem / "statement-sections/korean"
        self.sections.mkdir(parents=True)
        for name, text in (("name", "Title \\& test"), ("legend", "Story"),
                           ("input", "Input"), ("output", "Output")):
            (self.sections / f"{name}.tex").write_text(text, encoding="utf-8")
        self.info = {"language": "korean", "timeLimit": 1500, "memoryLimit": 256}

    def example(self, index, input_text="1\n", output_text="2\n"):
        first = self.sections / f"example.{index:02d}"
        second = first.with_name(first.name + ".a")
        first.write_text(input_text, encoding="utf-8")
        second.write_text(output_text, encoding="utf-8")
        return first, second

    def test_numeric_order_and_missing_answer(self):
        self.example(10)
        first, second = self.example(2)
        self.assertEqual(example_files(self.sections)[0], (first, second))
        second.unlink()
        with self.assertRaisesRegex(ValueError, "needs both"):
            example_files(self.sections)

    def test_optional_sections_and_solution_visibility(self):
        (self.sections / "notes.tex").write_text("% empty notes\n", encoding="utf-8")
        (self.sections / "tutorial.tex").write_text("SECRET-SOLUTION", encoding="utf-8")
        fragment = render_fragment("A", self.sections, self.info)
        self.assertIn(r"\problemlimits{1.5}{256}", fragment)
        self.assertNotIn("ExplanationSection", fragment)
        self.assertNotIn("tutorial", fragment)
        (self.sections / "notes.tex").write_text("Explanation", encoding="utf-8")
        self.assertIn("ExplanationSection", render_fragment("A", self.sections, self.info))

    def test_long_samples_use_breakable_full_width(self):
        first, second = self.example(1, "x\n" * 40)
        self.assertEqual(sample_layout("auto", first, second), "stacked")
        self.assertIn("SampleFileStack", render_fragment("A", self.sections, self.info))

    def test_parts_are_validated_before_generated_files_change(self):
        wrapper = self.problem / "statement.tex"
        wrapper.write_text(r"\polygonstatement{A}{statement-sections/korean}", encoding="utf-8")
        (self.problem / "statement.json").write_text(json.dumps(self.info), encoding="utf-8")
        prepare_statements(self.directory, [("A", wrapper.name)])
        generated = self.directory / "build/statements/A.tex"
        previous = generated.read_bytes()
        (self.sections / "output.tex").unlink()
        with self.assertRaisesRegex(ValueError, "Missing statement section"):
            prepare_statements(self.directory, [("A", wrapper.name)])
        self.assertEqual(generated.read_bytes(), previous)

    def test_escaping_statement_directory_is_rejected(self):
        (self.problem / "statement.tex").write_text(r"\polygonstatement{A}{../..}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Invalid statement directory"):
            prepare_statements(self.directory, [("A", "statement.tex")])

    def test_literal_sample_files_remain_unchanged(self):
        data = "1  2\nliteral_#%{}\\\n"
        first, _ = self.example(1, data)
        fragment = render_fragment("A", self.sections, self.info)
        self.assertIn("SampleFilePair", fragment)
        self.assertEqual(first.read_text(encoding="utf-8"), data)
