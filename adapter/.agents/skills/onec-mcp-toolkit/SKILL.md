---
name: onec-mcp-toolkit
description: Diagnose a running 1C infobase with MCP Toolkit. Use for 1C queries, deployed metadata, the 1C event log, object links and references, runtime role rights, installed BSL help, and Toolkit client or session operations. Correlate with SQL Server or Elasticsearch when the task needs evidence from them.
---

# 1C MCP Toolkit

Use the `onec-mcp-toolkit` server in the [adapter Codex configuration](../../../.codex/config.toml). Match the Toolkit session's infobase and client or server context to the task before accessing its data or UI. Use tools advertised by the current MCP connection and their live schemas. If discovery changes on the server, reconnect and use the refreshed catalog.

## Choose the evidence source

| Fact to establish | Route |
| --- | --- |
| Data, deployed metadata, roles, or registration log in the connected infobase | `onec-mcp-toolkit` |
| Project source and references, live EDT model and diagnostics, platform API compatibility, standards, or persistent 1C changes | Assigned 1C AI Core authorities under [1C-RULES.md](../../../../1C-RULES.md) |
| SQL Server storage, database metrics, or data exposed by the SQL service | `mssql`, scoped to the identified database. For entity tools, use targeted `describe_entities` when the entity is known. |
| Indexed application or infrastructure events and aggregations | `elasticsearch`, scoped to the index and time range |

For cross-system diagnosis, start where the symptom is recorded. Carry a confirmed correlation ID, session number, object link, or narrow time window with its time zone to the next source only when needed. Treat deployed metadata and the EDT model as facts about their respective environments.

## Keep calls focused

- Reuse established health, metadata, and results while their scope stays valid. For a connection check, use the native MCP catalog. A read-only backend smoke test is `execute_query` with `ВЫБРАТЬ 1 КАК Проверка` and `limit: 1`.
- Use `get_metadata` with `filter` for an exact object or field. Set `extension_name` for a named deployed extension. For discovery, constrain `meta_type`, `name_mask` or `attribute_mask`, and `limit`. Request detail `sections` only as needed.
- Use `execute_query` for 1C query language against the infobase. Confirm unfamiliar tables and fields via targeted metadata, bind values with `params`, select needed columns, and filter or aggregate at the source. Start with a small `limit`. Request `include_schema` when column types matter.
- Use `get_event_log` with a short `start_date` to `end_date` window, relevant `levels` or other known filters, and a small `limit`. For the next page, carry `last_date` into `start_date` and `next_same_second_offset` into `same_second_offset`.
- Follow an existing navigation link with `get_object_by_link`. Generate one with `get_link_of_object` from the reference returned by a query. For actual references in stored data, use `find_references_to_object` with specific `search_scope`, `meta_filter`, hit limits, and a bounded time budget.
- Use `get_access_rights` with an exact `metadata_object` and relevant `rights_filter` or `roles_filter`. A requested user's `effective_rights` reflects the union of their roles and excludes row-level and context restrictions.
- Use `get_bsl_syntax_help` for documentation bundled with the Toolkit platform installation. Start with precise `keywords` and a small `limit`, then request the full breadcrumb of the relevant candidate. Use the EDT route for API compatibility with the project.
- Read both the MCP error indicator and the Toolkit `success` field. Interpret `data` as returned, including compact TOON text. Page or widen only to resolve an outstanding question. In SQL and ELK, project needed fields and apply time filters, server-side aggregation, and small row or hit limits.

For `execute_code`, `get_screenshot`, `submit_for_deanonymization`, `restart_1c_session`, and `close_1c_session`, read [Client and session operations](references/client-and-session.md) when the task calls for one of them.
