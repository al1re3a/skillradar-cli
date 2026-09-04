import tempfile
import unittest
from pathlib import Path

from skillradar.index import discover, parse_skill, search


class IndexTests(unittest.TestCase):
    def make_skill(self, root: Path, folder: str, name: str, description: str):
        path = root / folder
        path.mkdir()
        (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {description}\n---\n# {name}\n\n## Workflow\n", encoding="utf-8")

    def test_parses_frontmatter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_skill(root, "pdf", "PDF Expert", "Read and render PDF documents")
            skill = parse_skill(root / "pdf" / "SKILL.md")
            self.assertEqual(skill.name, "PDF Expert")
            self.assertIn("Workflow", skill.headings)

    def test_discovers_nested_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_skill(root, "one", "One", "First skill")
            self.make_skill(root, "two", "Two", "Second skill")
            self.assertEqual(len(discover([root])), 2)

    def test_bm25_ranks_relevant_skill_first(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_skill(root, "pdf", "PDF Expert", "Read render and inspect PDF forms")
            self.make_skill(root, "slides", "Slide Maker", "Create presentation decks")
            results = search(discover([root]), "inspect a pdf form")
            self.assertEqual(results[0][0].name, "PDF Expert")

    def test_empty_query_has_no_results(self):
        self.assertEqual(search([], ""), [])


if __name__ == "__main__":
    unittest.main()
