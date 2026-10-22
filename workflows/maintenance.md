# Workflow: Maintenance

## Purpose

Complete one bounded upkeep task in tests, documentation, dependencies, or engineering tooling while preserving product behavior unless the request explicitly changes it.

Use **Implement Feature** for new product behavior, **Fix Bug** for a reported defect, **Refactor** for a structure-only code change, **Review Change** for read-only assessment, and **Investigate** when the requested deliverable is an answer.

## Roles and authority

- **Orchestrator:** Classifies the maintenance task, scopes paths and risk, chooses verification, and owns the final outcome.
- **Developer:** Makes the authorized change and checks the directly affected surface.
- **Tester:** Independently verifies behavior only when a changed test, tool, or document makes a material user or runtime claim that needs separate proof.
- **Reviewer:** Reviews dependency, shared tooling, CI, security, or broad configuration changes when independent review materially reduces risk. For a small documentation-only correction, Orchestrator may omit Reviewer and explain why.

Follow **agents/orchestrator.md**, repository rules, and any applicable security or release controls. Do not change protected settings, credentials, production systems, or external state without the required authorization.

## 1. Classify and bound the task — Orchestrator

Choose one primary deliverable:

- **Tests:** Add, repair, or organize checks for observable behavior.
- **Documentation:** Correct user, developer, or operational guidance.
- **Dependency:** Update or remove a direct dependency and its lock data.
- **Tooling/configuration:** Improve a developer command, build/test setup, CI check, or local engineering configuration.

Record the exact desired result, allowed paths, current revision, acceptance checks, and excluded behavior. Split independent deliverables into separate bounded units when that makes ownership or verification clearer. If the task reveals a product behavior change, route that portion through the matching workflow.

## 2. Check the baseline and relevant source — Developer

Inspect repository guidance, current scripts and conventions, callers, manifests, lockfiles, docs, and existing tests related to the task. Record existing failures or user changes before editing.

For dependency work, identify the direct dependency and intended version range. Check authoritative release notes, compatibility information, and relevant security advisories when they affect the requested update. Do not perform a broad upgrade or edit unrelated lock entries merely to make the diff look current.

For documentation, verify claims and commands against the current source. For tests, ensure the assertion describes behavior a user or caller can observe. For tooling, inspect every entry point and consumer affected by the change.

## 3. Make the bounded change — Developer

- Change only the paths and behavior needed for the maintenance outcome.
- Preserve existing product behavior and repository policy.
- Keep tests focused on the behavior they claim to protect.
- Keep dependency and lockfile changes consistent with the project toolchain.
- Avoid unrelated formatting, migrations, renames, or configuration cleanup.

Stop and return to Orchestrator if the change would broaden access, weaken security or CI protections, introduce a material compatibility or licensing choice, or exceed the authorized paths.

## 4. Verify the affected surface — Developer, Tester when needed

Run the repository's relevant command or inspect the actual artifact affected:

- **Tests:** Run the changed tests and relevant adjacent checks; confirm the assertion would fail if the stated behavior regressed.
- **Documentation:** Check links, named files, examples, and commands against the repository. Run a documented command only when permitted and safe.
- **Dependencies:** Inspect manifest and lockfile diff, resolve/import the package where feasible, and run the relevant compatibility checks.
- **Tooling/configuration:** Invoke the changed command or validate its generated result; inspect affected CI/config consumers.

Use Tester when an independent check of runtime behavior or of a changed test/tool is needed. Record exact commands, results, environment, and artifact revision. A skipped check is **NOT RUN**; an unavailable check is **BLOCKED**. Neither is a pass.

## 5. Review according to risk — Reviewer when needed

Reviewer inspects the exact latest diff for correctness, blast radius, security or policy impact, scope, and evidence quality. Always use Reviewer for shared tooling, CI/security policy, or material dependency changes. Orchestrator may omit the role for a low-risk documentation-only change after recording the reason.

Any material correction invalidates affected checks and review. Rerun them on the new artifact.

## Stop conditions and outcome

- **COMPLETED / MAINTENANCE_DELIVERED:** The bounded deliverable is correct and its applicable checks passed on the latest artifact.
- **BLOCKED / VERIFICATION_BLOCKED:** A required command, runtime, access, or source of compatibility evidence is unavailable.
- **BLOCKED / INCONCLUSIVE:** Checks ran but do not support the required conclusion.
- **NEEDS_HUMAN / DECISION_REQUIRED:** The task requires an unresolved policy, compatibility, licensing, product, or authorization decision.

## Required report

Include maintenance category and desired result; repository/revision and changed paths; exact commands/checks and outcomes; Tester and Reviewer results or why they were not needed; dependency/configuration risks where relevant; checks not run; and one next action for any blocker. Link a PR only if one was actually created.
