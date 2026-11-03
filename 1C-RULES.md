# 1C Rules

## 1C Routing and Source Integrity

- New adapter-owned objects use `кфк`; new `examples` objects use `кфк_т_`.
  YAxUnit test modules are exempt from the project prefix; apply `yaxunit:patterns:naming`.

| Scope | EDT workspace | Port | Configuration owner |
|---|---|---:|---|
| `adapter/{adapter,base,examples}` | adapter | `8765` | `adapter/.ai/project.yaml` |
| `conversion/{KFK,КД}` | conversion | `8767` | `conversion/.ai/project.yaml` |
| `tests/unit/{base,examples,unit,yaxunit}` | unit | `8768` | `tests/.ai/project.yaml` |

The adapter, conversion and unit EDT workspaces use distinct fixed ports, respectively `8765`, `8767` and `8768`, so they can run concurrently. These are workspace names, not MCP tool names: use the `edt` relay bound to the corresponding 1C AI Core profile. The conversion and testing profile settings, including the `conversion/КД` route, are owned by the respective `conversion` and `tests` profile roots. The server configured inside each EDT workspace and its Codex client URL must use the same assigned port.

The workspace uses these explicit code-index bindings:

| Project scope | code-index alias | Binding |
|---|---|---|
| `adapter/adapter` | `kfk` | Index only the canonical `adapter/adapter` checkout. |
| `adapter/base` | `kfk-base` | Index only the canonical `adapter/base` checkout. |
| `adapter/examples` | `kfk-examples` | Index only the canonical `adapter/examples` checkout. |
| `conversion/KFK` | `kfk-conv` | Index the Conversion Data extension checkout. |
| `conversion/КД` | `kfk-conv-kd` | Index the supporting Conversion Data base project. |
| `tests/unit/base` | `kfk-test-base` | Index the assembled test base separately. |
| `tests/unit/examples` | `kfk-test-examples` | Index this test checkout separately. |
| `tests/unit/unit` | `kfk-unit` | Index only this repository checkout. |
| `tests/unit/yaxunit` | `kfk-yaxunit` | Index only this upstream repository checkout. |

Code-index selection never selects an EDT server. Reused aliases are supplementary read-only evidence only; authoritative live state, platform documentation, diagnostics, and every persistent 1C mutation must use the EDT-MCP assigned to the current project scope.

- Use `$1c-routing` only when the request concerns work with a concrete 1C project or a general question about 1C. Do not load it for unrelated repository, tooling, Git, documentation, or engineering requests merely because the workspace contains 1C.
- Use the assigned EDT-MCP as the source of truth for the live EDT model, 1C source and metadata, platform-aware navigation, every persistent mutation, and primary diagnostics.
- Never access configuration or extension source trees under `src/**` directly through filesystem, shell, generic file, or patch tools. This prohibition includes list, find, glob, grep, read, parse, write, move, rename, and delete operations.
- Access 1C project source only through the assigned EDT-MCP or explicitly allowed read-only `code-index`/BSL LS MCP tools. Perform every change through EDT-MCP; never text-patch `.bsl`, `.mdo`, `.form`, `.rights`, DCS, XDTO, or other serialized 1C model files.
- Prefer the shared `code-index` MCP over EDT for read-only project information, search, and analysis when the indexed route is appropriate. Use it for indexed discovery, source and metadata structure, call/data graphs, references, and impact analysis. Bind the exact repository alias; the managed proxy must confirm daemon health and that exact path is `ready` before forwarding corpus-dependent calls. A stale, incomplete, or not-ready index stops the indexed workflow and is never a reason to repeat the same discovery through EDT.
- For BSL call graphs, use `get_callers_bsl`, `get_callees_bsl`, `get_call_tree_bsl`, or `find_path_bsl`; the universal call tools expose the less precise core graph. A zero-edge result covers only indexed static calls and does not exclude dynamic string/reflection dispatch.
- Use existing structured batch capabilities before generic SQL: `get_function.names`, `get_class.names`, and `get_object_structure.full_names` or `name_like` plus `meta_type`. For outlines, test ownership, conventions, and related symbols, compose the narrowest existing structured/search/graph calls at the orchestration layer; use `bsl_sql` only when no named operation can answer the concrete question.
- Use repository-local BSL LS only for focused BSL diagnostics and semantic navigation when that MCP is explicitly configured. It does not replace EDT diagnostics, metadata, platform documentation, or tests.
- The `bsl-indexer` daemon may write only its own `.code-index/` data in configured repository roots and coordination/runtime files under managed `CODE_INDEX_HOME`; do not expose daemon/index mutation commands through MCP.
- `CODE_INDEX_HOME` and its daemon are shared across registered workspaces. Kafka
  installation may replace only its managed `kfk*` aliases; it must preserve all
  other `[[paths]]` entries and existing daemon settings.
- Keep the shared user-level `v8std`/`code-index` block independent from the
  Kafka routing guard so another workspace installer cannot remove Kafka policy.
- Use the MCP named `v8std` as the primary standards/policy corpus. Its endpoint is user-owned configuration: the default local endpoint is `http://127.0.0.1:8766/mcp`, and the user may replace its `url`. Do not apply agent-side source classification, endpoint switching, or code-transfer restrictions beyond the configured MCP.
- Before choosing a 1C design, judging compliance or applying a change, select applicable artifact, operation and mechanism requirements from `v8std`: `$1c-standards` for design/normative analysis, `$1c-code-change` for changes. Verify the proposal and result against that same selection; missing evidence or unresolved mandatory requirements block the dependent outcome. Pure source discovery needs no normative preload.
- Additional work policy is stored separately from the original v8std corpus in the private `corporate` collection under stable `corporate:work:*` IDs. Apply precedence: explicit user and project constraints, mandatory work rules, recommended work rules, general 1C standards, advisory material.
- Apply BSL requirements only to new or changed code. Do not mass-format or otherwise modernize unrelated legacy code unless the task requires it.
- Reuse the pre-mutation requirements as the post-mutation review contract; do not replace that validation with a fresh best-effort search.
- Before introducing standalone reusable 1C behavior, apply the reuse-gate in $1c-code-change/$1c-code-index. Trivial local glue is exempt; discovery in a dependency never authorizes editing it. Non-1C work uses its own language/repository workflow without 1C overhead.
- For platform APIs and version-specific semantics, use EDT `get_platform_documentation` with `projectName`; use content assist and EDT validation when needed.
- Before a 1C mutation, capture focused EDT diagnostics for the affected objects when the current EDT API can return them; after the mutation, run the same focused diagnostics and compare findings by code, message, project/object, and location. Classify findings as new, pre-existing, resolved, proven false positive, infrastructure, or indeterminate. A failed or incomplete required baseline stops mutation; infrastructure or indeterminate post-validation that makes the result unreliable blocks completion.
- When EDT source reads return a source hash or version, retain it as the concurrency token. Pass it to mutation when the live tool guide exposes an expected-hash/version parameter. Without atomic compare-and-write, a local reread can detect many lost updates but cannot close the race; do not claim strict optimistic concurrency, and stop high-risk mutation that requires it.
- Prefer native method/region/fragment mutation when the assigned EDT toolset exposes it. Do not emulate a missing structural mutation by filesystem editing or fragile text surgery over a whole serialized module.
- After every 1C mutation, run focused EDT diagnostics for the affected objects and inspect the resulting findings.
- Do not disable, suppress, filter out, or hide EDT diagnostics.
- Do not treat an EDT finding as a confirmed defect until it is verified against the current source and metadata context.
- Leave a finding unfixed only when evidence supports classifying it as a false positive; otherwise keep it unresolved. Report its code, message, location, classification, and evidence. code-index, BSL LS, platform documentation, content assist, standards, and focused tests may corroborate the classification but never replace EDT diagnostics.
- If EDT and code-index/BSL LS disagree about live project state, EDT remains the designated live authority, but the conflicting indexed/analyzer route is invalid for the rest of the task until its health and freshness are re-established. If two required authoritative results for the same fact conflict, stop instead of choosing one. Use EDT `resync_to_disk` only when model-to-disk reconciliation is actually required. Never run `clean_project` automatically after an EDT mutation.
- Keep EDT raw `git` and `ask_workmate` disabled. Treat database updates, destructive metadata/project operations, imports, credential changes, runtime variable changes, branch switching, and evaluation as explicit-context high-risk operations.
- Check availability only for the project MCPs required by the selected route. If a required assigned EDT-MCP, `code-index`, `v8std`, or repository BSL LS endpoint, project, alias, or root is unavailable, report an explicit error and stop the MCP-dependent work. Do not substitute another MCP, workspace, filesystem/shell access, copied source, or model memory, and do not block work on an MCP that the task does not require.
- For unknown or version-sensitive EDT tool semantics, use `get_tool_guide` instead of guessing. Enable only the EDT toolset required for the task; progressive disclosure is context control, not authorization.
- Run existing relevant tests when their runner is available. Do not create tests merely because coverage is absent or the change is important; create them only when requested or required by project policy. Run additional tests only when required by the local repository instructions or the changed behavior.
- For YaXUnit authoring, establish observable behavior, test owner, client/server context, data and isolation strategy, mock boundary, assertion strategy, existing fixtures, and applicable `yaxunit` requirements before mutation. Use `$yaxunit-tests` for registration and fluent-formatting checks. Prefer public `ЮТест.Данные()` builders for new data and mock only an external boundary, never the behavior under test.
