#!/usr/bin/env python3
"""Install a minimal, project-scoped Codex adapter for Devkit (stdlib only)."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib

DEVKIT_ROOT = Path(__file__).resolve().parents[2]
ROLE_FILES = ("orchestrator", "tester", "developer", "reviewer")
SUBAGENTS = ("tester", "developer", "reviewer")
WORKFLOW_FILES = (
    "README.md",
    "fix-bug.md",
    "investigate.md",
    "implement-feature.md",
    "review-change.md",
    "refactor.md",
    "maintenance.md",
)
VERIFICATION_FILES = (
    "SKILL.md",
    "features/README.md",
    "features/feature.template.md",
    "references/run.schema.json",
)
BEGIN = "<!-- devkit:codex:start -->"
END = "<!-- devkit:codex:end -->"
RUNS_IGNORE_BEGIN = "# devkit:codex:runs-ignore:start"
RUNS_IGNORE_END = "# devkit:codex:runs-ignore:end"
RUNS_IGNORE_SECTION = f"{RUNS_IGNORE_BEGIN}\n/runs/\n{RUNS_IGNORE_END}"


def role_body(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    if content.startswith("---\n"):
        _, marker, body = content.partition("\n---\n")
        if not marker:
            raise ValueError(f"Invalid YAML frontmatter: {path}")
        return body.lstrip("\n").rstrip() + "\n"
    return content


def toml_str(value: str) -> str:
    # TOML multiline literal strings preserve Markdown and avoid escaping quotes.
    if "'''" in value:
        raise ValueError("Role instructions contain a TOML triple-quote delimiter")
    return "'''\n" + value.rstrip("\n") + "\n'''"


def role_toml(role: str) -> str:
    role_path = DEVKIT_ROOT / "agents" / f"{role}.md"
    instructions = (
        f"Codex Devkit subagent: devkit_{role}. You are a specialist, not the "
        "workflow Orchestrator. Follow your parent Orchestrator's bounded brief "
        "and the applicable Devkit workflow. Report stage results, not a final "
        "task-level disposition. Do not spawn further agents without an explicit "
        "delegation from Orchestrator.\n\n"
        + role_body(role_path)
    )
    description = {
        "tester": "Devkit Tester: reproduce defects and independently verify observed behavior without editing source code.",
        "developer": "Devkit Developer: investigate and implement the smallest authorized code change; report evidence for independent review.",
        "reviewer": "Devkit Reviewer: independently review the latest diff and evidence; report concrete findings without editing code.",
    }[role]
    data = (
        "# Generated from devkit/agents/" + role + ".md by Devkit Codex adapter.\n"
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

1. Read `.devkit/agents/orchestrator.md` in full. Read `.devkit/workflows/README.md` to route the request, then read the chosen existing workflow in full (for bug reports: `.devkit/workflows/fix-bug.md`). Paths referenced as `agents/...` and `workflows/...` inside Devkit instructions are rooted at `.devkit/`.
2. Follow repository instructions and the actual Codex permission/sandbox policy. Do not assume Devkit can override them. Do not edit application code as Orchestrator.
3. Delegate required specialist stages using **actual Codex subagents**: `devkit_tester`, `devkit_developer`, and `devkit_reviewer`, registered in `.codex/agents/`. Give each a self-contained brief with scope, acceptance, verification, prohibited actions, relevant evidence, and the applicable workflow path.
4. When behavioral verification is required, read `.agents/skills/devkit-verify/SKILL.md` if installed and use the matching feature document under its `features/` directory. `feature.template.md` is an authoring scaffold, not evidence that a feature was verified.
5. Let Tester assess the expected behavior before asking Developer to change code. Skip unnecessary code edits, Developer, or Reviewer on supported no-change paths as the workflow permits. Use current-artifact evidence for every completion claim.
6. Collect subagent outputs and independently decide the task disposition. If delegation or a required check is unavailable, say `BLOCKED` rather than imitating a subagent or claiming tests passed. Never invent a PR, approval, commit, or successful test.

These instructions apply to explicit Devkit requests; ordinary project work retains its existing behavior. The specialist role TOMLs are generated from the same canonical Devkit Markdown sources.
<!-- devkit:codex:end -->"""


def expected_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for role in ROLE_FILES:
        files[Path(".devkit/agents") / f"{role}.md"] = (DEVKIT_ROOT / "agents" / f"{role}.md").read_text(encoding="utf-8")
    for name in WORKFLOW_FILES:
        files[Path(".devkit/workflows") / name] = (DEVKIT_ROOT / "workflows" / name).read_text(encoding="utf-8")
    verification_root = DEVKIT_ROOT / "adapters/codex/templates/verification"
    install_root = Path(".agents/skills/devkit-verify")
    for name in VERIFICATION_FILES:
        files[install_root / name] = (verification_root / name).read_text(encoding="utf-8")
    for role in SUBAGENTS:
        files[Path(".codex/agents") / f"devkit_{role}.toml"] = role_toml(role)
    return files


def merge_agents(existing: str) -> str:
    starts, ends = existing.count(BEGIN), existing.count(END)
    if starts or ends:
        if starts != 1 or ends != 1 or existing.index(BEGIN) > existing.index(END):
            raise ValueError("AGENTS.md contains incomplete or duplicated Devkit markers")
        current_block = existing[existing.index(BEGIN) : existing.index(END) + len(END)]
        if current_block != AGENTS_SECTION:
            raise ValueError("AGENTS.md has a modified/older Devkit block; refusing to overwrite it")
        return existing
    if existing and not existing.endswith("\n"):
        existing += "\n"
    return existing + ("\n" if existing else "") + AGENTS_SECTION + "\n"


def merge_devkit_gitignore(existing: str) -> str:
    starts, ends = existing.count(RUNS_IGNORE_BEGIN), existing.count(RUNS_IGNORE_END)
    if starts or ends:
        if starts != 1 or ends != 1 or existing.index(RUNS_IGNORE_BEGIN) > existing.index(RUNS_IGNORE_END):
            raise ValueError(".devkit/.gitignore contains incomplete or duplicated Devkit markers")
        current_block = existing[
            existing.index(RUNS_IGNORE_BEGIN) : existing.index(RUNS_IGNORE_END) + len(RUNS_IGNORE_END)
        ]
        if current_block != RUNS_IGNORE_SECTION:
            raise ValueError(".devkit/.gitignore has a modified/older Devkit block; refusing to overwrite it")
        return existing
    if existing and not existing.endswith("\n"):
        existing += "\n"
    return existing + ("\n" if existing else "") + RUNS_IGNORE_SECTION + "\n"


def assert_no_symlinks(root: Path, relative: Path) -> None:
    cur = root
    for part in relative.parts:
        cur /= part
        if cur.is_symlink():
            raise ValueError(f"Symlink in managed path: {cur}")


def install(repo: Path, check: bool) -> None:
    repo = repo.expanduser().resolve()
    if not repo.is_dir() or not (repo / ".git").exists():
        raise ValueError(f"Expected the Git repository root containing .git: {repo}")
    if (repo / "AGENTS.override.md").exists():
        raise ValueError("Repository has AGENTS.override.md: Codex ignores root AGENTS.md; integrate instructions manually")
    wanted = expected_files()
    agents_file = repo / "AGENTS.md"
    assert_no_symlinks(repo, Path("AGENTS.md"))
    try:
        existing_agents = agents_file.read_text(encoding="utf-8") if agents_file.exists() else ""
    except UnicodeDecodeError as exc:
        raise ValueError("AGENTS.md is not UTF-8") from exc
    wanted[Path("AGENTS.md")] = merge_agents(existing_agents)

    devkit_gitignore = repo / ".devkit/.gitignore"
    devkit_gitignore_relative = Path(".devkit/.gitignore")
    assert_no_symlinks(repo, devkit_gitignore_relative)
    if devkit_gitignore.exists() and not devkit_gitignore.is_file():
        raise ValueError(f"Existing path is not a regular file: {devkit_gitignore}")
    try:
        existing_gitignore = devkit_gitignore.read_text(encoding="utf-8") if devkit_gitignore.exists() else ""
    except UnicodeDecodeError as exc:
        raise ValueError(".devkit/.gitignore is not UTF-8") from exc
    wanted[devkit_gitignore_relative] = merge_devkit_gitignore(existing_gitignore)

    # Preflight every target before writing ANY file: never overwrite user files.
    changed: list[tuple[Path, str]] = []
    for relative, content in wanted.items():
        assert_no_symlinks(repo, relative)
        dest = repo / relative
        if dest.exists():
            if not dest.is_file():
                raise ValueError(f"Existing path is not a regular file: {dest}")
            original = dest.read_text(encoding="utf-8")
            if original != content:
                if relative not in (Path("AGENTS.md"), devkit_gitignore_relative):
                    raise ValueError(f"Conflict: {dest}; no files installed. Review/remove the conflicting path manually")
                # These files may receive only their intact managed block;
                # their merge functions preserve all surrounding user content.
                changed.append((dest, content))
        else:
            changed.append((dest, content))
    if not changed:
        print(f"Devkit Codex adapter already installed: {repo}")
        return

    if check:
        print(f"Safe to install into {repo}. Would create/update:")
        for dest, _ in changed:
            print("  " + str(dest.relative_to(repo)))
        return

    for dest, content in changed:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    print(f"Installed Devkit Codex adapter in {repo} ({len(changed)} files).")
    print("Restart Codex in that repo and prompt: Use Devkit to investigate and fix <your bug>.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path, help="Path to target Git repository root")
    parser.add_argument("--check", action="store_true", help="Validate the installation without writing")
    args = parser.parse_args()
    try:
        install(args.repository, args.check)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
