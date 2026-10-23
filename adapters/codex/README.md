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

To preview and apply updates **after a manifest-backed installation**, run the installer from the updated Devkit source checkout:

```sh
python3 adapters/codex/install.py --check --update /absolute/path/to/your-repo
python3 adapters/codex/install.py --update /absolute/path/to/your-repo
```

The installer records installed file hashes in `.devkit/codex-install.json`. It updates only files still matching the last installed version, preserves other `AGENTS.md` content, and refuses user-edited managed files. Review and commit updated files before making new worktrees. Older installations without this manifest can add it by rerunning the installer **only if their files already match the current source**; otherwise update the conflicting files manually first.

The installer copies only the necessary Markdown and generates small Codex TOML files. Each specialist TOML tells Codex to **read its role Markdown at task start**, instead of storing a second copy of the full instructions:

```text
your-repo/
├── AGENTS.md                     # adds a marked Devkit section; keeps existing content
├── .devkit/
│   ├── codex-install.json          # installer record for safe updates
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

- Installer is **idempotent**: rerunning on unchanged files is a no-op. Use `--check` to preview and `--update` to replace only previously installed files that have not been edited locally. It keeps unrelated `AGENTS.md` content and refuses conflicts. There is no `--force` flag.
- It will fail if the root has `AGENTS.override.md`, since Codex would ignore the root `AGENTS.md`. Resolve manually for now.
- It does **not** change `.codex/config.toml`, model selections, approvals, or sandbox settings. Subagents inherit permissions from the main Codex session. **Read-only instructions for Tester and Reviewer are not a technical read-only sandbox**: use appropriate project permissions and review changes yourself.
- **One role source:** `.devkit/agents/*.md` is the source of truth after installation. A new subagent reads its own role Markdown at task start. Changes to role Markdown do not require regenerating TOML, but do not change an already-running agent. This file-read behavior still needs a real Codex end-to-end check.
- **Existing installations:** Older `devkit_*.toml` files may contain an embedded copy of role instructions. Review and replace those three files with the new generated loader TOMLs once; the installer will not silently overwrite them.
- Installation and updates write staged files and replace each file atomically. If a normal write fails midway, the installer attempts to restore earlier changes. This is **not** a crash-proof transaction; keep the files in Git and review your changes. No automatic uninstall is provided.
- Existing Devkit files installed before the manifest was introduced cannot be overwritten safely by `--update` without a known old version. Update conflicts manually once, then rerun to record the current installation.
- It does not install missing external tools or guarantee the target app can run. The workflow must report `BLOCKED` when tests or runtime surfaces are unavailable.
- This adapter is **Draft**, not production-validated. Integration on a real repository is still required.

Reference: [Codex subagents](https://developers.openai.com/codex/subagents) and [AGENTS.md](https://developers.openai.com/codex/guides/agents-md).
