# Investigate Workflow

## Goal

Answer a question about code or a reported problem using clear evidence. **Do not change code.** Use this workflow when the user wants to understand something, not fix it. A bug report can be investigation-only if that is what the user asks for.

## Roles

- **Orchestrator:** Defines the question, assigns work, handles blockers, and reports the result. Does not investigate.
- **Developer:** Reads code and history to explain how things work or find a cause. Does not edit code.
- **Tester:** Checks real behavior when runtime evidence is needed. Does not edit code.
- **Reviewer:** Not needed. There is no code change to review.

Follow the agent roles and permissions. Use real subagents through the platform adapter.

## 1. Define the question — Orchestrator

Record the **question**, the **target** (repo, version, or environment), what **evidence** would answer it, and any **limits**. Do not require a product decision unless it is needed to answer the question.

Give code questions to Developer. For a runtime symptom, Tester may go first to collect evidence. Use both only when needed.

## 2. Investigate — Developer

Read the relevant code, tests, configuration, logs, and history. Follow the parts that help answer the question; do not read unrelated files without a reason.

- For **how it works**, explain the main steps and point to the code.
- For **why it happens**, test possible explanations against evidence. Do not present a guess as a confirmed cause.
- For a reported problem, use Tester's observations when available. Note which conditions are still unknown.

Return `STAGE: INVESTIGATE` with findings, file and line references where relevant, the version examined, and any open questions. **Do not edit files or start a fix.**

## 3. Check behavior if needed — Tester

Skip this step when code evidence already answers the question. Otherwise Orchestrator gives Tester a specific behavior to check.

Test the right UI, API, CLI, or service when available. Record the version, environment, steps, results, and checks not run. A passing build or test suite alone does not prove runtime behavior.

Try another test only if it answers a useful question and stays within the time and tool limits. **There is no fixed attempt count.** Return observed facts or a clear blocker, not a final result.

Orchestrator sends new evidence to Developer if a technical explanation still needs work. Independent safe tasks may run together.

## 4. Finish or stop — Orchestrator

Use the specialist reports to decide whether the main question has an evidence-backed answer. If evidence conflicts or is missing, ask the right agent for one more useful check. **Do not investigate or choose a technical answer yourself.**

Stop when the question is answered, no useful safe check remains, a limit is reached, or permission is needed. Do not mark an unclear answer as confirmed.

## Final result — Orchestrator

| Result | Meaning |
| --- | --- |
| `COMPLETED / FINDINGS` | The main question has an evidence-backed answer. |
| `BLOCKED / INCONCLUSIVE` | The evidence is not enough to answer the main question. |
| `BLOCKED / ENVIRONMENT_BLOCKED` | A required tool, environment, or access is unavailable. |
| `NEEDS_HUMAN / DECISION_REQUIRED` | A user decision or permission is required. |

Report **the answer first**, then supporting code references or runtime evidence, the version checked, any unknowns, and the next useful check if blocked. Say when no runtime test was needed.

**Read-only rule:** Do not edit tracked code, tests, or config; do not create commits, branches, or worktrees for this task. Only use safe temporary test data when allowed. Do not merge or deploy. If a fix is needed, report it as a recommendation; use a separate change workflow only when the user requests it.
