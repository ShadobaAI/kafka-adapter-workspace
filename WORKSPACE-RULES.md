# Kafka Adapter Workspace Instructions

## Workspace Layout

This workspace has a root Git repository and a fixed collection of independent nested repositories under `KAFKA_PROJECTS_ROOT`. The root repository does not own their product source or replace their Git histories.

The root repository owns workspace AI profiles, instructions and settings, including files kept at their required paths inside nested repositories. Nested repositories exclude these files and `.gitkeep`; `tools/ai` is temporarily retained in `tools` by explicit user request. Keep runtime data, secrets and personal settings outside version control.

| Repository | Canonical path |
|---|---|
| `kafka-adapter` | `adapter/adapter` |
| `kafka-adapter-base` | `adapter/base` |
| `kafka-adapter-examples` | `adapter/examples` |
| `kafka-adapter-conv` | `conversion/KFK` |
| `kafka-adapter-tests-reports` | `tests/reports` |
| `kafka-adapter-tests-ui` | `tests/ui` |
| `kafka-adapter-tests-unit` | `tests/unit/unit` |
| `YAxUnit` (upstream checkout) | `tests/unit/yaxunit` |
| `kafka-tools` | `tools` |
| `kfk-tasks` | `tasks` |

Before work, identify every affected repository and read its local `AGENTS.md` when present; otherwise use the relevant repository README. Instruction precedence is: current user instructions, local repository instructions, then this file.

## Bounded Navigation

- Start from a user-supplied or known path, relevant local documentation, or a bounded MCP query.
- Request only the objects, methods, sections, files, or line ranges needed for the next decision.
- When the location is unknown, search within the smallest plausible repository or project scope and widen only when evidence requires it.
- Do not recursively scan an entire repository or workspace, load a large complete module when a fragment is sufficient, or run multiple discovery methods for the same question.

## Evidence and Failure Gates

- Before every read/search, identify the unresolved `fact`, dependent `decision`, one authoritative `source`, minimal `scope`, and `stop condition`. Reuse established evidence; no new question means no call. Do not store reasoning logs.
- Keep session evidence (`fact`, `source`, `scope`, `valid until`) for health, readiness, routing/toolsets, source/hash, contracts, selection, normative text, fixtures, dependencies and callers. Reuse until restart/reconnect, reindex, branch/revision change, relevant mutation/error, contradiction or documented staleness. Invalidate affected facts only.
- Establish health and the exact project, alias, root, or path readiness before the first dependent call when that state is unknown. Only `ready` or `healthy` is usable. Treat `error`, `degraded`, `partial`, `not ready`, `stale`, `incomplete`, timeout, ambiguous routing, and unverifiable completeness as failure.
- Classify errors before continuing: `recoverable-workflow` (authorized missing adoption/creation/prerequisite/toolset) may be repaired only within scope, without destructive/high-risk action, new credentials/data or changed intent, then authoritatively validated. `correctable-invocation` permits one correction established by schema/guide/error or known route, never guessing. `transient-retryable` permits one documented transient retry only for an idempotent or documented safe-to-retry operation. These successful recoveries need no new user-triggered run.
- `infrastructure` (unavailable authority, required project not ready, stale/incomplete index/corpus), `authority-contradiction`, `unsafe-or-out-of-scope`, and `unknown` stop the affected work before mutation. Do not substitute another MCP, shell/filesystem, web, copied source or memory. Report tool, exact scope, error and blocked outcome. New user input is needed for missing data/authorization, scope expansion, manual external recovery or contradiction resolution; recovery never expands mutation scope.
- A mutation timeout is indeterminate: verify authoritative state before deciding the next step; never blindly retry a write. A second failed invocation correction or retry stops automatic recovery.
- Do not treat an unexpected empty result as proof of absence unless the required scope is ready, the operation's documented coverage can establish absence, and no known fact conflicts with it. A contradiction between required authoritative results stops the task; report both results without selecting the convenient one.
- One fact permits a narrow query, bounded candidate inspection and one justified escalation; stop at sufficient evidence. Further expansion needs a new unresolved fact. Never repeat successful equivalent discovery or compliance (same phase, digest, target, ledger semantics and current applicability) without invalidation. Batch only known necessary items.

## Repository Boundaries

- Change multiple repositories only when the user explicitly defines that scope or an approved SDD lists every affected repository.
- Otherwise, keep changes in the target repository and report dependent work separately.
- Preserve unrelated user changes.
- Keep MCP configuration in its owning project profile; do not route a project through another project's MCP.

## 1C Work

For work involving 1C projects, models, source, or 1C-related MCP tools, indexes, standards, tests or tooling, read the mandatory [1C rules](1C-RULES.md) before dependent work. Never access 1C configuration or extension source under `src/**` through filesystem, shell, generic file or patch tools; use the assigned authorities described there. Use `$1c-routing` only for a concrete 1C project or general 1C question, not unrelated repository, tooling, Git, documentation or engineering work.

## Non-1C Files

- Edit non-1C files directly only within task scope; preserve UTF-8, existing style, naming, interfaces, line endings, and operational defaults.
- Do not manually edit generated release artifacts, generated reports, `*.cf`, `*.cfe`, archives, runtime data, or generated project output.
- Do not invent build or test commands. Use commands documented by the affected repository.

## SDD and ADR

Write SDD documents in Russian while preserving technical identifiers, commands, and paths.

An approved SDD is required before implementing a non-trivial behavior change, public API change, data-schema change, or multi-repository change. A draft does not authorize implementation. Store SDDs under `tasks/sdd`; if it is missing, report a workspace-layout error. Routine local bug fixes, focused tests, documentation-only changes, and tooling corrections do not require an SDD unless they change one of those contracts.

Create an ADR only for a durable architecture or component-boundary decision and store it under `tasks/adr`.

## Documentation and Completion

- Update owning documentation when a public interface, configuration, deployment rule, constraint, command, or user-visible behavior changes; do not update product documentation for internal refactoring.
- Record implementation results, checks, unresolved verification, and deviations in an approved SDD when one governs the change.
- Report checks actually run and relevant checks that could not run. Do not claim unperformed verification.

## Safety

- Do not read, expose, or commit secrets, tokens, credentials, passwords, `.env` contents, or personal configuration.
- Do not use destructive Git, filesystem, EDT, database, volume, cache, service, remote-state, or history operations without explicit authorization.
