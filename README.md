# Devkit

Devkit is a reusable set of AI engineering role instructions and task playbooks. It describes how an agent should route work, delegate bounded stages, and report evidence. It is not an agent runtime; the Codex adapter connects these instructions to Codex's project-scoped agents.

## Start in a product repository

See [the Codex adapter guide](adapters/codex/README.md) for installation. After installing, start a fresh Codex session from the product repository root.

Give Devkit the result you want and how you will recognize it:

```text
Use Devkit: [desired change or question].
Done when: [observable result or evidence].
Context: [symptoms, relevant paths, logs, or decisions already made].
Constraints: [scope, compatibility, permissions, or actions to avoid].
```

For example:

```text
Use Devkit to fix duplicate notifications after a retry.
Done when: the retry flow produces one notification, with a regression check for the reported case.
Context: the issue occurs when the worker retries after a timeout.
Constraints: do not change notification delivery semantics outside this flow.
```

You usually do not need to name a playbook, agent, or sequence of tools. The Orchestrator routes the request from the outcome; include a specific workflow only when you need to override that choice.

## How the workflow runs

The Orchestrator reads the workflow catalog, loads the matching playbook, and delegates only the stages that add independent value. The Developer owns code edits. The Tester checks observable behavior when required. The Reviewer independently assesses the latest change when required. The Orchestrator ties each result to the artifact being delivered and reports checks that were not run.

## Make verification repeatable

The highest-value setup in each product repository is a small, reusable way to start the app, check that it is ready, exercise a real user or API path, capture evidence, and clean up only resources created for the run. Keep a short feature map that links important user paths to the observable result that proves each path works. Prefer existing project tools over creating a new control layer.

The Codex adapter installs role and workflow instructions; it does not create this product-specific verification setup. If a required behavior cannot be exercised, the workflow must report the verification gap instead of treating a build or source inspection as proof.

## Status and inspiration

All cataloged playbooks are marked **Draft** until representative delegated runs establish that their handoffs and evidence gates work in a real product repository. See [the workflow catalog](workflows/README.md).

Devkit adapts public pstack ideas for this Codex setup: state the goal and done check, prove behavior on the real product, then add parallel work where it is independent. It does not reproduce the Cursor plugin or treat PR volume as a quality or productivity target. See the [pstack prompting guide](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/02-poteto-mode.md) and [verification guide](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/06-verify-and-ship.md).
