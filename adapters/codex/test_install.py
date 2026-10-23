"""Offline Codex installer tests. Run: python3 -m unittest discover -s adapters/codex -p 'test_*.py'"""
from pathlib import Path
from unittest import mock
import os
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

    def test_install_agents_and_workflows(self):
        install(self.repo)
        for relative, content in expected_files().items():
            self.assertEqual((self.repo / relative).read_text(encoding="utf-8"), content)
        for role in ("tester", "developer", "reviewer"):
            data = tomllib.loads((self.repo / ".codex/agents" / f"devkit_{role}.toml").read_text())
            self.assertEqual(data["name"], f"devkit_{role}")
            self.assertIn(f".devkit/agents/{role}.md", data["developer_instructions"])
            self.assertIn("Before doing any task work, read", data["developer_instructions"])
        self.assertEqual(1, (self.repo / "AGENTS.md").read_text().count(BEGIN))

    def test_catalog_and_core_instructions(self):
        root = Path(__file__).resolve().parents[2]
        catalog = (root / "workflows/README.md").read_text()
        installed = {p.name for p in expected_files() if p.parts[:2] == (".devkit", "workflows")}
        for line in catalog.splitlines():
            if line.startswith("| `"):
                cols = [c.strip() for c in line.strip("|").split("|")]
                if cols[-1] == "Planned":
                    self.assertNotIn(cols[0].strip("`"), installed)
                else:
                    self.assertIn(cols[0].strip("`"), installed)
        fix_bug = (root / "workflows/fix-bug.md").read_text()
        self.assertIn("ALREADY_FIXED_VERIFIED", fix_bug)
        self.assertIn("BLOCKED / CHECKS_FAILED", fix_bug)
        tester = (root / "agents/tester.md").read_text()
        self.assertIn("Allowed test or build scripts may create or change files", tester)
        self.assertIn("Never include sensitive values in your report", tester)
        for text in ((root / "agents/orchestrator.md").read_text(), catalog):
            self.assertIn("UNSUPPORTED_WORKFLOW", text)
            self.assertIn("suggest a workflow or the next step", text)

    def test_orchestrator_subagent_lifecycle_instructions_installed(self):
        install(self.repo)
        instructions = (self.repo / ".devkit/agents/orchestrator.md").read_text()
        for rule in (
            "Start a fresh subagent for each new task by default",
            "Reuse an open subagent",
            "collect its report and evidence",
            "close_agent",
            "Before the final report",
        ):
            self.assertIn(rule, instructions)

    def test_reinstall_overwrites_custom_devkit_files(self):
        install(self.repo)
        role = self.repo / ".devkit/agents/developer.md"
        toml = self.repo / ".codex/agents/devkit_developer.toml"
        workflow = self.repo / ".devkit/workflows/fix-bug.md"
        for path in (role, toml, workflow):
            path.write_text("custom local contents")
        install(self.repo)
        for relative in (Path(".devkit/agents/developer.md"), Path(".codex/agents/devkit_developer.toml"), Path(".devkit/workflows/fix-bug.md")):
            self.assertEqual((self.repo / relative).read_text(), expected_files()[relative])

    def test_reinstall_replaces_marked_block_only(self):
        path = self.repo / "AGENTS.md"
        path.write_text("# Project instructions\n\nDo not deploy.\n")
        install(self.repo)
        text = path.read_text()
        path.write_text(text.replace("## Devkit (Codex adapter)", "## Changed Devkit instructions") + "\n# More local rules\n")
        install(self.repo)
        result = path.read_text()
        self.assertIn("## Devkit (Codex adapter)", result)
        self.assertNotIn("## Changed Devkit instructions", result)
        self.assertIn("Do not deploy.", result)
        self.assertIn("# More local rules", result)
        self.assertEqual(1, result.count(BEGIN))
        self.assertEqual(1, result.count(END))

    def test_installer_is_idempotent(self):
        install(self.repo)
        names = set(expected_files()) | {Path("AGENTS.md")}
        previous = {p: (self.repo / p).read_bytes() for p in names}
        install(self.repo)
        self.assertEqual(previous, {p: (self.repo / p).read_bytes() for p in names})

    def test_preview_changes_nothing(self):
        install(self.repo, check=True)
        self.assertEqual([".git"], sorted(p.name for p in self.repo.iterdir()))
        install(self.repo)
        role = self.repo / ".devkit/agents/developer.md"
        role.write_text("local modification")
        install(self.repo, check=True)
        self.assertEqual("local modification", role.read_text())

    def test_preview_reports_current_expected_content(self):
        install(self.repo)
        relative = Path(".devkit/agents/developer.md")
        files = expected_files()
        files[relative] += "\nA new instruction.\n"
        with mock.patch("install.expected_files", return_value=files):
            install(self.repo, check=True)
            self.assertNotIn("A new instruction.", (self.repo / relative).read_text())
            install(self.repo)
            self.assertIn("A new instruction.", (self.repo / relative).read_text())

    def test_file_permissions_preserved(self):
        install(self.repo)
        role = self.repo / ".devkit/agents/developer.md"
        role.chmod(0o640)
        role.write_text("modified")
        install(self.repo)
        self.assertEqual(0o640, role.stat().st_mode & 0o777)

    def test_broken_agents_markers_refused_before_changes(self):
        path = self.repo / "AGENTS.md"
        path.write_text(BEGIN + "\nmissing end\n")
        with self.assertRaisesRegex(ValueError, "markers"):
            install(self.repo)
        self.assertFalse((self.repo / ".devkit").exists())

    def test_symlink_in_managed_path_rejected(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.repo / ".codex").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            install(self.repo)
        self.assertEqual([], list(outside.iterdir()))

    def test_directory_collision_refused_before_changes(self):
        path = self.repo / ".codex/agents/devkit_tester.toml"
        path.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "regular file"):
            install(self.repo)
        self.assertFalse((self.repo / "AGENTS.md").exists())

    def test_root_override_rejected(self):
        (self.repo / "AGENTS.override.md").write_text("override")
        with self.assertRaisesRegex(ValueError, "AGENTS.override.md"):
            install(self.repo)

    def test_atomic_write_failure_keeps_old_file(self):
        install(self.repo)
        relative = Path(".devkit/agents/developer.md")
        target = self.repo / relative
        target.write_text("local change")
        files = expected_files()
        with mock.patch("install.os.replace", side_effect=OSError("simulated failure")):
            with self.assertRaisesRegex(OSError, "simulated failure"):
                install(self.repo)
        self.assertEqual("local change", target.read_text())
        self.assertEqual([], list(target.parent.glob(".devkit-*")))

    def test_review_workflow_uses_safe_checkout(self):
        workflow = (Path(__file__).resolve().parents[2] / "workflows/review-change.md").read_text()
        self.assertIn("temporary checkout or detached worktree", workflow)
        self.assertIn("Do not switch the user's current branch", workflow)


if __name__ == "__main__":
    unittest.main()
