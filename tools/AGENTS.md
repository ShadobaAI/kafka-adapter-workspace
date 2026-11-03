# Repository Agent Instructions

Apply the mandatory [workspace rules](../WORKSPACE-RULES.md); local rules take precedence.

This repository contains CI/release scripts, Docker environments, database utilities, and the XDTO generator. Limit navigation and validation to the affected component and use its documented README or configuration.

- Use the smallest supported component check: syntax, focused tests, schema validation, or `docker compose config`.
- Start long-running infrastructure only when required, and start services or read logs only if this triggers neither a prohibited download nor a destructive state change.
- `docker compose down -v`, `prune`, volume or database deletion, restore, and equivalent destructive operations require explicit user confirmation.
- Do not read or print `.env`, tokens, passwords, or credentials. Do not disclose tracked test credentials outside this repository.
- Do not modify generated output, backups, local volumes, or runtime data unless explicitly in scope.
