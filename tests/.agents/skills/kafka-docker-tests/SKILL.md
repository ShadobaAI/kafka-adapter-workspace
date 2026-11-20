---
name: kafka-docker-tests
description: Собирать тестовую 1Cv8.1CD адаптера Kafka по release CI и запускать локальные сценарии Vanessa в отдельных Docker-контейнерах с Allure. Применять для Docker-прогонов в тестовом контуре Kafka Adapter.
---

# Docker-прогоны UI адаптера Kafka

Запускай команды PowerShell из каталога `tests` рабочего пространства Kafka Adapter. Применяй `AGENTS.md` проекта и корневые `WORKSPACE-RULES.md` и `1C-RULES.md`. Docker Desktop должен работать с Linux-контейнерами. Сборка и запуск используют CI из `../adapter/adapter/.github`. Docker использует Vanessa Single из EPF релиза, как в CI. Интерактивный контур использует встроенную обработку и свой профиль `ui/.vanessa/profile.json`.

## Подготовить базу

Переиспользуй готовую `1Cv8.1CD`, если нужны те же версии конфигурации и фикстур. Для новой базы извлеки внутренний `kafka-adapter-cf-xml.zip` из артефакта `cf-xml-artifacts` нужного запуска CI или укажи опубликованный `--adapter-tag`.

```powershell
$tools = Join-Path $PWD 'scripts\docker-ci'
$adapterXml = '<путь к извлечённому kafka-adapter-cf-xml.zip>'
$base = python -X utf8 "$tools\create_ci_infobase.py" --adapter-xml $adapterXml | ConvertFrom-Json
$base.base
```

Для повторного запуска загрузи `$base` из `base.json` нужной сборки через `Get-Content -Raw -Encoding UTF8` и `ConvertFrom-Json`. Каталог сборок по умолчанию — `.local/docker-ci/bases`.

Скрипт получает DT, XML базы и расширения из тех же источников, что CI. Для GHCR использует ORAS и существующую авторизацию Docker. Для готового набора исходных артефактов передай `--assets`; при необходимости добавь `--adapter-xml`, чтобы выбрать другую сборку адаптера. Ожидаемый состав набора указан в `release-quality.yml` адаптера. Проверяй `base.json`, `create-infobase.log` и `fill-infobase.log` в `$base.root`. Манипуляции с тестовыми данными выполняются на новых экземплярах базы, с учётом `.ai/FIXTURES.md`.

## Запустить нужные сценарии

В следующем примере `incoming` и `outgoing` получают по контейнеру и копии базы. Для панели укажи `--parallel 1 panel`. Список доступных групп выводит `--list-groups`.

```powershell
$run = python -X utf8 "$tools\run_ui_docker.py" --base $base.base --parallel 2 incoming outgoing | ConvertFrom-Json
$run.root
```

`--feature` принимает путь относительно `ui/features` или имя файла в одной группе. Можно передать несколько `--feature`. `--scenario` ограничивает одну группу по точному заголовку, сохраняя `Контекст` и варианты данных в рабочей копии feature. Скрипт замораживает изменённые и новые файлы рабочего дерева `ui`, включая `libraries`. Для базы с `base.json` скрипт берёт образ и EPF из сборки. Для отдельной `1Cv8.1CD` можно явно указать `--image` и `--epf` или `--vanessa-tag`. UI запускается сразу на готовой базе, Unit-тесты пропускаются.

## Дождаться результата

- Читай `overnight-status.json` до `phase = finished`, затем проверяй `result` и результаты групп. `--wait` позволяет дождаться результата с кодом завершения в одном вызове. При фоновом запуске URL прогресса и Allure появляется в `viewer-url.txt`.
- `groups.json` сопоставляет индексы с группами, начиная с нуля. В `results/test-results-1-ui-<индекс>/` ищи `group-result.json`, `runner.log`, `1cv8c.log`, `allure/` и вложения. `local-source.json` связывает результаты с хешами запущенных файлов. Общий отчёт лежит в `allure-ui-report/`.
- Разбирай проблемы запуска по логам контейнера и `exit-code.txt`, проблемы конкретного шага по Allure. Для подтверждения точечного прогона сверяй имя и статус сценария с сырым результатом Allure.
- Сборка, тесты и генерация отчёта используют `docker run --rm`. Рабочие копии находятся внутри одноразовых контейнеров. Docker удаляет их и анонимные volumes образов по завершении. Контейнеры прогона можно проверить через `docker ps -a` по префиксу `kafka-ui-<имя каталога запуска>-`. Диагностика и отчёты прогона сохраняются в `.local/docker-ci/runs`.
