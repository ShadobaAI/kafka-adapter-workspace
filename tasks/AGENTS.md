# Repository Agent Instructions

Apply the mandatory [workspace rules](../WORKSPACE-RULES.md); local rules take precedence.

This repository owns task tracking, SDD specifications, and architecture decisions; it does not own product source.

- Store SDDs under `sdd/` and ADRs under `adr/`; preserve stable IDs and history during moves or index maintenance. Write SDDs in Russian, preserving technical identifiers, commands and paths.
- Keep migration and audit reports bounded to their task; do not recreate a general-purpose central knowledge base.
- Do not store raw MCP output, secrets, absolute workspace paths, personal configuration, or reasoning logs.
- Changes to product documentation or source require explicit multi-repository scope in an approved SDD.
- Keep only bounded active handoffs under `work/`, one per Issue or approved SDD workstream. Record committed revisions, completed work, decisions, remaining actions and verification gaps; do not use it as a general-purpose Memory Bank. At completion, promote durable conclusions to the SDD, ADR or owning documentation and remove the handoff; Git history supplies the audit trail.
- After implementation, update the owning repository documentation for any changed current behavior, contract, or instruction in addition to recording the SDD result.
