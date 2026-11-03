# Repository Agent Instructions

Read the mandatory [workspace rules](../../WORKSPACE-RULES.md); if they are missing, report a workspace-layout error and stop. Local rules take precedence. This repository publishes generated Allure UI, Allure Unit and Sonar reports through GitHub Pages; start with [README.md](README.md).

- Never manually edit `latest/`, `<run_id>-<run_attempt>/`, Allure output, Sonar output, or other generated report content.
- The publishing workflow can overwrite or delete generated directories.
- Edit only `README.md`, GitHub Pages/Actions configuration, or service files when the task explicitly concerns report publication.
- Validate configuration and links without modifying generated content.
- Do not delete old runs unless the user explicitly requests the exact destructive scope.
