"""Offline installer contract tests. Run: python3 -m unittest discover -s adapters/codex -p 'test_*.py'"""
from pathlib import Path
from unittest import mock
import json
import os
import tempfile
import tomllib
import unittest

import install as adapter
from install import BEGIN, END, MANIFEST, expected_files, install


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
            instructions = data["developer_instructions"]
            self.assertIn(f".devkit/agents/{role}.md", instructions)
            self.assertIn("Before doing any task work, read", instructions)
            self.assertIn("report BLOCKED", instructions)
            self.assertNotIn("## Rules", instructions)
        self.assertTrue((self.repo / ".devkit/agents/orchestrator.md").is_file())
        self.assertIn("NO_CHANGE_NEEDED", (self.repo / ".devkit/workflows/fix-bug.md").read_text())
        self.assertIn("COMPLETED / FINDINGS", (self.repo / ".devkit/workflows/investigate.md").read_text())
        self.assertIn("COMPLETED / IMPLEMENTED", (self.repo / ".devkit/workflows/implement-feature.md").read_text())
        self.assertIn("COMPLETED / REVIEWED", (self.repo / ".devkit/workflows/review-change.md").read_text())
        self.assertIn("COMPLETED / REFACTORED", (self.repo / ".devkit/workflows/refactor.md").read_text())
        self.assertIn("COMPLETED / MAINTAINED", (self.repo / ".devkit/workflows/maintenance.md").read_text())
        self.assertIn(BEGIN, (self.repo / "AGENTS.md").read_text())

    def test_role_markdown_is_canonical_after_install(self):
        """A role edit must not leave old role text embedded in Codex TOML."""
        install(self.repo, check=False)
        role_path = self.repo / ".devkit/agents/developer.md"
        toml_path = self.repo / ".codex/agents/devkit_developer.toml"
        before = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        original_role = role_path.read_text(encoding="utf-8")
        self.assertNotIn(original_role, before["developer_instructions"])
        role_path.write_text(original_role + "\nNew role rule after install.\n", encoding="utf-8")
        after = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        self.assertEqual(before, after)
        self.assertIn(".devkit/agents/developer.md", after["developer_instructions"])
        self.assertNotIn("New role rule after install.", after["developer_instructions"])

    def test_catalog_matches_installed_workflows(self):
        catalog = (Path(__file__).resolve().parents[2] / "workflows/README.md").read_text(encoding="utf-8")
        installed = {path.name for path in expected_files() if path.parts[:2] == (".devkit", "workflows")}
        for line in catalog.splitlines():
            if not line.startswith("| `"):
                continue
            cols = [part.strip() for part in line.strip("|").split("|")]
            filename = cols[0].strip("`")
            status = cols[-1]
            if status == "Planned":
                self.assertNotIn(filename, installed)
            else:
                self.assertIn(filename, installed)

    def test_fix_bug_agent_results_and_failure_outcome(self):
        root = Path(__file__).resolve().parents[2] / "workflows"
        en = (root / "fix-bug.md").read_text(encoding="utf-8")
        vi = (root / "fix-bug.vi.md").read_text(encoding="utf-8")
        tester_section = en.split("### Check an existing fix — Tester", 1)[1].split("## 4.", 1)[0]
        self.assertIn("Report `ALREADY_FIXED_VERIFIED`", tester_section)
        self.assertIn("Orchestrator then decides", tester_section)
        self.assertIn("report `DEFECT_PRESENT`", tester_section)
        self.assertIn("report `INCONCLUSIVE`", tester_section)
        self.assertNotIn("Report `COMPLETED / ALREADY_FIXED`", tester_section)
        for text in (en, vi):
            self.assertIn("| `BLOCKED / CHECKS_FAILED` |", text)
            self.assertIn("`ALREADY_FIXED_VERIFIED`", text)

    def test_tester_can_accept_script_output_but_reports_sensitive_changes(self):
        tester = (Path(__file__).resolve().parents[2] / "agents/tester.md").read_text(encoding="utf-8")
        self.assertIn("Do not manually edit tracked code", tester)
        self.assertIn("Allowed test or build scripts may create or change files", tester)
        self.assertIn("Tell Orchestrator if script output affects security settings", tester)
        self.assertIn("Never include sensitive values in your report", tester)

    def test_no_workflow_fallback_asks_user_for_guidance(self):
        root = Path(__file__).resolve().parents[2]
        orchestrator = (root / "agents/orchestrator.md").read_text(encoding="utf-8")
        catalog = (root / "workflows/README.md").read_text(encoding="utf-8")
        for text in (orchestrator, catalog):
            self.assertIn("UNSUPPORTED_WORKFLOW", text)
            self.assertIn("ask", text.lower())
            self.assertIn("suggest a workflow or the next step", text)
            self.assertNotIn("short task-local plan", text)
            self.assertNotIn("use a short plan only", text)

    def test_install_manifest_matches_installed_files(self):
        install(self.repo, check=False)
        manifest = json.loads((self.repo / MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(len(manifest["files"]), 14)
        for relative, checksum in manifest["files"].items():
            self.assertEqual(adapter.digest((self.repo / relative).read_bytes()), checksum)

    def test_update_replaces_only_unedited_managed_files(self):
        (self.repo / "AGENTS.md").write_text("# Existing rules\n", encoding="utf-8")
        install(self.repo, check=False)
        files = expected_files()
        relative = Path(".devkit/workflows/investigate.md")
        files[relative] += "\nA new workflow step.\n"
        with mock.patch("install.expected_files", return_value=files):
            install(self.repo, check=True, update=True)
            self.assertNotIn("A new workflow step", (self.repo / relative).read_text())
            install(self.repo, check=False, update=True)
            self.assertIn("A new workflow step", (self.repo / relative).read_text())
        self.assertTrue((self.repo / "AGENTS.md").read_text().startswith("# Existing rules\n"))
        self.assertEqual(adapter.digest((self.repo / relative).read_bytes()), json.loads((self.repo / MANIFEST).read_text())["files"][str(relative)])

    def test_update_rejects_local_edits_and_keeps_all_files(self):
        install(self.repo, check=False)
        path = self.repo / ".devkit/agents/developer.md"
        path.write_text(path.read_text() + "\nLocal change.\n")
        before = {f: f.read_bytes() for f in self.repo.rglob("*") if f.is_file()}
        with self.assertRaisesRegex(ValueError, "Managed file changed"):
            install(self.repo, check=False, update=True)
        for f, data in before.items():
            self.assertEqual(f.read_bytes(), data)

    def test_legacy_install_without_manifest_cannot_overwrite(self):
        install(self.repo, check=False)
        (self.repo / MANIFEST).unlink()
        files = expected_files()
        files[Path(".devkit/agents/developer.md")] += "\nNew upstream instructions.\n"
        with mock.patch("install.expected_files", return_value=files):
            with self.assertRaisesRegex(ValueError, "Conflict"):
                install(self.repo, check=False, update=True)
        self.assertFalse((self.repo / MANIFEST).exists())

    def test_mid_install_write_failure_rolls_back(self):
        original_replace = os.replace
        calls = 0
        def fail_once(src, dst):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("simulated disk write failure")
            return original_replace(src, dst)
        with mock.patch("install.os.replace", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "simulated"):
                install(self.repo, check=False)
        self.assertEqual([".git"], sorted(p.name for p in self.repo.iterdir()))

    def test_mid_update_write_failure_rolls_back(self):
        install(self.repo, check=False)
        before = {f: f.read_bytes() for f in self.repo.rglob("*") if f.is_file()}
        files = expected_files()
        files[Path(".devkit/agents/developer.md")] += "\nNew instructions.\n"
        files[Path(".devkit/workflows/investigate.md")] += "\nNew workflow.\n"
        original_replace = os.replace
        calls = 0
        def fail_once(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated update failure")
            return original_replace(src, dst)
        with mock.patch("install.expected_files", return_value=files):
            with mock.patch("install.os.replace", side_effect=fail_once):
                with self.assertRaisesRegex(OSError, "simulated"):
                    install(self.repo, check=False, update=True)
        for f, data in before.items():
            self.assertEqual(f.read_bytes(), data)
        self.assertEqual(set(before), {f for f in self.repo.rglob("*") if f.is_file()})

    def test_update_keeps_existing_file_permissions(self):
        install(self.repo, check=False)
        path = self.repo / ".devkit/agents/developer.md"
        path.chmod(0o640)
        files = expected_files()
        files[Path(".devkit/agents/developer.md")] += "\nNew upstream role instruction.\n"
        with mock.patch("install.expected_files", return_value=files):
            install(self.repo, check=False, update=True)
        self.assertEqual(path.stat().st_mode & 0o777, 0o640)

    def test_manifest_symlink_is_rejected(self):
        other = Path(self.tmp.name) / "other.json"
        other.write_text("{}")
        (self.repo / ".devkit").mkdir()
        (self.repo / MANIFEST).symlink_to(other)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            install(self.repo, check=False)

    def test_review_workflow_allows_only_safe_temporary_checkout(self):
        workflow = (Path(__file__).resolve().parents[2] / "workflows/review-change.md").read_text()
        self.assertIn("temporary checkout or detached worktree", workflow)
        self.assertIn("Do not switch the user's current branch", workflow)
        self.assertIn("Do not edit code", workflow)

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
