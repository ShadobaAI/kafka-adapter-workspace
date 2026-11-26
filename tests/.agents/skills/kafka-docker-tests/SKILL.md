---
name: kafka-docker-tests
description: Build or reuse the Kafka Adapter test infobase (1Cv8.1CD) and run Vanessa UI or YAxUnit tests in Docker with Allure and Coverage41C. Use in the Kafka Adapter test workspace.
---

# Kafka Adapter tests in Docker

Run the PowerShell commands from the `tests` directory of the Kafka Adapter workspace. Follow the project's `AGENTS.md` and the workspace root's `WORKSPACE-RULES.md` and `1C-RULES.md`. Docker Desktop must be running in Linux container mode. The build and test runs use the CI configuration in `../adapter/adapter/.github`. Docker uses the Vanessa Single EPF from the release, as CI does. Interactive runs use the built-in data processor and the `ui/.vanessa/profile.json` profile.

Use the local runners below. Both start 1C as `АдминистраторТакси` with `/iTaxi` and keep the CI coverage arguments. UI scenarios supply `/iTaxi` for their TestClients. Set UI concurrency according to the available Docker memory, including any concurrent Unit run.

## Prepare the infobase

Reuse an existing `1Cv8.1CD` when you need the same configuration and fixture versions. To create an infobase, the script uses an existing CF-XML export in `.local/base_xml` with `Configuration.xml` at its root. The configuration already includes the adapter.

Before **every** infobase build with `create_ci_infobase.py`, remind the user that `tests/.local/base_xml` is an export of the `base` configuration from the `unit` infobase. Ask whether the export is up to date for this build. Pass `yes` to the script's standard input for that run only after the user explicitly confirms in chat. When running the script manually, the user enters `да` or `yes` in the terminal.

```powershell
$tools = Join-Path $PWD 'scripts\docker-ci'
$base = python -X utf8 "$tools\create_ci_infobase.py" | ConvertFrom-Json
$base.base
```

To reuse a build, load `$base` from its `base.json` using `Get-Content -Raw -Encoding UTF8` and `ConvertFrom-Json`. The default build directory is `.local/docker-ci/bases`.

The script obtains the DT file and extensions from the release CI sources. For GHCR, it uses ORAS and existing Docker authentication. To use local files, pass `--assets` with the path to a directory containing `kfk-tmpl-test.dt`, `kafka-adapter-examples.cfe`, `unit/YAXUNIT.cfe`, `unit/unit.cfe` (or `unit/output/unit.cfe`), and `ui/VAExtension.cfe`. You can also place `ui/vanessa-automation-single.epf` there for UI runs.

In `base.json`, `base_xml` identifies the source directory, and `inputs.base_xml` contains the SHA-256 digest of the relative paths and file contents of the loaded copy. Check `create-infobase.log` and `fill-infobase.log` in `$base.root`. Work with test data on fresh infobase instances and follow `.ai/FIXTURES.md`.

## Run the selected UI scenarios

In the example below, `incoming` and `outgoing` each get a dedicated container and a copy of the infobase. For the panel group, use `--parallel 1 panel`. Use `--list-groups` to list the available groups.

```powershell
$run = python -X utf8 "$tools\run_ui_docker.py" --base $base.base --parallel 2 incoming outgoing | ConvertFrom-Json
$run.root
```

`--feature` accepts a path relative to `ui/features` or a filename within one group. Repeat `--feature` to select multiple files. `--scenario` filters a single group by exact scenario title and preserves `Контекст` and data variants in the working copy of the feature file. The script takes a snapshot of modified and new files in the `ui` working tree, including `libraries`. For an infobase with a `base.json` file, the script uses the image and EPF from the build. For a standalone `1Cv8.1CD`, you can explicitly pass `--image` and either `--epf` or `--vanessa-tag`. The script runs UI tests directly against the prepared infobase and skips unit tests.

## Run Unit tests

Use an infobase with the required Unit extension revision. The runner uses `unit/unit/YaxParams.json` for the CI test selection.

```powershell
$run = python -X utf8 "$tools\run_unit_docker.py" --base $base.base | ConvertFrom-Json
$run.root
```

For a seed tied to a previous server name, pass its known name with `--hostname` to keep the connection identity in the disposable container. The runner prints its output directory and waits. Read `results/test-results-1-unit/unit-result.json` for completion, `allure/` for test statuses, and `coverage/genericCoverage.xml` for validated coverage. If the run stalls during startup, verify the active 1C process has `/iTaxi` and check for a startup dialog before restarting.

## Wait for the result

- Read `overnight-status.json` until `phase = finished`, then check `result` and the group results. Use `--wait` to wait for the result and get the exit code in a single invocation. For background runs, `viewer-url.txt` contains the URL for progress and Allure.
- `groups.json` maps zero-based indices to groups. Look in `results/test-results-1-ui-<index>/` for `group-result.json`, `runner.log`, `1cv8c.log`, `allure/`, and attachments. `local-source.json` links the results to the hashes of the files used in the run. The combined report is in `allure-ui-report/`.
- Diagnose startup problems using the container logs and `exit-code.txt`. Use Allure to investigate problems with individual steps. To verify a focused run, check the scenario name and status against the raw Allure result.
- The build, tests, and report generation use `docker run --rm`. The working copies are inside disposable containers. Docker removes the containers and their anonymous volumes when they exit. Use `docker ps -a` to look for run containers with the prefix `kafka-ui-<run-directory-name>-`. Run diagnostics and reports are saved in `.local/docker-ci/runs`.
