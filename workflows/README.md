# Devkit Workflow Catalog

Status: **All cataloged workflows have authored playbooks. They remain Draft until representative runtime runs prove the gates below.**

## Purpose

List the everyday engineering outcomes Devkit intends to support. Keep the roles in `agents/` reusable and the task-specific sequence, evidence, and exit criteria in each `workflows/*.md` file. Do not put each workflow's stage order into `agents/orchestrator.md`.

## Design principles

Devkit adapts pstack's public engineering lessons to its own roles and Codex adapter; it is not a copy of the Cursor plugin. The workflow is designed around:

- A clear user outcome and observable done check; the Orchestrator selects the playbook.
- Repeatable evidence on the real product before increasing parallelism.
- One owner per change surface and specialist handoffs only when they add independent value.
- Repeated lessons encoded in code, checks, or reusable project tools instead of repeated chat instructions.
- Rigor proportional to the task's risk; agent count and PR volume are not success metrics.

## Prompting and project verification

Prompts should state the goal, how to tell it is done, useful known context, and real constraints. Do not enumerate roles or prescribe a tool sequence unless the request intentionally overrides the workflow.

Each product repository should provide, where feasible, a reusable verification path for launch/readiness, driving a real feature, collecting evidence, and cleanup, plus a feature map of user paths and their observable success criteria. Reuse existing tests and control tools. If a required surface is unavailable, report that gap as **BLOCKED** or **NOT_RUN**, not as a pass. The Codex adapter supplies a generic skill and feature template; product-specific commands and completed scenarios stay in the product repository.

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

1. **Authoring:** The six playbooks listed above are present as workflow definitions.
2. **Runtime validation:** After installing into the chosen project, run representative tasks through the matching adapter. Save the exact artifact revision and verification evidence; include a failure or blocker case for workflows that implement or verify changes.
3. **Readiness:** Update a workflow from Draft to Tested only after a real delegated run demonstrates its documented handoffs and gates. Mark it Ready only after repeatable runs support its claims and known platform dependencies are documented.

Keep this catalog synchronized with observed adapter capabilities, not aspirations. Document review alone does not establish runtime readiness.
