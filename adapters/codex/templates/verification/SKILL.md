---
name: devkit-verify
description: Verify a documented product feature, capture revision-specific evidence, and report gaps honestly. Use when a Devkit task requires behavioral verification.
---

# Devkit verification

Use this skill to check observable product behavior. Product-specific commands and scenarios belong in `features/`.

## Select a feature

1. Read `features/README.md`.
2. Find a completed feature document that matches the task and acceptance criteria.
3. Treat `features/feature.template.md` only as an authoring guide. It is not a runnable scenario or verification evidence.
4. If there is no matching feature document, use the repository's existing verification instructions. If no suitable method exists, report `MANUAL_VERIFICATION_REQUIRED` or `BLOCKED` with the missing detail; do not invent product commands or claim a pass.

## Run the verification

1. **Launch:** Follow the selected feature's launch instructions. Record the exact command and the documented ready signal. Do not assume an application is ready because a process started.
2. **Doctor:** Confirm the repository root, current `HEAD` SHA, worktree state, target environment, required account/data state, and that the app is ready on the intended surface. Do not run against production or shared mutable data unless explicitly authorized.
3. **Drive:** Execute the feature steps in order. Compare each observable result with its stated expectation. Use the real UI, API, CLI, or other surface named by the feature document; source inspection alone does not verify behavior.
4. **Evidence:** Create `.devkit/runs/<run-id>/`, using a UTC timestamp and a sanitized lowercase feature slug with only letters, numbers, and hyphens. Add a short suffix if that directory already exists. Save relevant logs, screenshots, traces, or command output there. Write `run.json` using `references/run.schema.json`; include the exact `HEAD` SHA and whether the worktree was dirty. Use paths relative to the run directory in each check's `evidence` list. Redact credentials, tokens, and sensitive user data from artifacts and environment details.
5. **Cleanup:** Stop only processes and remove only temporary data created by this run. Preserve pre-existing processes and user data. Finish `run.json` after cleanup.

## Report status

- `PASS`: every required check passed with observable evidence tied to the recorded revision.
- `FAIL`: at least one required observable result failed.
- `BLOCKED`: the check could not be completed because a required environment, permission, tool, or input was unavailable.
- `MANUAL_VERIFICATION_REQUIRED`: the remaining required check needs a person or a suitable automated path has not been documented.

Record unrun checks as `NOT_RUN` with a reason. A missing screenshot is not automatically a failure when another suitable artifact proves the result, but every passing required check must point to evidence. Do not turn an unavailable or ambiguous check into `PASS`.
