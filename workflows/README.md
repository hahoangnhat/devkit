# Devkit Workflow Catalog

Status: **Design registry — not a claim of runtime readiness**.

## Purpose

List the everyday engineering outcomes Devkit intends to support. Keep the roles in `agents/` reusable and the task-specific sequence, evidence, and exit criteria in each `workflows/*.md` file. Do not put each workflow's stage order into `agents/orchestrator.md`.

## Initial catalog

| Workflow | Use when | Expected deliverable | State |
| --- | --- | --- | --- |
| `fix-bug.md` | Correct a reported defect | Reproduction, fix, regression evidence, review | **Draft** (file exists; untested end-to-end) |
| `investigate.md` | Explain behavior, diagnose a problem, or explore feasibility without modifying code | Findings, cited code references, uncertainties, next action | Planned |
| `implement-feature.md` | Introduce or change product behavior | Scoped implementation, behavior verification, review | Planned |
| `review-change.md` | Review a PR/diff without implementing changes | Findings with severity, concrete evidence, and decision | Planned |
| `refactor.md` | Improve structure while preserving externally observable behavior | Changed code, behavior-parity evidence, review | Planned |
| `maintenance.md` | Update tests, docs, dependencies, or tooling | Bounded maintenance change, specific checks, review if needed | Planned |

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

1. **Now:** Maintain this catalog and validate `fix-bug.md` with one real issue-to-verified-result run once the required agents and adapter exist.
2. **Next workflow to author:** `investigate.md` (read-only, low-risk, useful for many requests).
3. **Then:** `implement-feature.md` (first new code-producing workflow).
4. **Later:** `review-change.md`, `refactor.md`, then `maintenance.md`, each with its own evaluation before marking Ready.

Do not write all workflow files in advance. Keep this catalog synchronized with actual tested capabilities, not aspirations.
