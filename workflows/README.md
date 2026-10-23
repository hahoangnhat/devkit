# Devkit workflow catalog

Read this file first to choose a workflow. **Do not open all workflow files to compare them.** After choosing an available workflow, read only that workflow file in full.

| Workflow | Use when | Expected result | Status |
| --- | --- | --- | --- |
| `fix-bug.md` | A reported behavior is wrong and may need fixing | Evidence of a fix, an existing fix, no needed change, or a blocker | Draft |
| `investigate.md` | Understand code or a problem without changing code | Findings with code references and open questions | Draft |
| `implement-feature.md` | Add or change product behavior | Verified code change, already present behavior, or a blocker | Draft |
| `review-change.md` | Review a diff or PR without fixing it | Review verdict with findings and evidence | Draft |
| `refactor.md` | Improve code structure without changing behavior | Refactor with before-and-after checks, or a blocker | Draft |
| `maintenance.md` | Update tests, docs, dependencies, or tools | Scoped update with relevant checks, or a blocker | Draft |

**All six listed workflows are available as Drafts.** `Planned` means a file has not been implemented and must not be selected. `Draft` means instructions exist, but the workflow has not passed end-to-end tests.

## How to choose

- Choose by the user's **goal**, not by a keyword. A bug report may ask for investigation only.
- Choose one workflow for each separate task. Split unrelated goals before routing.
- Do not use `fix-bug.md` as a replacement for another workflow.
- If no available workflow fits, report `UNSUPPORTED_WORKFLOW` and ask the user to suggest a workflow or the next step. Do not start work without their guidance.
- A workflow does not grant permissions. Follow the user's limits, repository rules, and platform permissions.

## Delivering changes

For Fix Bug, Implement Feature, Refactor, and Maintenance, a verified file change is complete **only after** Developer commits with the active adapter's co-author, pushes the task branch, and opens or identifies a PR against `develop`. Orchestrator assigns this stage after independent checks. Follow `agents/orchestrator.md` and `agents/developer.md`; do not duplicate Git commands in each workflow. If delivery fails, report `BLOCKED / DELIVERY_BLOCKED` with the verified work and what remains.

A no-change result needs no empty commit or PR. Investigate and Review Change are read-only and never publish changes. An explicitly requested saved investigation report is a separate documentation change through Maintenance with approved scope.

## Workflow quality

`Planned` → `Draft` → `Tested` → `Ready`.

- `Draft`: Steps, roles, evidence, and stop rules are written.
- `Tested`: The workflow ran on a real platform, including a failure or blocked case; evidence was checked against the correct code version.
- `Ready`: Repeated tests show reliable results, no false success, and known limits are documented.

Add new workflows one at a time. Keep this catalog in sync with files that actually exist.
