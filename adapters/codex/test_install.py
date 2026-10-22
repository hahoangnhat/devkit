"""Offline installer contract tests. Run: python3 -m unittest discover -s adapters/codex -p 'test_*.py'"""
from pathlib import Path
import tempfile
import tomllib
import unittest

from install import BEGIN, END, expected_files, install


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "project"
        self.repo.mkdir()
        (self.repo / ".git").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_install_agents_and_workflow(self):
        install(self.repo, check=False)
        for role in ("tester", "developer", "reviewer"):
            data = tomllib.loads((self.repo / ".codex/agents" / f"devkit_{role}.toml").read_text())
            self.assertEqual(data["name"], f"devkit_{role}")
            self.assertIn("STATUS", data["developer_instructions"])
        self.assertTrue((self.repo / ".devkit/agents/orchestrator.md").is_file())
        self.assertIn("NO_CHANGE_NEEDED", (self.repo / ".devkit/workflows/fix-bug.md").read_text())
        self.assertIn(BEGIN, (self.repo / "AGENTS.md").read_text())

    def test_repeat_is_idempotent(self):
        install(self.repo, check=False)
        before = {p: (self.repo / p).read_bytes() for p in expected_files() | {Path("AGENTS.md"): ""}}
        install(self.repo, check=False)
        for name, contents in before.items():
            self.assertEqual(contents, (self.repo / name).read_bytes())
        self.assertEqual(1, (self.repo / "AGENTS.md").read_text().count(BEGIN))
        self.assertEqual(1, (self.repo / "AGENTS.md").read_text().count(END))

    def test_preserves_existing_agents(self):
        (self.repo / "AGENTS.md").write_text("# Existing\n\nDo not deploy.", encoding="utf-8")
        install(self.repo, check=False)
        result = (self.repo / "AGENTS.md").read_text()
        self.assertTrue(result.startswith("# Existing\n\nDo not deploy.\n"))
        self.assertIn(BEGIN, result)

    def test_conflict_preflight_prevents_partial_install(self):
        dest = self.repo / ".codex/agents/devkit_tester.toml"
        dest.parent.mkdir(parents=True)
        dest.write_text("existing user config")
        with self.assertRaisesRegex(ValueError, "Conflict"):
            install(self.repo, check=False)
        self.assertEqual("existing user config", dest.read_text())
        self.assertFalse((self.repo / ".devkit").exists())
        self.assertFalse((self.repo / "AGENTS.md").exists())

    def test_dry_run_leaves_repo_unchanged(self):
        install(self.repo, check=True)
        self.assertEqual([".git"], sorted(p.name for p in self.repo.iterdir()))

    def test_modified_managed_block_fails_safely(self):
        install(self.repo, check=False)
        agents = self.repo / "AGENTS.md"
        modified = agents.read_text().replace("## Devkit (Codex adapter)", "## User-modified Devkit adapter")
        agents.write_text(modified)
        with self.assertRaisesRegex(ValueError, "modified/older"):
            install(self.repo, check=False)
        self.assertEqual(modified, agents.read_text())

    def test_symlink_in_managed_path_rejected(self):
        other = Path(self.tmp.name) / "other"
        other.mkdir()
        (self.repo / ".codex").symlink_to(other, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            install(self.repo, check=False)
        self.assertEqual([], list(other.iterdir()))

    def test_root_override_fails(self):
        (self.repo / "AGENTS.override.md").write_text("override")
        with self.assertRaisesRegex(ValueError, "AGENTS.override.md"):
            install(self.repo, check=False)
        self.assertFalse((self.repo / ".codex").exists())


if __name__ == "__main__":
    unittest.main()
