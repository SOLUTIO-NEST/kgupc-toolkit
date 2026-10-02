"""Validate source routing and fail early on invalid contest registrations."""

import tempfile
import unittest
from pathlib import Path

from kgupc_toolkit import build


class BuildConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.problems = self.root / "2025" / "problems"
        self.problems.mkdir(parents=True)
        (self.problems / "main.tex").write_text("", encoding="utf-8")
        for letter in ("A", "B"):
            (self.problems / letter).mkdir()
            (self.problems / letter / "statement.tex").write_text("", encoding="utf-8")

    def manifest(self, content):
        (self.problems / "problem-list.tex").write_text(content, encoding="utf-8")

    def test_problem_child_directory_and_workshop_extensionless_path_route_to_main(self):
        for source in (self.problems, self.problems / "main",
                       self.problems / "A" / "statement.tex"):
            with self.subTest(source=source):
                self.assertEqual(build.find_main(source), self.problems / "main.tex")

    def test_editorial_child_routes_to_editorial(self):
        solutions = self.root / "2025" / "solutions"
        (solutions / "A").mkdir(parents=True)
        (solutions / "main.tex").write_text("", encoding="utf-8")
        child = solutions / "A" / "solution.tex"
        child.write_text("", encoding="utf-8")
        self.assertEqual(build.find_main(child), solutions / "main.tex")

    def test_missing_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Source does not exist"):
            build.find_main(self.problems / "missing.tex")

    def test_manifest_preserves_contest_order_and_ignores_comments(self):
        self.manifest("% Contest order\n\\includeproblem{B}{statement.tex} % B first\n"
                      "\\includeproblem{A}{statement.tex}\n")
        self.assertEqual(build.read_problems(self.problems),
                         [("B", "statement.tex"), ("A", "statement.tex")])

    def test_duplicate_letter_is_rejected(self):
        self.manifest("\\includeproblem{A}{statement.tex}\n" * 2)
        with self.assertRaisesRegex(ValueError, "Duplicate problem letter"):
            build.read_problems(self.problems)

    def test_missing_or_escaping_statement_is_rejected(self):
        for filename in ("missing.tex", "../B/statement.tex"):
            with self.subTest(filename=filename):
                self.manifest(f"\\includeproblem{{A}}{{{filename}}}\n")
                with self.assertRaisesRegex(ValueError, "Missing or invalid statement"):
                    build.read_problems(self.problems)

    def test_invalid_manifest_reports_line_number(self):
        self.manifest("% comment\n\\import{A}{statement.tex}\n")
        with self.assertRaisesRegex(ValueError, r"problem-list\.tex:2:"):
            build.read_problems(self.problems)

    def test_empty_contest_is_rejected(self):
        self.manifest("% No registered problems\n")
        with self.assertRaisesRegex(ValueError, "No problems registered"):
            build.read_problems(self.problems)


if __name__ == "__main__":
    unittest.main()
