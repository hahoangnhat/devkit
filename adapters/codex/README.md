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

For a first read-only instruction and routing smoke test, ask:

> Use Devkit to investigate how [a behavior] works. Read the Orchestrator instructions, workflow catalog, and selected playbook. Return an evidence-backed explanation with file references. Do not edit files, run tests, or spawn agents.

For a real task, state the requested outcome and let the catalog route it:

> Use Devkit to add a `--json` option to this CLI. Done when JSON output is valid and existing text output is byte-identical. Context: the current text format is used by scripts. Constraints: do not add dependencies.

You usually do not need to name a workflow category or tell the agent which roles to invoke. Add only the context and constraints that can change the implementation or its verification. Do not merge or deploy unless that action is explicitly part of the request and permitted by platform controls.

The first smoke test checks instruction loading and routing only; it does **not** prove that project-scoped agents can be invoked. Before relying on delegation, use a disposable scratch repository with read-only parent permissions and explicitly request one read-only handoff to `devkit_tester`. Confirm the real subagent appears in `/subagents`, its report cites the current repository, and it makes no changes. Then exercise a small end-to-end change in a disposable project before treating that workflow as runtime-validated.

In Codex CLI, `/subagents` shows spawned agent threads. If no subagents appear when explicitly requested, verify project trust, that `agents.enabled` has not been disabled, and that the Codex version supports project-scoped `.codex/agents/*.toml`.

## Safety and limits

- Installer is **idempotent**: rerunning on unchanged files is a no-op. It checks every path first, keeps existing `AGENTS.md` content and refuses conflicting files or modified managed sections rather than overwriting them. There is no `--force` flag.
- It will fail if the root has `AGENTS.override.md`, since Codex would ignore the root `AGENTS.md`. Resolve manually for now.
- It does **not** change `.codex/config.toml`, model selections, approvals, or sandbox settings. Subagents inherit permissions from the main Codex session. **Read-only instructions for Tester and Reviewer are not a technical read-only sandbox**: use appropriate project permissions and review changes yourself.
- It does not invoke or authenticate Codex, and there is no automatic upgrade/uninstall mechanism yet. For future Devkit changes, compare and intentionally replace generated files; conflicting reruns are rejected.
- It does not create the target product's verification harness or feature map. Add a small reusable way to launch/check readiness, exercise the real feature, capture evidence, and clean up in each target repository where feasible.
- It does not install missing external tools or guarantee the target app can run. The workflow must report `BLOCKED` when tests or runtime surfaces are unavailable.
- This adapter is **Draft**, not production-validated. Integration on a real repository is still required.

Reference: [Codex subagents](https://developers.openai.com/codex/subagents) and [AGENTS.md](https://developers.openai.com/codex/guides/agents-md).
