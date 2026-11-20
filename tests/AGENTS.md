# Kafka Adapter test workspace

Read and apply the mandatory [workspace rules](../WORKSPACE-RULES.md) and the applicable project or repository instructions. If the shared rules are missing, report a workspace-layout error and stop. User instructions take precedence over project and workspace rules.

Select `tests` as the Codex working directory. Read [project context](.ai/PROJECT.md) for ownership and [the profile](.ai/project.yaml) for mappings; do not assume these instructions or the profile are discovered when starting inside a nested Git repository.

## Test workspace

- `ui` owns Vanessa Automation scenarios and test configuration. Existing scenarios and run results are evidence of test behavior. `unit/unit` is the project-owned test extension.
- `unit/base` is assembled from the adapter repositories: change the originals through the adapter project, then update the assembled copy using the existing script when authorized. `unit/examples` is a checkout of adapter examples: change the original through the adapter project and update this checkout through Git when authorized. Do not make product fixes in these copies. Examples are development-only, not a production artifact.
- `unit/yaxunit` is an upstream framework checkout. Justified changes are permitted within task scope; preserve upstream conventions, keep Kafka-specific changes narrowly scoped, and leave changes uncommitted unless explicitly requested. Its framework role does not itself authorize a mutation. Run focused upstream checks when available.
- Use the unit EDT workspace and the applicable unit code-index bindings for dependent UI and unit work; stop a dependent operation when its required service or exact mapping is unavailable. EDT and v8std retain their assigned authority. Use BSL LS for focused analyzer work and changed BSL diagnostics when enabled and prepared, not as a prerequisite for unrelated UI operations. OpenViking is an optional, preferred source for adapter documentation when ready and does not replace EDT or v8std.
- Use `$yaxunit-tests` for YAxUnit work and apply its naming requirements to test modules; use `кфк_т_` for new objects owned by examples. Preserve Russian 1C identifiers. Use focused EDT diagnostics and relevant focused tests; report unavailable checks. Before introducing reusable behavior, check existing facilities and justify solution complexity at design and review.
- Assembly scripts and non-1C test configuration may be edited directly in UTF-8 within scope; never manually edit generated EDT projects, reports, or test output. Do not change product repositories without explicit multi-repository scope.

## UI scenarios

- Edit feature files and other non-1C test configuration directly in UTF-8; preserve Gherkin language, names, indentation, fixtures and scenario style. Use `$vanessa-ui-tests` for UI scenarios. Interactive runs use `ui/.vanessa/profile.json` and the built-in data processor at `/URL e1cib/app/Обработка.VanessaAutomationsingle`. Static design, review and authoring do not require the interactive profile.
- For isolated Docker UI runs, follow [kafka-docker-tests](.agents/skills/kafka-docker-tests/SKILL.md). Docker runs use the release CI's Vanessa Single EPF and `ui/VAParams.json`.
- Run only affected features or scenarios with documented commands when the environment is available. Run relevant adapter scenarios covering a change when available.
- For `кфкПродюсеры` and `кфкКонсьюмеры`, cover items and groups (task dispatchers) for each applicable operation in independent scenarios. Check operations, saved state and permissions separately; derive group expectations from its own form and commands. Use scenario-owned dispatchers for write tests and clean them up on success or failure; do not modify prepared `Диспетчер задач` groups merely as local cleanup.

### UI test design

- Test adapter-specific behavior observable by a user, such as a command, form-to-setting connection or role-specific access. Check relevant YAxUnit coverage for the same behavior and conditions and do not duplicate unit checks. A UI case may cover the same feature when it verifies a distinct user-visible contract. If overlap cannot be assessed, report it as unverified and defer the potentially duplicate case.
- Do not test 1C platform functionality for its own sake; check the adapter's use of a control or dialog only when that integration is the objective.
- Assume functionality works by default. Include only actions and checks needed for the scenario's objective, preparation, isolation, cleanup and recovery. Assert the expected observable result: navigation or absence of an exception is insufficient. Do not hide a failure of the tested behavior.
- Prefer UI actions under the appropriate TestClient rights. Use code, including BSL or direct data access, only when an equivalent UI action is unavailable or would make the test substantially more complex. Exported form methods may be called when they substantially simplify the test. A direct call alone does not verify command wiring, availability or permissions; check those through the UI when they are the objective.
- UI scenarios may use functionality, objects, fixtures and helpers from `unit/base` (`base`), `unit/examples` (`examples`) and `unit/yaxunit` (`yaxunit`) when applicable to the execution context. Follow the ownership and change boundaries above.
- Move project-defined universal steps into a reusable step library. First check for a suitable standard or project step. Libraries may use exported scenarios or custom steps; keep them separate from runnable tests as described in the [UI README](ui/README.md). Ensure the library is available on every intended route for the affected scenarios, including interactive and CI runs where applicable; report routes that could not be verified.

### UI test isolation and data

- Each scenario, including each example of a scenario outline, must run independently, repeatedly and in any order. Its preparation may use `Контекст`, shared steps and initialized fixtures, but must not depend on another test's execution or results. Account for data left by earlier runs, including failures, and prepare the required state of the fixtures the scenario uses. Use scenario-owned or shared fixtures and restore shared fixtures as needed according to [fixtures and initialization](.ai/FIXTURES.md).
- If a scenario requires empty tables, clear the necessary tables directly in its feature's preparation before creating its fixtures; do not require a manually pre-cleared database. Do not add separate checks of the target infobase, conflicting data or activity, or cleanup result solely for this preparation. For testing, full cleanup of any or all tables with the prefixes `кфк` and `кфк_т_` is permitted, but is not required before every scenario.
- A planned full cleanup can remove shared fixtures, including prepared dispatcher groups. Prepare what the scenario needs after cleanup and plan restoration of affected shared fixtures after success or failure; this is distinct from modifying prepared groups to clean up one scenario's items. Follow [Test data](#test-data) and [fixtures and initialization](.ai/FIXTURES.md); reinitialization is not a general rollback.

## Users and sessions

The manager and every TestClient use Taxi (`/iTaxi`). The community license permits at most three simultaneous sessions: one manager and two TestClients.

| User | Rights and use |
| --- | --- |
| `АдминистраторТакси` | Full infobase administrator; always the test manager. |
| `Администратор` | Full infobase administrator using interface 8.5; not used in tests. |
| `АдминистраторKafka` | Kafka subsystem administrator; `кфкПолныеПрава` instead of `кфкБазовыеПрава`; administrative TestClient. |
| `ПользовательKafka` | Kafka subsystem read/audit; `кфкБазовыеПрава`; restricted-rights TestClient. |

Test administrative actions as `АдминистраторKafka` and read/audit restrictions as `ПользовательKafka`; manager rights must not replace the tested user's rights. Both Kafka users have additional roles for example data, client startup and BSP; these do not grant Kafka administration.

Keep the manager and TestClients, including `АдминистраторKafka` and `ПользовательKafka`, open after a scenario, run, failure or stop. Before connecting another TestClient or launching a YAxUnit client that would exceed the session limit, end only as many unnecessary TestClients owned by this contour as needed. Before starting `АдминистраторKafkaПараллельный`, check sessions and leave only the manager and two required administrative clients. Preserve diagnostics and perform scenario recovery first; verify a session actually ended before starting another. If a safe session cannot be freed, defer the launch. Reconnect a closed TestClient only when a later scenario needs it and a session is available. Closing forms or disconnecting from TestClient does not free a session. Never close other people's sessions. Perform cleanup and data restoration independently of session closure; do not start a new administrative client solely to restore connectivity after rights checks.

## Test data

For a new infobase, call `кфк_т_ТестовыеДанные.ИнициализацияДанных()` and then `кфк_т_ТестовыеДанные.ИнициализацияПользователей()`. Before initializing, using or changing prepared data, read [fixtures and initialization](.ai/FIXTURES.md), including the procedures' effects.

Scenarios may use initialized fixtures and their own items. Before a write run, define data, initial state and cleanup/restoration, including failure. Restore shared fixtures after changes and clean up scenario-owned items as designed. Do not use repeated initialization as local cleanup or a guaranteed full rollback.

## Published test reports

`reports/` publishes generated Allure UI, Allure Unit and Sonar reports through GitHub Pages; start with [reports/README.md](reports/README.md).

- Never manually edit `reports/latest/`, `reports/<run_id>-<run_attempt>/`, Allure output, Sonar output, or other generated report content.
- The publishing workflow can overwrite or delete generated directories.
- Edit only `reports/README.md`, GitHub Pages/Actions configuration, or service files when the task explicitly concerns report publication.
- Validate configuration and links without modifying generated content.
- Do not delete old runs unless the user explicitly requests the exact destructive scope.
