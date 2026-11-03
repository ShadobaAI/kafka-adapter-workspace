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

- Edit feature files and other non-1C test configuration directly in UTF-8; preserve Gherkin language, names, indentation, fixtures and scenario style. Use `$vanessa-ui-tests` for UI scenarios; runtime operations use `ui/.vanessa/profile.json`, while static design, review and authoring do not require it. Always use the built-in data processor at `/URL e1cib/app/Обработка.VanessaAutomationsingle`.
- Run only affected features or scenarios with documented commands when the environment is available. Run relevant adapter scenarios covering a change when available.
- For all `кфкПродюсеры` and `кфкКонсьюмеры` tests, cover both catalog items and groups (task dispatchers). Check applicable operations, saved state and permissions separately; derive group expectations from its own form and commands. Create scenario-owned dispatchers for write tests and restore them on failure; do not modify prepared `Диспетчер задач` groups as local cleanup.

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
