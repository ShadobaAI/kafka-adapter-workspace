"""Собрать изолированную 1Cv8.1CD из готовой выгрузки base + adapter в .local/base_xml."""

import argparse
from fnmatch import fnmatchcase
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote
from urllib.request import Request, urlopen
from zipfile import ZipFile


TESTS = Path(__file__).resolve().parents[2]
RUNTIME_DIR = TESTS / ".local" / "docker-ci"
BASE_XML_DIR = TESTS / ".local" / "base_xml"
ADAPTER = TESTS.parent / "adapter" / "adapter"
CI_SCRIPTS = ADAPTER / ".github" / "scripts"
CLIENT_IMAGE = "ghcr.io/shadobaai/client:latest"
IBCMD_IMAGE = "ghcr.io/shadobaai/ibcmd:latest"
ORAS_VERSION = "1.3.0"
TEMPLATE = "kfk-tmpl-test.dt"
VANESSA_REPO = "Pr-Mex/vanessa-automation"
VANESSA_EPF = "vanessa-automation-single.epf"
EXTENSIONS = (
    ("ТестированиеАдаптераKafka", "kafka-adapter-examples.cfe"),
    ("YAXUNIT", "unit/YAXUNIT.cfe"),
    ("МодульныеТесты", "unit/unit.cfe"),
    ("VAExtension", "ui/VAExtension.cfe"),
)


def write_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def file_sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def directory_sha256(directory):
    digest = hashlib.sha256()
    for path in sorted(directory.rglob("*"), key=Path.as_posix):
        if path.is_file():
            digest.update(path.relative_to(directory).as_posix().encode("utf-8") + b"\0")
            digest.update(bytes.fromhex(file_sha256(path)))
    return digest.hexdigest()


def require_file(path):
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f"Файл отсутствует или пуст: {path}")
    return path


def confirm_base_xml():
    require_file(BASE_XML_DIR / "Configuration.xml")
    print(f"{BASE_XML_DIR} — выгрузка конфигурации base из базы unit с уже включённым адаптером.\n"
          "Выгрузка актуальна для этой сборки 1Cv8.1CD? Для подтверждения введите «да» или «yes».",
          file=sys.stderr, flush=True)
    if sys.stdin.readline().strip().casefold() not in ("да", "yes"):
        raise ValueError("Создание базы отменено.")


def bind(path, target, readonly=True):
    mount = f"type=bind,source={path},target={target}"
    if readonly:
        mount += ",readonly"
    return ["--mount", mount]


def run_logged(command, log_path):
    with log_path.open("wb") as log:
        code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
    if code:
        raise RuntimeError(f"Код завершения {code}. Лог: {log_path}")


def resolve_image(reference, log_dir):
    inspect = ["docker", "image", "inspect", "--format", "{{.Id}} {{.Os}}", reference]
    result = subprocess.run(inspect, capture_output=True, text=True)
    if result.returncode:
        name = reference.rsplit("/", 1)[-1].replace(":", "-")
        run_logged(["docker", "pull", reference], log_dir / f"pull-{name}.log")
        result = subprocess.run(inspect, capture_output=True, text=True, check=True)
    image_id, os_name = result.stdout.strip().split()
    if os_name != "linux":
        raise ValueError(f"Требуется Linux-образ: {reference}")
    return image_id


def open_url(url):
    return urlopen(Request(url, headers={"User-Agent": "kafka-local-docker-ci"}), timeout=60)


def get_release(repo, tag):
    endpoint = "tags/" + quote(tag, safe="") if tag else "latest"
    with open_url(f"https://api.github.com/repos/{repo}/releases/{endpoint}") as response:
        return json.load(response)


def download_asset(release, pattern, destination):
    matches = [asset for asset in release["assets"] if fnmatchcase(asset["name"], pattern)]
    if len(matches) != 1:
        raise ValueError(f"Ожидался один артефакт {pattern} в {release['tag_name']}")
    asset = matches[0]
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    with open_url(asset["browser_download_url"]) as response, temporary.open("wb") as output:
        shutil.copyfileobj(response, output)
    if temporary.stat().st_size != asset["size"]:
        raise RuntimeError(f"Размер загруженного файла не совпадает: {temporary}")
    checksum = asset.get("digest")
    if checksum and checksum != "sha256:" + file_sha256(temporary):
        raise RuntimeError(f"Контрольная сумма загруженного файла не совпадает: {temporary}")
    temporary.replace(destination)
    return release["tag_name"]


def download_release(repo, tag, pattern, destination):
    return download_asset(get_release(repo, tag), pattern, destination)


def download_vanessa(release, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vanessa-", dir=destination.parent) as scratch:
        archive = Path(scratch) / "vanessa.zip"
        download_asset(release, "vanessa-automation-single.*.zip", archive)
        with ZipFile(archive) as package, package.open(VANESSA_EPF) as source, destination.open("xb") as output:
            shutil.copyfileobj(source, output)
    return require_file(destination)


def oras_command(scratch):
    installed = shutil.which("oras")
    if installed:
        return installed
    if sys.platform != "win32":
        raise RuntimeError("Для загрузки OCI-артефактов установите ORAS или укажите --assets")
    filename = f"oras_{ORAS_VERSION}_windows_amd64.zip"
    archive = scratch / filename
    download_release("oras-project/oras", f"v{ORAS_VERSION}", filename, archive)
    with ZipFile(archive) as release:
        release.extract("oras.exe", scratch)
    return str(scratch / "oras.exe")


def fetch_inputs(args, root):
    assets = root / "inputs"
    assets.mkdir()
    sources = [
        ("ShadobaAI/kafka-adapter-examples", args.examples_tag, EXTENSIONS[0][1], EXTENSIONS[0][1]),
        ("bia-technologies/yaxunit", args.yaxunit_tag, "YAxUnit-*.cfe", EXTENSIONS[1][1]),
    ]
    versions = {}
    for repo, tag, pattern, destination in sources:
        versions[destination] = download_release(repo, tag, pattern, assets / destination)
    vanessa = get_release(VANESSA_REPO, args.vanessa_tag)
    versions[EXTENSIONS[3][1]] = download_asset(vanessa, "VAExtension*.cfe", assets / EXTENSIONS[3][1])
    download_vanessa(vanessa, assets / "ui" / VANESSA_EPF)

    # Host ORAS uses the same credential helper as Docker Desktop.
    with tempfile.TemporaryDirectory(prefix="oras-", dir=root) as scratch:
        oras = oras_command(Path(scratch))
        for reference, target, label in (
            (args.template_ref, assets, "template"),
            (args.unit_ref, assets / "unit", "unit"),
        ):
            target.mkdir(exist_ok=True)
            run_logged([oras, "pull", reference, "-o", str(target)], root / f"pull-{label}.log")
            versions[label] = reference
    return assets, versions


def collect_inputs(assets):
    inputs = {TEMPLATE: assets / TEMPLATE}
    for _, filename in EXTENSIONS:
        inputs[filename] = assets / filename
    if not inputs["unit/unit.cfe"].is_file():
        inputs["unit/unit.cfe"] = assets / "unit" / "output" / "unit.cfe"
    return {name: require_file(path) for name, path in inputs.items()}


def create_infobase(root, inputs, ibcmd, client, timeout):
    with tempfile.TemporaryDirectory(prefix="build-", dir=root) as scratch:
        scratch = Path(scratch)
        fill = require_file(CI_SCRIPTS / "fill-test-infobase-docker.sh")
        base_xml = shutil.copytree(BASE_XML_DIR, scratch / "base")
        base_xml_hash = directory_sha256(base_xml)

        connection = "/F/work/base-db"
        commands = [
            ["vrunner", "infobase", "init", "--src", "/inputs/template.dt", "--ibcmd", "--ibconnection", connection],
            ["vrunner", "cf", "load", "--ibcmd", "--ibconnection", connection, "/inputs/base"],
        ]
        mounts = bind(base_xml, "/inputs/base") + bind(inputs[TEMPLATE], "/inputs/template.dt")
        for index, (extension, filename) in enumerate(EXTENSIONS):
            target = f"/inputs/{index}.cfe"
            mounts += bind(inputs[filename], target)
            commands.append(["vrunner", "cfe", "load", "--extension-name", extension,
                             "--ibcmd", "--ibconnection", connection, target])

        # Keep the live database on Linux storage inside each container.
        create = "\n".join(shlex.join(command) for command in commands)
        create += "\ncp /work/base-db/1Cv8.1CD /export/unfilled.1CD"
        docker = ["docker", "run", "--rm", "--init", "-w", "/work",
                  *bind(scratch, "/export", readonly=False)]
        timed_bash = ["timeout", "-k", "20s", str(timeout), "bash", "-ec"]
        run_logged([*docker, *mounts, ibcmd, *timed_bash, create], root / "create-infobase.log")

        # Shell scripts checked out with CRLF also run in the Linux image.
        fill_copy = scratch / fill.name
        fill_copy.write_text(fill.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        fill_command = "\n".join((
            "mkdir -p /work/base-db",
            "cp /export/unfilled.1CD /work/base-db/1Cv8.1CD",
            "bash /export/fill-test-infobase-docker.sh",
            "cp /work/base-db/1Cv8.1CD /export/filled.1CD",
        ))
        fill_log = root / "fill-infobase.log"
        run_logged([*docker, client, *timed_bash, fill_command], fill_log)
        # vrunner can exit 0 when the startup hook failed in the application.
        output = fill_log.read_text(encoding="utf-8", errors="replace")
        if any(message in output for message in (
            "Метод объекта не обнаружен", "Поле объекта не обнаружено", "Ошибка при вызове метода",
            "Ошибка при выполнении обработчика", "ОШИБКА -", "ERROR -",
        )):
            raise RuntimeError(f"1С сообщила об ошибке при заполнении базы. Лог: {fill_log}")
        database = root / "1Cv8.1CD"
        require_file(scratch / "filled.1CD").rename(database)
    return database, base_xml_hash


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, help="готовый каталог с шаблоном DT и расширениями, иначе скачать их")
    parser.add_argument("--output", type=Path, help="новый каталог сборки, по умолчанию в .local/docker-ci/bases")
    parser.add_argument("--examples-tag", default="1.2.5.1")
    parser.add_argument("--vanessa-tag")
    parser.add_argument("--yaxunit-tag")
    parser.add_argument("--template-ref", default="ghcr.io/shadobaai/kfk-tmpl-test:latest")
    parser.add_argument("--unit-ref", default="ghcr.io/shadobaai/unit:latest")
    parser.add_argument("--ibcmd-image", default=IBCMD_IMAGE)
    parser.add_argument("--client-image", default=CLIENT_IMAGE)
    parser.add_argument("--stage-timeout", type=int, default=1800, help="секунд на каждый этап 1С")
    args = parser.parse_args()
    if args.stage_timeout < 1:
        parser.error("--stage-timeout должен быть положительным")
    if args.output and args.output.resolve().is_relative_to(BASE_XML_DIR.resolve()):
        parser.error("--output должен находиться вне исходного каталога .local/base_xml")
    return args


def main():
    args = parse_args()
    confirm_base_xml()
    if args.output is None:
        parent = RUNTIME_DIR / "bases"
        parent.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix="base-", dir=parent))
    else:
        root = args.output.resolve()
        root.mkdir(parents=True)
    print(f"Сборка базы: {root}", file=sys.stderr, flush=True)
    assets, versions = (args.assets.resolve(), {}) if args.assets else fetch_inputs(args, root)
    inputs = collect_inputs(assets)
    ibcmd = resolve_image(args.ibcmd_image, root)
    client = resolve_image(args.client_image, root)
    input_hashes = {name: file_sha256(path) for name, path in inputs.items()}
    database, base_xml_hash = create_infobase(root, inputs, ibcmd, client, args.stage_timeout)
    input_hashes["base_xml"] = base_xml_hash
    info = dict(root=str(root), base=str(database), sha256=file_sha256(database),
                base_xml=str(BASE_XML_DIR), assets=str(assets), versions=versions, inputs=input_hashes,
                ibcmd_image=ibcmd, client_image=client)
    epf = assets / "ui" / VANESSA_EPF
    if epf.is_file():
        info.update(vanessa_epf=str(require_file(epf)), vanessa_epf_sha256=file_sha256(epf))
    write_json(root / "base.json", info)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
