# Client and session operations

Check the live tool schema, target infobase, and server or client mode. Use the workspace [failure and authorization rules](../../../../../WORKSPACE-RULES.md) for high-impact actions.

| Tool | When and how |
| --- | --- |
| `execute_code` | Use a narrowly scoped BSL fragment when the task explicitly authorizes evaluation and a dedicated read tool is insufficient. Set `execution_context` to `server` for server-side work or `client` for a supported open-client task. Return the minimum required data through `Результат`. Confirm authorization for any writes or other effects of the exact fragment. |
| `get_screenshot` | Use for requested visual evidence from the Toolkit's Windows 1C client. Capture the current window or specify one `form_name` or object `link`. Opening or activating a form and selecting `page_name` affect the client UI. Prefer a relevant `region` and reduced `scale_percent` when legible. Check `capture_complete` before drawing conclusions about overlays. |
| `submit_for_deanonymization` | When the live catalog advertises this tool and the authorized final response contains Toolkit tokens, submit that text once to the attached 1C client through `text`. The tool acknowledges receipt and displays restored values to the user in 1C. Keep the original tokens in the chat response. |
| `restart_1c_session` | With authorization to restart the connected Toolkit session, call once. After it returns, reconnect to MCP and re-establish the infobase and needed capabilities before continuing. |
| `close_1c_session` | With authorization to end the connected Toolkit session, call once. It returns a launcher command for a later session. Treat the launcher response as sensitive data. A relaunch requires an authorized, verified launcher and target. |

After a timeout during a state-changing operation, verify its outcome before any further action. If a tool is absent, check the applicable Toolkit mode and tool settings when the capability is needed. Screenshots and client operations depend on an open client. De-anonymization also depends on enabled anonymization.

For version-specific behavior, consult the relevant tool section in `README_FULL.md` of the Toolkit repository.
