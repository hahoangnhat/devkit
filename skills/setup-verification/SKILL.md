---
name: setup-verification
description: Establish or repair project-local runtime verification when an app has no reliable user-facing verification harness. Do not use for ordinary test runs.
---

# Setup project verification

Use this skill when a project needs a repeatable way to run the application, exercise real behavior, and collect proof. This skill describes the setup procedure; it is not a browser driver or test framework. Follow the active Devkit workflow, agent role, approved file scope, and platform permissions. Do not create a separate workflow.

## 1. Inspect before changing anything

- Identify the real user-facing surface: browser, desktop, CLI/TUI, API, mobile app, or library. A repository may have more than one.
- Find the existing start commands, test tools, fixtures, and automation. Prefer a working Playwright, Cypress, HTTP, PTY, or other project harness over introducing a new one.
- Determine a safe, isolated test environment: test accounts, local data, ports, services, credentials, and a way to clean up only resources this run owns.
- If no usable application behavior exists yet, **stop and report NOT_READY**. Do not invent routes, selectors, expected results, or an untested feature map. Revisit setup after the first runnable feature exists.
- If verification already works and is documented, report how to use it. Do not create a duplicate skill or wrapper.

## 2. Propose the smallest useful setup

Explain the test surface, chosen tool, why existing tools are insufficient (if applicable), proposed files and dependencies, first behavior to verify, evidence to capture, and cleanup plan. Wait for Orchestrator's scope approval before writing files when operating under Devkit. Ask for approval before installing dependencies or using privileged, shared, external, or production resources.

Do not build a custom `control-*` CLI just to wrap an existing usable tool. Add a helper script only if it makes a repeated action reliable and simpler.

## 3. Create a project-local verification skill

Use the active platform's native skill location. On Codex, create `.agents/skills/verify-<app>/SKILL.md` where `<app>` is a short, stable project name. This **project-owned** skill is separate from the Devkit-managed `setup-verification` skill.

Write a discoverable `name` and `description` in YAML frontmatter, and document only commands and behavior verified in the repository:

- **Launch:** exact way to start a usable test instance, including prerequisites, isolated fixtures, and readiness condition.
- **Doctor:** one read-only check for the right running app, build, data, and authentication state.
- **Drive:** exact user-path actions using the chosen tool. Prefer accessible roles, labels, stable identifiers, commands, or API contracts over screen coordinates and brittle selectors.
- **Evidence:** actions, expected and actual outcomes, and saved logs, output, screenshots, or read-back state. A green command alone is not proof of behavior.
- **Cleanup:** stop only processes and remove only temporary data created by this run. Preserve evidence.

Add a `features/README.md` index plus **only features currently implemented and observable**, starting with one to three if the project is small. Each feature file records the user-visible purpose, entry points, prerequisites, exact drive steps, observable success or failure, and gotchas. Keep implementation details out of the feature map; inspect current source when code paths matter.

Keep actual automated tests in the project's existing test directories when possible. Put optional scripts beside the skill only when they are needed to reproduce the documented procedure. Do not install a new framework if the existing one can drive the feature.

## 4. Prove the instructions work

On the exact intended workspace and code state, execute **Launch → Doctor → Drive one mapped feature → Capture evidence → Cleanup**. Confirm the evidence survived cleanup and inspect any files or settings changed by tests. If a step fails, fix the setup within approved scope and repeat the affected proof. Do not lower expected results to force a pass.

If the application cannot start, the harness cannot reach the real user path, or a required tool or environment is unavailable, report **BLOCKED** with the attempted commands and missing prerequisite. A skill that has not passed one real drive is a draft, not verified setup. Do not present the remaining feature entries as tested just because one entry passed.

## 5. Hand off for independent checking

Report the generated skill and harness paths, actual commands, tested feature and entry point, code version, evidence location, cleanup result, untested features, and remaining risks. Under Devkit, hand this to Orchestrator for independent Tester checks and Reviewer assessment. Commit, push, and PR delivery belong to the chosen workflow's authorized publication stage, not to this skill.

When application behavior or the harness changes later, compare the feature map with the current app and update only affected entries with fresh evidence. Do not silently rewrite product behavior to make documentation appear correct.
