# Devkit Codex adapter — first integration (Draft)

This is a **project-scoped installer**, not a new agent runtime. Codex is the runtime: the **main chat** acts as Orchestrator via `AGENTS.md` and uses native Codex custom agents for Tester, Developer and Reviewer. The canonical Markdown instructions remain in `devkit/agents/` and `devkit/workflows/`. The reusable setup skill lives in `devkit/skills/setup-verification/`.

## Install into a real repository

Prerequisites: Python 3.11+ and a recent Codex CLI with custom subagents enabled. Codex must be installed and authenticated separately. For automatic PR delivery, install and authenticate GitHub CLI (`gh auth login`) and have push/PR access to the target repository. **Run the command from the Devkit source checkout**, not the target repository:

```sh
git -C /absolute/path/to/your-repo switch develop
python3 adapters/codex/install.py --check /absolute/path/to/your-repo
python3 adapters/codex/install.py /absolute/path/to/your-repo
```

**Install on `develop`, then commit the Devkit files before creating task worktrees.** A worktree created from `develop` includes only files saved in that branch's commit, not uncommitted or untracked files in another checkout:

```sh
cd /absolute/path/to/your-repo
git add AGENTS.md .devkit .codex/agents .agents/skills/setup-verification
git commit -m "Add Devkit Codex instructions"
```

If Devkit was already committed to `develop`, do not create an extra commit. Use your normal branch and review process to land later updates on `develop`. Do not make task worktrees from a branch that lacks these files.

During Devkit development, rerun **the same install command** to copy your latest Devkit source:

```sh
python3 adapters/codex/install.py --check /absolute/path/to/your-repo
python3 adapters/codex/install.py /absolute/path/to/your-repo
```

**Rerunning install replaces Devkit-managed Markdown and TOML files**, even if you edited them locally. The installer replaces only the marked Devkit section in `AGENTS.md` and keeps other project instructions. Commit the Devkit files to `develop` before creating task worktrees.

The installer copies only the necessary Markdown and one reusable skill, and generates small Codex TOML files. Each specialist TOML tells Codex to **read its role Markdown at task start**, instead of storing a second copy of the full instructions:

```text
your-repo/
├── AGENTS.md                     # adds a marked Devkit section; keeps existing content
├── .devkit/
│   ├── agents/
│   │   ├── orchestrator.md
│   │   ├── tester.md
│   │   ├── developer.md
│   │   └── reviewer.md
│   └── workflows/
│       ├── README.md
│       ├── fix-bug.md
│       ├── investigate.md
│       ├── implement-feature.md
│       ├── review-change.md
│       ├── refactor.md
│       └── maintenance.md
├── .agents/
│   └── skills/
│       └── setup-verification/
│           └── SKILL.md
└── .codex/
    └── agents/
        ├── devkit_tester.toml
        ├── devkit_developer.toml
        └── devkit_reviewer.toml
```

**Start a fresh Codex session from your repository root** (the project instruction chain is read at session startup):

```sh
cd /absolute/path/to/your-repo
codex
```

For a first read-only smoke test, ask:

> Use Devkit. Read the Orchestrator instructions and the Fix Bug workflow, list the three registered Devkit specialist roles, and explain how you would investigate a hypothetical bug. Do not edit files, run tests, or spawn agents.

For a read-only investigation, ask:

> Use Devkit to investigate how [component] works. Report file and line references. Do not change code.

For a real Implement Feature test when you're ready, ask:

> Use Devkit to add [feature] with [expected behavior and acceptance checks]. Have Developer investigate and propose files before editing. Do not merge or deploy.

For a read-only code review, ask:

> Use Devkit to review PR [link] or diff [ref]. Report blocking and advisory findings with evidence. Do not edit code, publish a PR review, or merge.

For a refactor, ask:

> Use Devkit to simplify [component] without changing its behavior. Have Developer propose the files, compare before-and-after checks, then ask Tester and Reviewer to verify. Do not merge or deploy.

For maintenance, ask:

> Use Devkit to update [docs/tests/dependency/tool] for [specific goal]. Keep the change small and check the relevant results. Do not merge or deploy.

To establish runtime verification on a runnable project, ask:

> Use Devkit Maintenance and the `setup-verification` skill to set up reliable verification for [app]. Prefer the project's existing tools, prove one real user path, and have Tester independently check the result. Do not change application behavior.

The installed `setup-verification` skill is a **setup procedure**, not a test tool. It may create project-owned `.agents/skills/verify-<app>/` instructions and tests after scope approval. Those generated skills are **not managed or overwritten by the Devkit installer**. If the project has no runnable behavior yet, the skill reports `NOT_READY` rather than inventing a feature map.

For a real Fix Bug test when you're ready, ask:

> Use Devkit to investigate and fix this bug: [steps, observed behavior, expected behavior, environment]. Delegate to devkit_tester, devkit_developer and devkit_reviewer only when their stages are justified by the workflow. Do not merge or deploy.

In Codex CLI, `/subagents` shows spawned agent threads. If no subagents appear when explicitly requested, verify project trust, that `agents.enabled` has not been disabled, and that the Codex version supports project-scoped `.codex/agents/*.toml`.

**Subagent lifecycle:** Devkit starts fresh specialists by default, passes reports and evidence to later tasks, and reuses agents only when they hold state that is hard to transfer. The Orchestrator collects final reports and tracks agent status. It closes completed threads **only if the active Codex runtime exposes an agent-close tool**. Some runtimes (including multi-agent V2) do not; `interrupt_agent` is not a replacement for closing a completed thread. Use `/subagents` to inspect agent activity. Completed threads may remain visible when no close tool exists; the installer cannot remove them.

## Commit, push, and PR delivery

For Fix Bug, Implement Feature, Refactor, and Maintenance, a **verified file change** is delivered by Developer after independent checks and review: commit only the approved diff, include the active adapter co-author, push the task branch, then create a PR against `develop`. The Codex adapter provides `CO_AUTHOR: Codex <noreply@openai.com>`; do not duplicate an attribution trailer already added by Codex. Normal Git author settings remain unchanged.

On the verified task branch, Developer may use Git and GitHub CLI:

```sh
git add -- <approved-paths>
git commit -m "<meaningful change>" -m "Co-authored-by: Codex <noreply@openai.com>"
git push -u origin <task-branch>
gh pr create --base develop --head <task-branch> --title "<title>" --body "<summary, checks, risks>"
```

Use `gh pr view` when a PR already exists; never open a duplicate. These are example commands, not commands run by the installer. If the remote, `gh`, authentication or permissions are missing, report `BLOCKED / DELIVERY_BLOCKED` with the verified local changes and recovery step. Do not force-push or auto-merge. Tasks with no file changes, plus the read-only Investigate and Review Change workflows, do **not** create commits or PRs. A request to save an investigation report should be handled as a separate Maintenance documentation change.

## Safety and limits

- Rerunning the installer updates Devkit-managed files unconditionally; it **overwrites local changes** in `.devkit/agents/`, `.devkit/workflows/`, `.agents/skills/setup-verification/` and `.codex/agents/devkit_*.toml`. Use `--check` to preview paths that will change. Back up custom edits or keep them in Git before reinstalling.
- Other project files are untouched. In `AGENTS.md`, only the block between `<!-- devkit:codex:start -->` and `<!-- devkit:codex:end -->` is replaced. Broken or duplicate markers cause an error rather than risking unrelated instructions.
- The installer refuses symlinks on paths it manages and will not replace a directory. Existing `AGENTS.override.md` requires manual integration because it hides root `AGENTS.md`.
- It does **not** change `.codex/config.toml`, model choices, approval policy or sandbox settings. Subagents inherit permissions from the main Codex session. Tester/Reviewer read-only rules are instructions, not a technical sandbox.
- `.devkit/agents/*.md` remains the source of truth. The generated TOML asks each specialist to read its role Markdown at task start. Changes to role Markdown do not affect an already-running agent. This still needs a Codex end-to-end test.
- Files are replaced atomically **one at a time**. A failed run may leave a partly updated installation; rerun the same command to finish. The script does not provide rollback or uninstall.
- The target application and external tools must be prepared separately. Devkit remains **Draft**, not production-validated.

Reference: [Codex subagents](https://developers.openai.com/codex/subagents) and [AGENTS.md](https://developers.openai.com/codex/guides/agents-md).
