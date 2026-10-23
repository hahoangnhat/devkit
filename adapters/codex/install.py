#!/usr/bin/env python3
"""Install a minimal, project-scoped Codex adapter for Devkit (stdlib only)."""

from __future__ import annotations

import argparse
import hashlib
import json
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
BEGIN = "<!-- devkit:codex:start -->"
END = "<!-- devkit:codex:end -->"
MANIFEST = Path(".devkit/codex-install.json")


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
5. Collect subagent outputs and independently decide the task disposition. If delegation or a required check is unavailable, say `BLOCKED` rather than imitating a subagent or claiming tests passed. Never invent a PR, approval, commit, or successful test.

These instructions apply to explicit Devkit requests; ordinary project work retains its existing behavior. Specialist TOMLs point to the role Markdown files in `.devkit/agents/`. Read those files at task start; do not rely on an old copy.
<!-- devkit:codex:end -->"""


def expected_files() -> dict[Path, str]:
    files: dict[Path, str] = {}
    for role in ROLE_FILES:
        files[Path(".devkit/agents") / f"{role}.md"] = (DEVKIT_ROOT / "agents" / f"{role}.md").read_text(encoding="utf-8")
    for name in WORKFLOW_FILES:
        files[Path(".devkit/workflows") / name] = (DEVKIT_ROOT / "workflows" / name).read_text(encoding="utf-8")
    for role in SUBAGENTS:
        files[Path(".codex/agents") / f"devkit_{role}.toml"] = role_toml(role)
    return files


def digest(content: bytes | str) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def read_manifest(repo: Path) -> dict | None:
    path = repo / MANIFEST
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f"Not a regular file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid Devkit install manifest: {path}") from exc
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("files"), dict):
        raise ValueError(f"Unsupported Devkit install manifest: {path}")
    hashes = data["files"]
    if not isinstance(data.get("agents_block"), str) or any(
        not isinstance(name, str) or not isinstance(value, str)
        or len(value) != 64 or not all(c in "0123456789abcdef" for c in value)
        or Path(name).is_absolute() or ".." in Path(name).parts
        or not (name.startswith(".devkit/") or name.startswith(".codex/agents/"))
        for name, value in hashes.items()
    ):
        raise ValueError("Invalid managed-file hashes in Devkit install manifest")
    if len(data["agents_block"]) != 64 or not all(c in "0123456789abcdef" for c in data["agents_block"]):
        raise ValueError("Invalid AGENTS.md hash in Devkit install manifest")
    return data


def merge_agents(existing: str, previous_hash: str | None = None, update: bool = False) -> str:
    starts, ends = existing.count(BEGIN), existing.count(END)
    if starts or ends:
        if starts != 1 or ends != 1 or existing.index(BEGIN) > existing.index(END):
            raise ValueError("AGENTS.md contains incomplete or duplicated Devkit markers")
        begin = existing.index(BEGIN)
        end = existing.index(END) + len(END)
        current_block = existing[begin:end]
        if current_block != AGENTS_SECTION:
            if not (update and previous_hash and digest(current_block) == previous_hash):
                raise ValueError("AGENTS.md has a modified/older Devkit block; refusing to overwrite it")
            return existing[:begin] + AGENTS_SECTION + existing[end:]
        return existing
    if previous_hash:
        raise ValueError("AGENTS.md Devkit block was removed; refusing to restore it silently")
    if existing and not existing.endswith("\n"):
        existing += "\n"
    return existing + ("\n" if existing else "") + AGENTS_SECTION + "\n"


def assert_no_symlinks(root: Path, relative: Path) -> None:
    cur = root
    for part in relative.parts:
        cur /= part
        if cur.is_symlink():
            raise ValueError(f"Symlink in managed path: {cur}")


def apply_changes(repo: Path, changes: list[tuple[Path, bytes, bytes | None]]) -> None:
    """Stage files first, then replace atomically per file; undo completed writes on error."""
    staged: dict[Path, Path] = {}
    completed: list[tuple[Path, bytes | None]] = []
    created_dirs: set[Path] = set()
    modes = {dest: stat.S_IMODE(dest.stat().st_mode) if dest.exists() else None for dest, _, _ in changes}
    current_umask = os.umask(0)
    os.umask(current_umask)
    new_mode = 0o666 & ~current_umask

    def stage(dest: Path, data: bytes, mode: int | None = None) -> Path:
        fd, name = tempfile.mkstemp(prefix=f".{dest.name}.devkit-", dir=dest.parent)
        path = Path(name)
        try:
            with os.fdopen(fd, "wb") as f:
                os.fchmod(f.fileno(), new_mode if mode is None else mode)
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            return path
        except BaseException:
            path.unlink(missing_ok=True)
            raise

    try:
        for dest, content, _ in changes:
            missing = []
            parent = dest.parent
            while parent != repo and not parent.exists():
                missing.append(parent)
                parent = parent.parent
            assert_no_symlinks(repo, dest.relative_to(repo))
            dest.parent.mkdir(parents=True, exist_ok=True)
            created_dirs.update(missing)
            staged[dest] = stage(dest, content, modes[dest])

        for dest, _, old in changes:
            # Do not overwrite changes made between preflight and commit.
            current = dest.read_bytes() if dest.exists() else None
            if current != old:
                raise ValueError(f"File changed during install: {dest}")
            os.replace(staged[dest], dest)
            del staged[dest]
            completed.append((dest, old))
    except BaseException as error:
        rollback_errors = []
        for dest, old in reversed(completed):
            try:
                if old is None:
                    dest.unlink()
                else:
                    restore = stage(dest, old, modes[dest])
                    try:
                        os.replace(restore, dest)
                    finally:
                        restore.unlink(missing_ok=True)
            except OSError as exc:
                rollback_errors.append(f"{dest}: {exc}")
        if rollback_errors:
            raise OSError("Install failed; manual recovery required for: " + "; ".join(rollback_errors)) from error
        raise
    finally:
        for temp in staged.values():
            temp.unlink(missing_ok=True)
        for path in sorted(created_dirs, key=lambda x: len(x.parts), reverse=True):
            try:
                path.rmdir()
            except OSError:
                pass


def install(repo: Path, check: bool = False, update: bool = False) -> None:
    repo = repo.expanduser().resolve()
    if not repo.is_dir() or not (repo / ".git").exists():
        raise ValueError(f"Expected the Git repository root containing .git: {repo}")
    if (repo / "AGENTS.override.md").exists():
        raise ValueError("Repository has AGENTS.override.md: Codex ignores root AGENTS.md; integrate instructions manually")

    assert_no_symlinks(repo, MANIFEST)
    manifest = read_manifest(repo)
    wanted = expected_files()
    old_files = manifest["files"] if manifest else {}
    for old_name, old_hash in old_files.items():
        relative = Path(old_name)
        assert_no_symlinks(repo, relative)
        dest = repo / relative
        if not dest.is_file() or digest(dest.read_bytes()) != old_hash:
            raise ValueError(f"Managed file changed since installation: {dest}; refusing to overwrite")
        if relative not in wanted:
            raise ValueError(f"Old managed file is no longer in Devkit: {dest}; update manually")

    agents_file = repo / "AGENTS.md"
    assert_no_symlinks(repo, Path("AGENTS.md"))
    try:
        existing_agents = agents_file.read_text(encoding="utf-8") if agents_file.exists() else ""
    except UnicodeDecodeError as exc:
        raise ValueError("AGENTS.md is not UTF-8") from exc
    wanted[Path("AGENTS.md")] = merge_agents(
        existing_agents, manifest["agents_block"] if manifest else None, update=update
    )

    # A manifest records the last installed content, not a user's later edits.
    recorded = {
        "version": 1,
        "files": {str(path): digest(content) for path, content in wanted.items() if path != Path("AGENTS.md")},
        "agents_block": digest(AGENTS_SECTION),
    }
    wanted[MANIFEST] = json.dumps(recorded, indent=2, sort_keys=True) + "\n"

    changes: list[tuple[Path, bytes, bytes | None]] = []
    for relative, content in wanted.items():
        assert_no_symlinks(repo, relative)
        dest = repo / relative
        if dest.exists() and not dest.is_file():
            raise ValueError(f"Existing path is not a regular file: {dest}")
        old = dest.read_bytes() if dest.exists() else None
        new = content.encode("utf-8")
        if old == new:
            continue
        if old is not None:
            if relative == Path("AGENTS.md"):
                pass  # Only the exact managed block may change; merge_agents checked it.
            elif relative == MANIFEST:
                if manifest is None or not update:
                    raise ValueError(f"Install manifest differs: {dest}; use --update")
            elif not (update and str(relative) in old_files):
                raise ValueError(f"Conflict: {dest}; no files installed. Use --update for unchanged Devkit files")
        changes.append((dest, new, old))

    if not changes:
        print(f"Devkit Codex adapter already installed: {repo}")
        return
    if check:
        print(f"Safe to {'update' if update else 'install'} in {repo}. Would create/update:")
        for dest, _, _ in changes:
            print("  " + str(dest.relative_to(repo)))
        return
    apply_changes(repo, changes)
    print(f"{'Updated' if update else 'Installed'} Devkit Codex adapter in {repo} ({len(changes)} files).")
    print("Commit the installed Devkit files to develop before making task worktrees.")
    print("Start a new Codex session and prompt: Use Devkit to <describe your task>.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", type=Path, help="Path to target Git repository root")
    parser.add_argument("--check", action="store_true", help="Validate the installation without writing")
    parser.add_argument("--update", action="store_true", help="Update only unchanged, previously managed Devkit files")
    args = parser.parse_args()
    try:
        install(args.repository, args.check, args.update)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
