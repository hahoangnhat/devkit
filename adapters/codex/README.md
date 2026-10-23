# Devkit Codex adapter — first integration (Draft)

This is a **project-scoped installer**, not a new agent runtime. Codex is the runtime: the **main chat** acts as Orchestrator via `AGENTS.md` and uses native Codex custom agents for Tester, Developer and Reviewer. The canonical Markdown instructions remain in `devkit/agents/` and `devkit/workflows/`.

## Install into a real repository

Prerequisites: Python 3.11+ and a recent Codex CLI with custom subagents enabled. Codex must be installed and authenticated separately. **Run the command from the Devkit source checkout**, not the target repository:

```sh
git -C /absolute/path/to/your-repo switch develop
python3 adapters/codex/install.py --check /absolute/path/to/your-repo
python3 adapters/codex/install.py /absolute/path/to/your-repo
```

**Install on `develop`, then commit the Devkit files before creating task worktrees.** A worktree created from `develop` includes only files saved in that branch's commit, not uncommitted or untracked files in another checkout:

```sh
cd /absolute/path/to/your-repo
git add AGENTS.md .devkit .codex/agents
git commit -m "Add Devkit Codex instructions"
```

If Devkit was already committed to `develop`, do not create an extra commit. Use your normal branch and review process to land later updates on `develop`. Do not make task worktrees from a branch that lacks these files.

During Devkit development, rerun **the same install command** to copy your latest Devkit source:

```sh
python3 adapters/codex/install.py --check /absolute/path/to/your-repo
python3 adapters/codex/install.py /absolute/path/to/your-repo
```

**Rerunning install replaces Devkit-managed Markdown and TOML files**, even if you edited them locally. The installer replaces only the marked Devkit section in `AGENTS.md` and keeps other project instructions. Commit the Devkit files to `develop` before creating task worktrees.

The installer copies only the necessary Markdown and generates small Codex TOML files. Each specialist TOML tells Codex to **read its role Markdown at task start**, instead of storing a second copy of the full instructions:

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

For a real Fix Bug test when you're ready, ask:

> Use Devkit to investigate and fix this bug: [steps, observed behavior, expected behavior, environment]. Delegate to devkit_tester, devkit_developer and devkit_reviewer only when their stages are justified by the workflow. Do not merge or deploy.

In Codex CLI, `/subagents` shows spawned agent threads. If no subagents appear when explicitly requested, verify project trust, that `agents.enabled` has not been disabled, and that the Codex version supports project-scoped `.codex/agents/*.toml`.

## Safety and limits

- Rerunning the installer updates Devkit-managed files unconditionally; it **overwrites local changes** in `.devkit/agents/`, `.devkit/workflows/` and `.codex/agents/devkit_*.toml`. Use `--check` to preview paths that will change. Back up custom edits or keep them in Git before reinstalling.
- Other project files are untouched. In `AGENTS.md`, only the block between `<!-- devkit:codex:start -->` and `<!-- devkit:codex:end -->` is replaced. Broken or duplicate markers cause an error rather than risking unrelated instructions.
- The installer refuses symlinks on paths it manages and will not replace a directory. Existing `AGENTS.override.md` requires manual integration because it hides root `AGENTS.md`.
- It does **not** change `.codex/config.toml`, model choices, approval policy or sandbox settings. Subagents inherit permissions from the main Codex session. Tester/Reviewer read-only rules are instructions, not a technical sandbox.
- `.devkit/agents/*.md` remains the source of truth. The generated TOML asks each specialist to read its role Markdown at task start. Changes to role Markdown do not affect an already-running agent. This still needs a Codex end-to-end test.
- Files are replaced atomically **one at a time**. A failed run may leave a partly updated installation; rerun the same command to finish. The script does not provide rollback or uninstall.
- The target application and external tools must be prepared separately. Devkit remains **Draft**, not production-validated.

Reference: [Codex subagents](https://developers.openai.com/codex/subagents) and [AGENTS.md](https://developers.openai.com/codex/guides/agents-md).
