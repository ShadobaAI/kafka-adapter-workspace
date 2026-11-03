# Kafka Adapter test workspace

The [shared profile](project.yaml) covers Vanessa UI scenarios in `ui/` and the unit-test EDT workspace on port `8768`. The UI repository owns its Gherkin scenarios and test configuration; it is not shipped to production. Setup and focused UI commands are in the [UI README](../ui/README.md), and unit test selection and execution are in the [unit README](../unit/unit/README.md).

| Area | Ownership and update route |
| --- | --- |
| `unit/unit` | Kafka Adapter test extension. |
| `unit/base` | Configuration assembled from `adapter/base` and `adapter/adapter` by the scripts in `unit/unit/scripts`. Edit the originals through the adapter project. Assembly replaces managed output entries; do not run it as an incidental setup action. |
| `unit/examples` | Checkout of `adapter/examples`; update through Git after changes to the original. |
| `unit/yaxunit` | Upstream YAxUnit checkout; the framework EDT project is under `unit/yaxunit/exts/yaxunit`. Scoped, justified changes may remain uncommitted. |

The profile maps the four test EDT projects and their own indexes: `kfk-test-base`, `kfk-test-examples`, `kfk-unit` and `kfk-yaxunit`. The UI repository has its own `kfk-ui` alias but no EDT project. Index selection does not change the assigned EDT workspace; declared mappings alone do not establish service or project readiness.

The profile enables YAxUnit with the EDT launch configuration `base Тонкий клиент`. `unit/unit/allure` follows the `allure` report name in [YaxParams.json](../unit/unit/YaxParams.json); verify the actual output location for the selected runner. Vanessa uses `ui/.vanessa/profile.json`, `ui/features`, `ui/.vanessa/results`, and the `vanessa` MCP server configured in `tests/.codex/config.toml`; runtime settings and results are local, and `ui/VAParams.json` is the separate CI configuration. Configure the Vanessa manager and TestClients to use the same prepared test infobase as the unit contour; the AI profile does not configure or verify that database connection.

The optional OpenViking collection `kafka-adapter-docs` is preferred for adapter documentation when ready. Its server, indexing, publication and access are externally managed. The profile also uses v8std for standards. No connection, knowledge coverage or test environment readiness is assumed from configuration alone. Scenario, session, data and restoration rules are in [AGENTS.md](../AGENTS.md); initialization effects and fixtures are in [FIXTURES.md](FIXTURES.md).
