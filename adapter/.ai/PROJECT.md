# Kafka Adapter context

The profile root contains three independent repositories:

- [adapter](../adapter/README.md): the Kafka Adapter product extension and library, with maintained product documentation in `adapter/docs`.
- [base](../base/README.md): a BSP-based host configuration for development and testing in extension mode.
- [examples](../examples/README.md): a development-only extension with API examples and integration scenarios; it is not a production artifact.

The adapter provides bidirectional exchange between 1C:Enterprise and Apache Kafka using the Simple Kafka Connector 1C external component. The product README specifies platform 8.3.26+, compatibility mode 8.3.21 and BSP 3.1.10+; verify applicability to the task and target environment. Current 1C sources and tests are the primary evidence for behavior; maintained documentation describes the product contract unless it conflicts with them.

OpenViking is the optional, preferred knowledge source for [adapter documentation](../adapter/docs/). Its service lifecycle and document updates are managed separately. A local documentation path does not establish the server collection, publication or search readiness.

Repository paths, index aliases, EDT project names and knowledge mode are in [project.yaml](project.yaml); working rules and authority boundaries are in [AGENTS.md](../AGENTS.md). Rules for modifying and marking supplier code, ownership of individual objects, and permitted test environments are not established here: determine them from applicable instructions and task context before dependent work.
