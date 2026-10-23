#!/usr/bin/env python3
"""Install a minimal, project-scoped Codex adapter for Devkit (stdlib only)."""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path
import sys
import tempfile
import tomllib

DEVKIT_ROOT = Path(__file__).resolve().parents[2]
ROLE_FILES = ("orchestrator", "tester", "developer", "reviewer")
SUBAGENTS = ("tester", "developer", "reviewer")
WORKFLOW_FILES = ("README.md", "fix-bug.md", "investigate.md", "implement-feature.md", "review-change.md", "refactor.md", "maintenance.md")
SKILL_NAMES = ("setup-verification",)
BEGIN = "<!-- devkit:codex:start -->"
END = "<!-- devkit:codex:end -->"


def toml_str(value: str) -> str:
    # TOML multiline literal strings preserve Markdown and avoid escaping quotes.
    if "'''" in value:
        raise ValueError("Role instructions contain a TOML triple-quote delimiter")
    return "'''\n" + value.rstrip("\n") + "\n'''"


def role_toml(role: str) -> str:
    # The installed Markdown is the single source of truth. Do not copy its
    # content into TOML: users may change the Markdown after installation.
    role_path = f".devkit/agents/{role}.md"
    instructions = (
        f"You are Devkit {role.capitalize()}, a specialist, not the workflow Orchestrator. "
        f"Before doing any task work, read `{role_path}` in full from the "
        "root of the assigned repository workspace. If no workspace was "
        "assigned, use the current project root. Follow that file as your "
        "role instructions for this task, including its limits and report "
        "format. Do not use an older copy of its content. If you cannot "
        "find or read the file, report BLOCKED and do not proceed.\n\n"
        "Follow your parent Orchestrator's task brief and the selected Devkit "
        "workflow. Report your stage result, not the final task result. "
        "Do not start other agents unless Orchestrator explicitly asks."
    )
    description = {
        "tester": "Devkit Tester: reproduce defects and independently verify observed behavior without editing source code.",
        "developer": "Devkit Developer: investigate and implement the smallest authorized code change; report evidence for independent review.",
        "reviewer": "Devkit Reviewer: independently review the latest diff and evidence; report concrete findings without editing code.",
    }[role]
    data = (
        "# Read the role from " + role_path + " at task start (do not embed a copy).\n"
        + f'name = "devkit_{role}"\n'
        + f'description = "{description}"\n'
        + "developer_instructions = " + toml_str(instructions) + "\n"
    )
    parsed = tomllib.loads(data)
    assert all(parsed.get(k) for k in ("name", "description", "developer_instructions"))
    return data


AGENTS_SECTION = """<!-- devkit:codex:start -->
## Devkit (Codex adapter)

When the user explicitly asks to use Devkit for engineering work, the **main Codex session** acts as the Devkit Orchestrator:

1. Read `.devkit/agents/orchestrator.md` in full. Read `.devkit/workflows/README.md` to route the request, then read only the chosen existing workflow in full. Choose by the user's goal, not by keywords. Paths referenced as `agents/...` and `workflows/...` inside Devkit instructions are rooted at `.devkit/`.
2. Follow repository instructions and the actual Codex permission/sandbox policy. Do not assume Devkit can override them. Do not edit application code as Orchestrator.
3. Delegate required specialist stages using **actual Codex subagents**: `devkit_tester`, `devkit_developer`, and `devkit_reviewer`, registered in `.codex/agents/`. Give each a self-contained brief with scope, acceptance, verification, prohibited actions, relevant evidence, and the applicable workflow path.
4. Follow the chosen workflow for agent order, scope approval, checks, and stop rules. Use evidence for every completion claim.
5. For a verified change, give `devkit_developer` a final `PUBLISH` task with `CO_AUTHOR: Codex <noreply@openai.com>`. Developer uses Git to commit and push its task branch, and GitHub CLI (`gh pr create --base develop --head <task-branch>`) to open a PR, or `gh pr view` to identify an existing one. Include the approved diff, verification results and risks. Do not publish changes from read-only workflows or make empty commits. Follow actual tool access, authentication and repository permissions; never merge automatically.
6. Collect subagent outputs and independently decide the task disposition. If delegation or a required check is unavailable, say `BLOCKED` rather than imitating a subagent or claiming tests passed. Never invent a PR, approval, commit, or successful test.

These instructions apply to explicit Devkit requests; ordinary project work retains its existing behavior. Specialist TOMLs point to the role Markdown files in `.devkit/agents/`. Read those files at task start; do not rely on an old copy.
<!-- devkit:codex:end -->"""


def expected_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for role in ROLE_FILES:
        files[Path(".devkit/agents") / f"{role}.md"] = (DEVKIT_ROOT / "agents" / f"{role}.md").read_text(encoding="utf-8")
    for name in WORKFLOW_FILES:
        files[Path(".devkit/workflows") / name] = (DEVKIT_ROOT / "workflows" / name).read_text(encoding="utf-8")
    for name in SKILL_NAMES:
        files[Path(".agents/skills") / name / "SKILL.md"] = (DEVKIT_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    for role in SUBAGENTS:
        files[Path(".codex/agents") / f"devkit_{role}.toml"] = role_toml(role)
    return files


def merge_agents(existing: str) -> str:
    """Replace only the marked Devkit block; keep other AGENTS.md content."""
    starts, ends = existing.count(BEGIN), existing.count(END)
    if starts or ends:
        if starts != 1 or ends != 1 or existing.index(BEGIN) >= existing.index(END):
            raise ValueError("AGENTS.md has missing or duplicate Devkit markers")
        before, rest = existing.split(BEGIN, 1)
        _, after = rest.split(END, 1)
        return before + AGENTS_SECTION + after
    if existing and not existing.endswith("\n"):
        existing += "\n"
    return existing + ("\n" if existing else "") + AGENTS_SECTION + "\n"


def check_path(repo: Path, relative: Path) -> Path:
    """Never follow symlinks or overwrite a directory."""
    dest = repo
    for part in relative.parts:
        dest /= part
        if dest.is_symlink():
            raise ValueError(f"Symlink in Devkit path: {dest}")
    if dest.exists() and not dest.is_file():
        raise ValueError(f"Not a regular file: {dest}")
    return dest


def write_file(dest: Path, content: bytes) -> None:
    """Replace one file atomically (not an all-files transaction)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    original_mode = stat.S_IMODE(dest.stat().st_mode) if dest.exists() else None
    fd, name = tempfile.mkstemp(prefix=".devkit-", dir=dest.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(content)
        if original_mode is not None:
            temp.chmod(original_mode)
        else:
            temp.chmod(0o644)
        os.replace(temp, dest)
    finally:
        temp.unlink(missing_ok=True)


def install(repo: Path, check: bool = False) -> None:
    repo = repo.expanduser().resolve()
    if not repo.is_dir() or not (repo / ".git").exists():
        raise ValueError(f"Expected a Git repository root containing .git: {repo}")
    if (repo / "AGENTS.override.md").exists():
        raise ValueError("AGENTS.override.md hides AGENTS.md; integrate Devkit manually")

    wanted = expected_files()
    agents_file = check_path(repo, Path("AGENTS.md"))
    existing = agents_file.read_text(encoding="utf-8") if agents_file.exists() else ""
    wanted[Path("AGENTS.md")] = merge_agents(existing)

    changes = []
    for relative, text in wanted.items():
        dest = check_path(repo, relative)
        content = text.encode("utf-8")
        if not dest.exists() or dest.read_bytes() != content:
            changes.append((dest, content))

    if check:
        print(f"Devkit install preview for {repo}:")
        for dest, _ in changes:
            print("  Write: " + str(dest.relative_to(repo)))
        if not changes:
            print("  Already up to date")
        return

    for dest, content in changes:
        write_file(dest, content)
    print(f"Devkit installed in {repo} ({len(changes)} files written).")
    print("Commit the Devkit files to develop before creating task worktrees.")
    print("Start a new Codex session and prompt: Use Devkit to <describe your task>.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path, help="Target Git repository root")
    parser.add_argument("--check", action="store_true", help="Preview writes without changing files")
    args = parser.parse_args()
    try:
        install(args.repository, check=args.check)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
