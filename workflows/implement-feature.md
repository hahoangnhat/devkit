# Implement Feature Workflow

## Goal

Add or change product behavior requested by the user. Deliver working code with clear proof that it meets the agreed requirements. **Do not edit code until the change scope is approved.** Do not add work the user did not ask for.

## Roles

- **Orchestrator:** Records the goal, assigns steps, approves file scope, and reports the result. Does not write code or choose the technical design.
- **Developer:** Studies the code, proposes a small change, implements it after approval, and runs initial checks.
- **Tester:** Checks the requested behavior independently on the latest version. Does not edit code.
- **Reviewer:** Reviews the latest change after Tester passes. Does not edit code.

Follow the agent role files for technical steps and permissions. Use real subagents through the platform adapter. Skip code review when no code changes are needed.

## 1. Define the feature — Orchestrator

Record:

- **Goal:** What the user wants to do and why.
- **Expected:** What should happen, including important inputs, errors, and limits.
- **Acceptance:** Observable checks that would prove the feature works.
- **Target:** Project, code version, platform, and environment that matter.
- **Limits:** What is out of scope, plus time, cost, and permission limits.

Use the user's requirements, not guesses about product behavior. Ask the user when a missing product decision would change the result. Give Developer the known facts and acceptance checks.

## 2. Investigate and propose — Developer (no code edits)

Check the relevant code, tests, and existing behavior. Prefer the project's current patterns. Find the smallest useful approach and any important risks or dependencies.

Return:

- A short **plan** explaining the approach and why it fits.
- The **files to add or change**, with a reason for each.
- The **checks** needed to prove the feature works, including important existing behavior that must still work.
- Any open product questions or limits that block safe work.

**Do not edit code yet.** If the feature already appears to exist, report that and ask for independent verification instead of making an unneeded change.

## 3. Approve the change scope — Orchestrator

Check Developer's proposed file list against the user's limits and repository rules. Approve the files Developer may edit, or ask Developer for a clearer reason. Do not choose the technical design yourself.

If approval would exceed the user's permissions, ask the user first. Developer must request new scope approval **before editing any other file**.

## 4. Implement — Developer

Prepare a safe Git workspace as required by `agents/developer.md`. Work only within the approved scope.

Implement the agreed behavior with the smallest clear change. Add or update useful tests for success, failure, and edge cases where relevant. Avoid unrelated changes and new layers without a need.

Run initial checks. Report the exact changed version, file list, test commands and results, checks not run, and known risks. **Developer's own tests are not independent approval.**

## 5. Verify the feature — Tester

Check the **latest target version** against the acceptance checks, independently from Developer.

Use the real UI, API, CLI, library, or service that the feature affects when available. Check important error cases and nearby behavior that might break. Record the environment, inputs, expected and actual results, and any checks not run.

Return `PASS`, `FAIL`, or `BLOCKED` for the test stage, with evidence. Do not call an unavailable check a pass. If there was no code change because the feature seems to exist already, verify the current behavior against the same acceptance checks.

## 6. Review the change — Reviewer

After Tester returns `PASS`, review the **same exact version** and its full diff. Check correctness, important risks, approved scope, and test quality. Report `PASS`, `FAIL`, or `BLOCKED` with supported findings.

Skip this step if no code changed. Do not use review as a replacement for Tester's behavior checks.

## 7. Handle results and stop — Orchestrator

- **Tester `FAIL` or blocking Reviewer finding:** Send the evidence to Developer for a focused correction. Approve any needed new file scope first.
- **Code changes again:** Repeat affected Tester checks and the review on the new version. Old `PASS` results may no longer apply.
- **Required check cannot run:** Ask the responsible agent for a safe recovery. Otherwise report a blocker, not success.
- Allow up to **two code-correction rounds after the first implementation**. Stop when the work is verified, the limit is reached, no useful safe step remains, or a product decision is needed.

## Final result — Orchestrator

| Result | Meaning |
| --- | --- |
| `COMPLETED / IMPLEMENTED` | The latest implementation passed independent behavior checks and code review. |
| `COMPLETED / ALREADY_PRESENT` | The requested behavior was already present and independently verified; no code changed. |
| `BLOCKED / CHECKS_FAILED` | A required test or review still fails after the allowed corrections. |
| `BLOCKED / INCONCLUSIVE` | Evidence is not enough to confirm the requested behavior. |
| `BLOCKED / ENVIRONMENT_BLOCKED` | Required tools, environment, or access are not available. |
| `NEEDS_HUMAN / DECISION_REQUIRED` | A product decision or new permission is needed. |

Report the requested behavior, what changed (or why no change was needed), approved file scope, exact version checked, Tester and Reviewer results, tests not run, remaining risks, and a PR link only if one exists.

**Safety:** Do not merge, deploy, delete important data, or change protected systems without the required permission. A passing build alone does not prove the feature works.
