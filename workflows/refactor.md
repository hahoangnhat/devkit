# Refactor Workflow

## Goal

Make existing code easier to read, change, or maintain **without changing its behavior**. Show that important behavior still works. Do not add features or fix unrelated bugs.

## Roles

- **Orchestrator:** Sets the goal, assigns work, approves file scope, and reports results. Does not design or edit the refactor.
- **Developer:** Proposes files, records a baseline, and makes approved changes.
- **Tester:** Independently checks behavior before and after the change.
- **Reviewer:** Reviews the latest diff after Tester passes.

Use the agent role files for technical details and permissions. Start only the agents needed for each stage.

## 1. Define the goal — Orchestrator

Record:

- **Goal:** What code should be simpler and why.
- **Keep:** Behavior, public APIs, outputs, errors, and data formats that must not change.
- **Success:** The intended code improvement and checks that show behavior is preserved.
- **Target:** Repository, version, and environment.
- **Limits:** Out-of-scope areas, time, cost, and permissions.

If the user wants a behavior change, clarify it or choose another workflow. Do not pick a technical solution for Developer.

## 2. Investigate and propose — Developer (read-only)

Study the code, callers, tests, and history. Find a small change that has a clear benefit.

Report the planned approach, **files to edit with reasons**, important risks, and **baseline checks** to run on the original version and repeat after the change.

**Do not edit code yet.** If no useful refactor is needed, explain why and stop. If the important behavior cannot be checked, propose a safer plan or report the gap.

## 3. Approve the file scope — Orchestrator

Check Developer's proposed files against the user's limits and repository rules. Approve the file list or request a better explanation. Do not decide how the refactor should be implemented.

Developer must ask for approval **before editing any other file**. Ask the user only when broader permission or a product decision is needed.

## 4. Make the refactor — Developer

Prepare a safe Git workspace using `agents/developer.md`. Before editing, run the baseline checks on the original code when possible. Record the **exact version**, commands, inputs, and results.

Edit only approved files. Preserve behavior and contracts. Keep the diff focused; add tests when they help protect existing behavior. Do not quietly introduce new dependencies or unrelated cleanup.

Run the relevant checks again and compare with the baseline. Report the changed version, diff, test results, checks not run, and remaining risks. If an important comparison is not possible, say so; **do not call it verified**.

## 5. Check unchanged behavior — Tester

Independently check the **latest changed version** against the baseline or other reliable before-and-after evidence. Use the relevant UI, API, CLI, or service when possible.

Check important outputs, errors, edge cases, and affected callers. Record the original and changed versions, environment, steps, expected and actual results, and missing checks.

Return `PASS`, `FAIL`, or `BLOCKED` with evidence. A passing build alone does not prove unchanged behavior.

## 6. Review — Reviewer

After Tester passes, review the **same version**. Check the change's benefit, behavior risks, tests, and approved file scope. Return `PASS`, `FAIL`, or `BLOCKED` with supported findings.

Skip review when no code changed. Do not require unrelated cleanup.

## 7. Handle results — Orchestrator

- On Tester `FAIL` or blocking review findings, send evidence to Developer for a focused correction.
- Approve any new files before Developer edits them. After a change, rerun affected Tester checks and review on the new version.
- For missing baseline evidence or required checks, ask the right agent for a safe next check. Otherwise report a blocker.
- Allow up to **two code-correction rounds after the first refactor**. Stop when verified, limits are reached, or no useful safe step remains.

## Deliver the verified change — Orchestrator and Developer

For verified file changes, follow `agents/orchestrator.md` → **Deliver verified changes** before reporting `COMPLETED`. If publishing fails, report `BLOCKED / DELIVERY_BLOCKED`. No change means no commit or PR.

## Final result — Orchestrator

| Result | Meaning |
| --- | --- |
| `COMPLETED / REFACTORED` | Latest refactor passed independent behavior checks and review, and its PR was delivered. |
| `COMPLETED / NO_CHANGE_NEEDED` | No justified code change was found; no files changed. |
| `BLOCKED / CHECKS_FAILED` | Required tests or review still fail after allowed corrections. |
| `BLOCKED / INCONCLUSIVE` | Evidence cannot confirm important behavior stayed the same. |
| `BLOCKED / DELIVERY_BLOCKED` | Required checks passed, but the verified change could not be committed, pushed, or delivered as a PR. |
| `BLOCKED / ENVIRONMENT_BLOCKED` | Required tool, environment, or access is missing. |
| `NEEDS_HUMAN / DECISION_REQUIRED` | A user decision or new permission is needed. |

Report the goal, approved files, exact versions, baseline and final checks, Tester and Reviewer results, tests not run, and risks. Link a PR only if it exists.

**Safety:** Do not merge, deploy, or make hard-to-undo changes without permission. Do not hide behavior changes inside a refactor.
