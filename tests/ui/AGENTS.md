# Kafka Adapter UI tests

Apply the mandatory [workspace rules](../../WORKSPACE-RULES.md) and [project context](.ai/PROJECT.md); local rules below take precedence. The repository owns Vanessa Automation scenarios and test configuration. Current scenarios and run results are evidence of test behavior.

## Profile and authorities

- EDT, code-index and v8std are mandatory for 1C-dependent work; stop if a required service or exact adapter mapping is not ready. Use the adapter EDT and its canonical indexes; `kfk-ui` identifies the test repository and is not an adapter index. Do not duplicate adapter indexes.
- OpenViking is optional and preferred for adapter documentation when ready; its lifecycle and publication are external. It does not replace EDT or v8std.
- Before introducing reusable behavior, check existing facilities and justify the solution's complexity in design and review. Do not change product repositories without explicit multi-repository scope.

## Scenarios

- Edit feature files and other non-1C test configuration directly in UTF-8; preserve Gherkin language, names, indentation, fixtures and scenario style.
- Use `$vanessa-ui-tests` and `.vanessa/profile.json` to research, record, edit, run or debug UI scenarios. Always use the built-in data processor at `/URL e1cib/app/Обработка.VanessaAutomationsingle`.
- Run only affected features or scenarios with documented commands when the environment is available.
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

Keep the manager and TestClients, including `АдминистраторKafka` and `ПользовательKafka`, open after a scenario, run, failure or stop. End an active TestClient only before connecting one that would cause a fourth session. Before starting `АдминистраторKafkaПараллельный`, check sessions and end unnecessary TestClients in this contour so only the manager and two required administrative clients remain. Preserve diagnostics and perform scenario recovery first; verify the session actually ended before connecting another. Closing forms or disconnecting from TestClient does not free a session. Never close other people's sessions. Perform cleanup and data restoration independently of session closure; do not start a new administrative client solely to restore connectivity after rights checks.

## Test data

For a new infobase, call `кфк_т_ТестовыеДанные.ИнициализацияДанных()` and then `кфк_т_ТестовыеДанные.ИнициализацияПользователей()`. Before initializing, using or changing prepared data, read [fixtures and initialization](.ai/FIXTURES.md), including the procedures' effects.

Scenarios may use initialized fixtures and their own items. Before a write run, define data, initial state and cleanup/restoration, including failure. Restore shared fixtures after changes and clean up scenario-owned items as designed. Do not use repeated initialization as local cleanup or a guaranteed full rollback.
