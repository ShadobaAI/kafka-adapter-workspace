# Data Conversion context

The profile covers two EDT projects:

- [KFK](../KFK/README.md) is the Kafka Adapter extension for 1C:Data Conversion 3.1. It adapts exchange module generation for arbitrary XDTO packages and does not implement Kafka transport.
- `КД` is the external 1C:Data Conversion 3.1 base configuration used to develop and validate the extension, analogous to the adapter's development base. It is outside the KFK Git repository and may be changed only when explicitly in scope.

The extension adopts some supplier objects and adds adapter-owned objects. The KFK README states a compatibility line of Data Conversion 3.1+, while the currently documented attachment covers only one local base version. When the base is updated, check adopted objects, form data paths and end-to-end contract generation. Exact supplier ownership, maintenance and modification marking rules, and authorized test environments must be established before dependent work.

Repository paths, EDT names, index aliases and knowledge mode are in [project.yaml](project.yaml); working rules are in [AGENTS.md](../AGENTS.md). The optional OpenViking collection is intended for [adapter documentation](../../adapter/adapter/docs/); its service lifecycle and updates are managed separately. A configured collection does not establish publication or search readiness.
