"""Run selected local Vanessa tests in isolated adapter CI containers."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from html import escape
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from threading import Thread
import time
from urllib.parse import urlsplit

from create_ci_infobase import (
    ADAPTER, CI_SCRIPTS, CLIENT_IMAGE, RUNTIME_DIR, TESTS, VANESSA_EPF, VANESSA_REPO, bind,
    download_vanessa, file_sha256, get_release, require_file, resolve_image, run_logged, write_json,
)


UI = TESTS / "ui"
ALIASES = {
    "incoming": "РегистрыСведений/ВходящиеСообщения",
    "outgoing": "РегистрыСведений/ИсходящиеСообщения",
    "panel": "Обработки/ПанельАдминистрирования",
}
SCENARIO_HEADINGS = {"сценарий", "пример", "структура сценария", "шаблон сценария",
                     "scenario", "example", "scenario outline", "scenario template"}
OTHER_HEADINGS = {"функциональность", "правило", "контекст", "переменные", "feature", "rule", "background"}
# Inherit the client image's locale, as in release CI.
WORKER_COMMAND = r"""
set -euo pipefail

export_results() {
    local rc=$?
    local copy_rc=0
    shopt -s nullglob
    for path in /work/allure /work/screen /work/*.log /work/exit-code.txt /work/genericCoverage.xml; do
        if [[ -e "$path" ]]; then
            cp -R -- "$path" /export/ || copy_rc=1
        fi
    done
    exit "$((rc != 0 ? rc : copy_rc))"
}
trap export_results EXIT

mkdir -p /work/base-ui "/work/features/${1%%/*}"
cp /seed/1Cv8.1CD /work/base-ui/
cp /vendor/vanessa-automation-single.epf /work/
cp -R /inputs/libraries /inputs/VAParams.json /work/
cp -R -- "/inputs/features/$1" "/work/features/${1%%/*}/"
timeout -k 20s "$2" bash /inputs/run-ui-docker.sh
"""


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git(*args):
    return subprocess.check_output(["git", "-C", str(UI), *args])


def ui_files(paths):
    names = git("ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", *paths)
    files = sorted({name.decode("utf-8") for name in names.split(b"\0") if name})
    return [name for name in files if (UI / name).is_file()]


def list_groups(files):
    return sorted({"/".join(PurePosixPath(name).parts[1:3]) for name in files
                   if name.endswith(".feature") and len(PurePosixPath(name).parts) >= 4})


def select_groups(args):
    groups = [ALIASES.get(name, name.replace("\\", "/")) for name in args.groups]
    if len(set(groups)) != len(groups):
        raise ValueError("Укажите каждую группу один раз")
    for group in groups:
        if len(group.split("/")) != 2 or any(part in ("", ".", "..") for part in group.split("/")):
            raise ValueError(f"Ожидалась группа раздел/объект: {group}")
    return groups


def feature_paths(names, groups):
    paths = []
    for name in names:
        name = name.replace("\\", "/").removeprefix("features/")
        if "/" not in name and len(groups) == 1:
            name = f"{groups[0]}/{name}"
        path = PurePosixPath(name)
        if (path.suffix != ".feature" or path.is_absolute() or ".." in path.parts
                or "/".join(path.parts[:2]) not in groups or len(path.parts) < 3):
            raise ValueError(f"Укажите .feature внутри выбранной группы: {name}")
        paths.append("features/" + path.as_posix())
    return sorted(set(paths))


def scenario_blocks(lines):
    sections = []
    fence = None
    for index, line in enumerate(lines):
        line = line.lstrip("\ufeff").strip()
        if fence:
            if line == fence:
                fence = None
        elif line.startswith(('"""', '```')):
            fence = line[:3]
        else:
            heading, sep, title = line.partition(":")
            heading = heading.casefold()
            if not sep or heading not in SCENARIO_HEADINGS | OTHER_HEADINGS:
                continue
            start = index
            while start:
                previous = lines[start - 1].strip()
                if previous and not previous.startswith(("@", "#")):
                    break
                start -= 1
            sections.append((start, title.strip() if heading in SCENARIO_HEADINGS else None))
    sections.append((len(lines), None))
    return [(start, end, title) for (start, title), (end, _) in zip(sections, sections[1:]) if title is not None]


def restrict_scenarios(snapshot, files, scenarios):
    wanted = set(scenarios)
    counts = Counter()
    effective_files = {}
    for name in files:
        if not name.startswith("features/") or not name.endswith(".feature"):
            continue
        path = snapshot / name
        lines = path.read_bytes().decode("utf-8").splitlines(keepends=True)
        blocks = scenario_blocks(lines)
        selected = [title for _, _, title in blocks if title in wanted]
        counts.update(selected)
        if not selected:
            path.unlink()
            continue
        # Vanessa's name filter in this release can skip a feature's Context.
        # Keep the selected scenarios, their tags and examples, and shared sections.
        for start, end, title in reversed(blocks):
            if title not in wanted:
                del lines[start:end]
        path.write_bytes("".join(lines).encode("utf-8"))
        effective_files[name] = file_sha256(path)
    for name in scenarios:
        if counts[name] != 1:
            raise ValueError(f"Сценарий должен встретиться ровно один раз: {name} ({counts[name]})")
    return effective_files


def prepare_inputs(root, groups, features, scenarios):
    snapshot = root / "inputs"
    snapshot.mkdir()
    runnable = features or [f"features/{group}" for group in groups]
    paths = ["VAParams.json", "libraries", *runnable]
    commit = git("rev-parse", "HEAD").decode().strip()
    files = ui_files(paths)
    if not set(features) <= set(files):
        raise ValueError(f"Не найдены выбранные .feature: {sorted(set(features) - set(files))}")
    actual_groups = set(list_groups([name for name in files if name.startswith("features/")]))
    if set(groups) != actual_groups:
        raise ValueError(f"Нет сценариев в группах: {sorted(set(groups) - actual_groups)}")
    if "VAParams.json" not in files or not any(name.startswith("libraries/") and name.endswith(".feature") for name in files):
        raise ValueError("В рабочем дереве ui нужны VAParams.json и библиотеки Vanessa")

    hashes = {}
    for name in files:
        source = UI / name
        if not source.resolve().is_relative_to(UI.resolve()):
            raise ValueError(f"Файл находится вне ui: {name}")
        destination = snapshot / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        hashes[name] = file_sha256(destination)
    if (commit != git("rev-parse", "HEAD").decode().strip() or files != ui_files(paths)
            or any(file_sha256(UI / name) != digest for name, digest in hashes.items())):
        raise RuntimeError("Рабочие файлы ui изменились при копировании. Повторите запуск")

    effective_files = restrict_scenarios(snapshot, files, scenarios) if scenarios else {}
    write_json(root / "local-source.json", dict(commit=commit, source=str(UI), files=hashes,
               features=features, scenarios=scenarios, scenario_files=effective_files))
    prepare_ci_runner(snapshot)


def prepare_ci_runner(snapshot):
    runner = require_file(CI_SCRIPTS / "run-ui-docker.sh")
    text = runner.read_text(encoding="utf-8")
    manager = '/N"Администратор"'
    if text.count(manager) != 1 or f'/Execute"/work/{VANESSA_EPF}"' not in text:
        raise RuntimeError(f"Изменился контракт CI-раннера: {runner}")
    text = text.replace(manager, '/N"АдминистраторТакси" /iTaxi')
    (snapshot / runner.name).write_text(text, encoding="utf-8", newline="\n")


def python_ci(script, *args):
    return [sys.executable, "-B", "-X", "utf8", str(CI_SCRIPTS / script), *map(str, args)]


def run_group(root, spec, index, group, image):
    output = root / "results" / f"test-results-1-ui-{index}"
    output.mkdir()
    container = f"kafka-ui-{root.name}-{index}"
    started = now()
    command = ["docker", "run", "--rm", "--init", "--name", container,
               *bind(Path(spec["base"]), "/seed/1Cv8.1CD"), *bind(root / "inputs", "/inputs"),
               *bind(Path(spec["epf"]), f"/vendor/{VANESSA_EPF}"),
               *bind(output, "/export", readonly=False), *bind(ADAPTER, "/coverage-project"),
               "-e", "COVERAGE_PROJECT_DIR=/coverage-project", "-w", "/work", image,
               "bash", "-ec", WORKER_COMMAND, "--", group, str(spec["timeout"])]
    with (output / "runner.log").open("wb") as log:
        runner = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode

    allure = output / "allure"
    coverage = output / "genericCoverage.xml"
    with (output / "validation.log").open("wb") as log:
        allure_rc = subprocess.run(python_ci("validate_allure_report.py", "--results-dir", allure),
                                  stdout=log, stderr=subprocess.STDOUT).returncode
        coverage_rc = subprocess.run(python_ci("validate_coverage_report.py", "--allow-uncovered", coverage),
                                     stdout=log, stderr=subprocess.STDOUT).returncode
    if coverage_rc == 0:
        (output / "coverage").mkdir()
        coverage.rename(output / "coverage" / coverage.name)
    records = [read_json(path) for path in allure.rglob("*-result.json")]
    counts = Counter(record.get("status", "unknown") for record in records)
    exit_file = output / "exit-code.txt"
    test_code = int(exit_file.read_text(encoding="utf-8-sig").strip()) if exit_file.is_file() else None
    passed = bool(counts["passed"]) and not (set(counts) - {"passed", "skipped"})
    if spec["scenarios"]:
        wanted = set(spec["scenarios"])
        names = {record.get("name", "") for record in records}
        seen = {name if name in wanted else name.rsplit(" №", 1)[0] for name in names}
        passed = passed and seen == wanted and counts["passed"] == len(records)
    result = dict(index=index, group=group, container=container, runner=runner, test_exit=test_code,
                  allure=allure_rc, coverage=coverage_rc, stats=counts, started_at=started, finished_at=now(),
                  result="passed" if runner == 0 and test_code == 0 and allure_rc == 0 and coverage_rc == 0 and passed else "failed")
    write_json(output / "group-result.json", result)
    return result


def make_report(root, groups):
    source = root / "allure-ui"
    report = root / "allure-ui-report"
    run_logged(python_ci("prepare_allure_results.py", "--results-dir", source, "--scope", "ui",
                         "--unit-dir", root / "unit-unused", "--ui-groups-dir", root / "results",
                         "--ui-groups-json", json.dumps(groups, ensure_ascii=False)), root / "prepare-allure.log")
    report.mkdir()
    image = resolve_image("node:22-slim", root)
    dirs = ["/inputs", *["/inputs/" + path.relative_to(source).as_posix()
                         for path in source.rglob("*") if path.is_dir()]]
    run_logged(["docker", "run", "--rm", "--init", *bind(source, "/inputs"),
                *bind(report, "/report", readonly=False), image,
                "timeout", "-k", "20s", "300", "npx", "--yes", "allure@3", "generate", *dirs, "-o", "/report"],
               root / "generate-allure.log")
    run_logged(python_ci("validate_allure_report.py", "--results-dir", source, "--summary", report / "summary.json"),
               root / "validate-allure.log")
    require_file(report / "index.html")


def view_handler(root):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root / "allure-ui-report"), **kwargs)

        def do_GET(self):
            state = read_json(root / "overnight-status.json")
            if state.get("report_ready"):
                return super().do_GET()
            if urlsplit(self.path).path != "/":
                self.send_error(404)
                return
            refresh = "" if state["phase"] == "finished" else '<meta http-equiv="refresh" content="5">'
            rows = "".join(f'<li>{escape(group["group"])} · {group["result"]}</li>' for group in state["completed"])
            message = escape(state.get("error", ""))
            page = (f'<meta charset="utf-8">{refresh}<title>Kafka Adapter UI</title>'
                    f'<h1>Kafka Adapter UI</h1><p>{state["phase"]} · {state.get("result") or ""}</p>'
                    f'<p>Завершено {len(state["completed"])} из {state["groups"]}</p>'
                    f'<ul>{rows}</ul><p>{message}</p>').encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

    return Handler


def execute(root, spec, state):
    status_path = root / "overnight-status.json"
    try:
        image = resolve_image(spec["image"], root)
        state.update(phase="ui", client_image=image)
        write_json(status_path, state)
        (root / "results").mkdir()
        with ThreadPoolExecutor(max_workers=min(spec["parallel"], len(spec["groups"]))) as pool:
            jobs = {pool.submit(run_group, root, spec, index, group, image): (index, group)
                    for index, group in enumerate(spec["groups"])}
            for future in as_completed(jobs):
                index, group = jobs[future]
                try:
                    result = future.result()
                except Exception as error:
                    result = dict(index=index, group=group, result="failed", error=str(error))
                state["completed"].append(result)
                write_json(status_path, state)
        state["phase"] = "reports"
        write_json(status_path, state)
        if file_sha256(Path(spec["base"])) != spec["base_sha256"]:
            raise RuntimeError("Исходная 1Cv8.1CD изменилась во время прогона")
        if file_sha256(Path(spec["epf"])) != spec["epf_sha256"]:
            raise RuntimeError("Исходная обработка Vanessa изменилась во время прогона")
        make_report(root, spec["groups"])
        state["report_ready"] = True
        state["result"] = "passed" if all(job["result"] == "passed" for job in state["completed"]) else "failed"
    except Exception as error:
        state.update(result="failed", error=str(error))
    state.update(phase="finished", finished_at=now())
    write_json(status_path, state)
    print(json.dumps(state, ensure_ascii=False), file=sys.stderr, flush=True)
    return int(state["result"] != "passed")


def controller(root, keep_viewer):
    spec = read_json(root / "run.json")
    status_path = root / "overnight-status.json"
    state = read_json(status_path)
    with ThreadingHTTPServer(("127.0.0.1", 0), view_handler(root)) as server:
        (root / "viewer-url.txt").write_text(f"http://127.0.0.1:{server.server_port}/\n", encoding="utf-8")
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            code = execute(root, spec, state)
            if keep_viewer:
                time.sleep(3600)
            return code
        finally:
            server.shutdown()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, help="путь к подготовленной 1Cv8.1CD")
    parser.add_argument("--image", help=f"образ клиента, по умолчанию из base.json или {CLIENT_IMAGE}")
    vanessa = parser.add_mutually_exclusive_group()
    vanessa.add_argument("--epf", type=Path, help="готовая vanessa-automation-single.epf")
    vanessa.add_argument("--vanessa-tag", help="скачать EPF Vanessa из указанного релиза")
    parser.add_argument("--parallel", type=int, default=1, help="максимум одновременно работающих контейнеров")
    parser.add_argument("--timeout", type=int, default=3600, help="секунд на группу")
    parser.add_argument("--feature", action="append", default=[], help="путь внутри features или имя файла в одной группе")
    parser.add_argument("--scenario", action="append", default=[], help="точное имя сценария в одной группе")
    parser.add_argument("--wait", action="store_true", help="дождаться результата и вернуть код завершения")
    parser.add_argument("--list-groups", action="store_true", help="показать группы и короткие имена")
    parser.add_argument("groups", nargs="*", help="группы раздел/объект либо incoming, outgoing, panel")
    args = parser.parse_args()
    if not args.list_groups and (not args.base or not args.groups):
        parser.error("для запуска укажите --base и хотя бы одну группу")
    if args.parallel < 1 or args.timeout < 1:
        parser.error("--parallel и --timeout должны быть положительными")
    if args.scenario and (len(args.groups) != 1 or len(set(args.scenario)) != len(args.scenario)):
        parser.error("--scenario требует одну группу и неповторяющиеся имена")
    return args


def select_epf(args, build, root):
    if args.epf:
        return require_file(args.epf.resolve())
    if not args.vanessa_tag and build.get("vanessa_epf"):
        epf = require_file(Path(build["vanessa_epf"]))
        if file_sha256(epf) != build["vanessa_epf_sha256"]:
            raise ValueError(f"Контрольная сумма EPF отличается от base.json: {epf}")
        return epf
    tag = args.vanessa_tag or build.get("versions", {}).get("ui/VAExtension.cfe")
    return download_vanessa(get_release(VANESSA_REPO, tag), root / "inputs" / VANESSA_EPF)


def main():
    args = parse_args()
    if args.list_groups:
        groups = list_groups(ui_files(["features"]))
        print(json.dumps(dict(groups=groups, aliases={key: value for key, value in ALIASES.items() if value in groups}),
                         ensure_ascii=False))
        return 0
    base = require_file(args.base.resolve())
    groups = select_groups(args)
    features = feature_paths(args.feature, groups)
    manifest = base.with_name("base.json")
    build = read_json(manifest) if manifest.is_file() else {}
    base_hash = file_sha256(base)
    if build.get("sha256") and build["sha256"] != base_hash:
        raise ValueError(f"Контрольная сумма 1Cv8.1CD отличается от {manifest}")

    parent = RUNTIME_DIR / "runs"
    parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    prepare_inputs(root, groups, features, args.scenario)
    epf = select_epf(args, build, root)
    write_json(root / "groups.json", groups)
    write_json(root / "run.json", dict(base=str(base), base_sha256=base_hash, epf=str(epf),
               epf_sha256=file_sha256(epf), groups=groups,
               parallel=args.parallel, image=args.image or build.get("client_image") or CLIENT_IMAGE,
               timeout=args.timeout, scenarios=args.scenario))
    write_json(root / "overnight-status.json", dict(phase="starting", groups=len(groups), completed=[],
               unit="skipped", base_sha256=base_hash, started_at=now()))

    if args.wait:
        print(json.dumps(dict(root=str(root), groups=groups, parallel=args.parallel), ensure_ascii=False), flush=True)
        return controller(root, keep_viewer=False)
    with (root / "controller.log").open("wb") as log:
        process = subprocess.Popen([sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "__run", str(root)],
                                   stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                                   start_new_session=os.name != "nt")
    print(json.dumps(dict(root=str(root), groups=groups, parallel=args.parallel, controller=process.pid), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        if len(sys.argv) == 3 and sys.argv[1] == "__run":
            sys.exit(controller(Path(sys.argv[2]), keep_viewer=True))
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
