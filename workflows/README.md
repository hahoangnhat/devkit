# Devkit Workflow Catalog

Status: **All cataloged workflows have authored playbooks. They remain Draft until representative runtime runs prove the gates below.**

## Purpose

List the everyday engineering outcomes Devkit intends to support. Keep the roles in `agents/` reusable and the task-specific sequence, evidence, and exit criteria in each `workflows/*.md` file. Do not put each workflow's stage order into `agents/orchestrator.md`.

## Design principles

The owner built Devkit's workflow system as an independent approach tailored to this repository. Its routing, roles, handoffs, outcomes, evidence gates, readiness criteria, and authorization boundaries are defined by Devkit's own contracts and conventions.

The playbooks aim to make each task's expected behavior and completion evidence clear, keep changes bounded and verifiable, assign ownership explicitly, and stop when the workflow lacks evidence or authorization to continue. They do not claim compatibility with another workflow system.

## Initial catalog

| Workflow | Use when | Expected deliverable | State |
| --- | --- | --- | --- |
| `fix-bug.md` | Correct a reported defect | Reproduction, fix or evidence-backed no-change result, verification, review | **Draft** (authored; runtime validation pending) |
| `investigate.md` | Explain behavior, diagnose a problem, or assess feasibility without modifying code | Evidence-backed answer, cited references, uncertainties, next action | **Draft** (authored; runtime validation pending) |
| `implement-feature.md` | Introduce or intentionally change product behavior | Scoped implementation, behavior verification, review | **Draft** (authored; runtime validation pending) |
| `review-change.md` | Review a specified change without implementing it | Findings with severity, evidence, and review disposition | **Draft** (authored; runtime validation pending) |
| `refactor.md` | Improve structure while preserving observable behavior | Named target shape, behavior-parity evidence, review | **Draft** (authored; runtime validation pending) |
| `maintenance.md` | Update tests, docs, dependencies, or tooling | Bounded change, specific checks, risk-based review | **Draft** (authored; runtime validation pending) |

## Routing principles

1. **Classify by expected outcome, not by keyword.** A request containing “bug” might be investigation-only; a review request must not silently authorize code changes.
2. **Keep roles separate from workflows.** Orchestrator coordinates; Tester checks behavior; Developer owns code edits; Reviewer assesses changes. Only invoke the roles the selected workflow needs.
3. **Choose one primary workflow per bounded unit.** If a request contains independent outcomes, separate them into units before choosing playbooks.
4. **No silent substitutions.** Do not route a new feature through `fix-bug.md` merely because it is the only available playbook.
5. **Missing workflow:** For a narrowly scoped, low-risk, reversible task, Orchestrator may build a *task-local plan* using the same safety and evidence requirements. Mark this as `task-local`, not an established production workflow. For higher-risk or unclear work, stop with a precise blocker or escalate an actual decision.
6. **Access is not granted by this catalog.** Repository permissions, adapter capabilities, and explicit user authorization govern actions. Do not merge, deploy, delete data, or change protected infrastructure without authorization.

## Readiness gates for every new workflow

A workflow moves through **Planned → Draft → Tested → Ready**, never directly to Ready after its Markdown is written.

- **Draft:** Defines entry conditions, goal/done predicate, actors, stage order, required handoff fields, expected evidence, stopping/retry conditions, and authorization gates.
- **Tested:** Successfully completes a representative task and handles at least one failure/blocker case using real platform delegation. Validate that reported evidence matches the artifact/version inspected. Save the results.
- **Ready:** Has repeatable results across representative tasks, no false-success behavior in evaluation, and known limitations and platform dependencies are documented. A Ready workflow is still constrained by adapter and repository permissions.

## Incremental delivery order

1. **Authoring:** The six playbooks listed above are present and ready for review as workflow definitions.
2. **Runtime validation:** After installing into the chosen project, run representative tasks through the matching adapter. Save the exact artifact revision, verification evidence, and at least one blocked or failure case for each workflow that uses those stages.
3. **Readiness:** Update a workflow from Draft to Tested only after a real delegated run demonstrates the documented handoffs and gates. Mark it Ready only after repeatable runs support its claims.

Keep this catalog synchronized with observed adapter capabilities, not aspirations. Document review alone does not establish runtime readiness.
