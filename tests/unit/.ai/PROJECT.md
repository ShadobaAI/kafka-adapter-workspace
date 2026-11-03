# Kafka Adapter unit tests

The unit-test EDT workspace combines four separately maintained areas:

| Area | Ownership and update route |
| --- | --- |
| `unit/` | Kafka Adapter test extension; test selection and execution are documented in [its README](../unit/README.md). |
| `base/` | Configuration assembled from `adapter/base` and `adapter/adapter` by the scripts in [unit/scripts](../unit/scripts/). Edit the originals through the adapter project. Assembly replaces managed output entries; do not run it as an incidental setup action. |
| `examples/` | Checkout of `adapter/examples`; update through Git after changes to the original. |
| `yaxunit/` | Upstream YAxUnit checkout; the framework EDT project is under `yaxunit/exts/yaxunit`. Scoped, justified changes may remain uncommitted. |

The [profile](project.yaml) maps the test repository and framework checkout to `kfk-unit` and `kfk-yaxunit`, respectively. For `base`, reuse the canonical `kfk-base` and `kfk` indexes; for `examples`, reuse `kfk-examples`. These are supplementary read-only indexes and do not select a different EDT workspace. The current plugin profile format binds one index alias to each repository path and cannot represent the two external canonical indexes for the assembled base or reuse the external examples index for a different checkout path. The two copied projects are therefore not declared as profile repositories; their source paths remain protected. Do not treat them as mapped until a supported binding is verified.

The profile enables YAxUnit with the documented EDT launch configuration `base Тонкий клиент`. `unit/allure` follows the `allure` report name in [YaxParams.json](../unit/YaxParams.json); verify the actual output location for the selected runner before relying on it. The runtime and test database are external prerequisites.

The optional OpenViking collection `kafka-adapter-docs` is intended for adapter documentation and is preferred when ready. The server, indexing, publication and access are managed outside this profile. The profile also uses v8std for standards. No source readiness is assumed from configuration alone.
