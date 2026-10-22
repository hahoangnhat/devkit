# Devkit Codex adapter — first integration (Draft)

This is a **project-scoped installer**, not a new agent runtime. Codex is the runtime: the **main chat** acts as Orchestrator via `AGENTS.md` and uses native Codex custom agents for Tester, Developer and Reviewer. The canonical Markdown instructions remain in `devkit/agents/` and `devkit/workflows/`.

## Install into a real repository

Prerequisites: Python 3.11+ and a recent Codex CLI with custom subagents enabled. Codex must be installed and authenticated separately. **Run the command from the Devkit source checkout**, not the target repository:

```sh
python3 adapters/codex/install.py --check /absolute/path/to/your-repo
python3 adapters/codex/install.py /absolute/path/to/your-repo
```

The installer copies only the necessary Markdown and generates:

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
│       └── fix-bug.md
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

For a real test when you're ready, ask:

> Use Devkit to investigate and fix this bug: [steps, observed behavior, expected behavior, environment]. Delegate to devkit_tester, devkit_developer and devkit_reviewer only when their stages are justified by the workflow. Do not merge or deploy.

In Codex CLI, `/subagents` shows spawned agent threads. If no subagents appear when explicitly requested, verify project trust, that `agents.enabled` has not been disabled, and that the Codex version supports project-scoped `.codex/agents/*.toml`.

## Safety and limits

- Installer is **idempotent**: rerunning on unchanged files is a no-op. It checks every path first, keeps existing `AGENTS.md` content and refuses conflicting files or modified managed sections rather than overwriting them. There is no `--force` flag.
- It will fail if the root has `AGENTS.override.md`, since Codex would ignore the root `AGENTS.md`. Resolve manually for now.
- It does **not** change `.codex/config.toml`, model selections, approvals, or sandbox settings. Subagents inherit permissions from the main Codex session. **Read-only instructions for Tester and Reviewer are not a technical read-only sandbox**: use appropriate project permissions and review changes yourself.
- It does not invoke or authenticate Codex, and there is no automatic upgrade/uninstall mechanism yet. For future Devkit changes, compare and intentionally replace generated files; conflicting reruns are rejected.
- It does not install missing external tools or guarantee the target app can run. The workflow must report `BLOCKED` when tests or runtime surfaces are unavailable.
- This adapter is **Draft**, not production-validated. Integration on a real repository is still required.

Reference: [Codex subagents](https://developers.openai.com/codex/subagents) and [AGENTS.md](https://developers.openai.com/codex/guides/agents-md).
