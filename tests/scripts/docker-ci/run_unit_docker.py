"""Запустить YAxUnit с покрытием в одноразовой копии тестовой базы."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from create_ci_infobase import (
    ADAPTER, CI_SCRIPTS, CLIENT_IMAGE, RUNTIME_DIR, TESTS, bind, file_sha256,
    require_file, resolve_image, write_json,
)


WORKER_COMMAND = r"""
set -euo pipefail

export_results() {
    local runner_status=$?
    local copy_status=0
    shopt -s nullglob
    for path in /work/allure /work/*.log /work/exit-code.txt /work/genericCoverage.xml; do
        if [[ -e "$path" ]]; then
            cp -R -- "$path" /export/ || copy_status=1
        fi
    done
    exit "$((runner_status != 0 ? runner_status : copy_status))"
}
trap export_results EXIT

mkdir -p /work/base-unit
cp /seed/1Cv8.1CD /work/base-unit/
cp /inputs/YaxParams.json /work/
timeout -k 20s "$1" bash /inputs/run-unit-docker.sh
"""


def prepare_runner(inputs):
    source = require_file(CI_SCRIPTS / "run-unit-docker.sh")
    script = source.read_text(encoding="utf-8-sig")
    replacements = (
        ('    --db-user "Администратор"\n',
         '    --db-user "АдминистраторТакси"\n'),
        ('    --additional "/debug -http -attach /debuggerURL $coverage_debug_url"\n',
         '    --additional "/iTaxi /debug -http -attach /debuggerURL $coverage_debug_url"\n'),
    )
    for original, taxi in replacements:
        if script.count(original) + script.count(taxi) != 1:
            raise ValueError(f"Не удалось подтвердить параметры запуска в Такси: {source}")
        script = script.replace(original, taxi)
    (inputs / source.name).write_text(script, encoding="utf-8", newline="\n")
    shutil.copyfile(require_file(TESTS / "unit" / "unit" / "YaxParams.json"), inputs / "YaxParams.json")


def validate_results(output):
    allure_path = output / "allure"
    coverage_path = output / "genericCoverage.xml"
    python = [sys.executable, "-B", "-X", "utf8"]
    with (output / "validation.log").open("wb") as log:
        allure = subprocess.run(
            [*python, str(CI_SCRIPTS / "validate_allure_report.py"), "--results-dir", str(allure_path)],
            stdout=log, stderr=subprocess.STDOUT,
        ).returncode
        coverage = subprocess.run(
            [*python, str(CI_SCRIPTS / "validate_coverage_report.py"), str(coverage_path)],
            stdout=log, stderr=subprocess.STDOUT,
        ).returncode
    if coverage == 0:
        destination = output / "coverage"
        destination.mkdir()
        coverage_path.rename(destination / coverage_path.name)
    return allure, coverage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="путь к подготовленной 1Cv8.1CD")
    parser.add_argument("--image", help="образ клиента, по умолчанию из base.json")
    parser.add_argument("--hostname", help="имя сервера для запуска ранее подготовленной копии")
    parser.add_argument("--timeout", type=int, default=3600, help="секунд на прогон")
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout должен быть положительным")

    base = require_file(args.base.resolve())
    base_hash = file_sha256(base)
    manifest = base.with_name("base.json")
    build = json.loads(manifest.read_text(encoding="utf-8-sig")) if manifest.is_file() else {}
    if build.get("sha256") and build["sha256"] != base_hash:
        raise ValueError(f"Контрольная сумма 1Cv8.1CD отличается от {manifest}")

    runs = RUNTIME_DIR / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="unit-", dir=runs))
    inputs = root / "inputs"
    output = root / "results" / "test-results-1-unit"
    inputs.mkdir()
    output.mkdir(parents=True)
    prepare_runner(inputs)

    container = f"kafka-{root.name}"
    image = resolve_image(args.image or build.get("client_image") or CLIENT_IMAGE, root)
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    write_json(root / "run.json", dict(
        base=str(base), base_sha256=base_hash, image=image, hostname=args.hostname,
        runner_sha256=file_sha256(inputs / "run-unit-docker.sh"),
        yaxparams_sha256=file_sha256(inputs / "YaxParams.json"), started_at=started,
    ))
    print(json.dumps(dict(root=str(root), container=container), ensure_ascii=False), flush=True)

    command = ["docker", "run", "--rm", "--init", "--name", container]
    if args.hostname:
        command.extend(["--hostname", args.hostname])
    command.extend([
        *bind(base, "/seed/1Cv8.1CD"), *bind(inputs, "/inputs"),
        *bind(output, "/export", readonly=False), *bind(ADAPTER, "/coverage-project"),
        "-e", "COVERAGE_PROJECT_DIR=/coverage-project", "-w", "/work", image,
        "bash", "-ec", WORKER_COMMAND, "--", str(args.timeout),
    ])
    with (output / "runner.log").open("wb") as log:
        runner = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
    allure, coverage = validate_results(output)
    exit_code = output / "exit-code.txt"
    test_exit = exit_code.read_text(encoding="utf-8-sig").strip() if exit_code.is_file() else None
    passed = runner == allure == coverage == 0 and test_exit == "0"
    write_json(output / "unit-result.json", dict(
        runner=runner, test_exit=test_exit, allure=allure, coverage=coverage,
        result="passed" if passed else "failed",
        finished_at=datetime.now().astimezone().isoformat(timespec="seconds"),
    ))
    return int(not passed)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
