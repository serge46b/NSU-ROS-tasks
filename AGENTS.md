Ты работаешь с курсом ROS 2 на Windows. ROS установлен в WSL2 (Ubuntu), дистрибуция **Jazzy**. Хостовый терминал Cursor — **PowerShell**; ROS-команды выполняй только внутри WSL.

Репозиторий: `E:\education\NSU\Robotics\NSU-ROS-tasks`  
Тот же путь в WSL: `/mnt/e/education/NSU/Robotics/NSU-ROS-tasks`

## Как запускать ROS

Каждый вызов `wsl` — новый bash. В **той же** команде сначала `source`, потом `ros2`. Из PowerShell оборачивай скрипт в **одинарные** кавычки, иначе `$ROS_DISTRO`, `$u` и т.п. съест PowerShell **до** передачи в bash.

```powershell
wsl -e bash -lc 'source /opt/ros/jazzy/setup.bash; export ROS_DOMAIN_ID=42; ros2 node list --no-daemon --spin-time 2'
```

- Не используй двойные кавычки вокруг bash-скрипта с `$переменными`.
- Длинный сценарий лучше положить в `.sh` и вызвать `wsl -e bash /mnt/e/education/NSU/Robotics/NSU-ROS-tasks/script.sh`.
- `DISPLAY=:0` и WSLg обычно уже есть в `bash -lc`; GUI (turtlesim, RViz) открывается на Windows-рабочем столе.
- После проверки останавливай GUI: `pkill -f turtlesim_node`.

Пример turtlesim (команда занимает процесс, пока её не убьют):

```powershell
wsl -e bash -lc 'source /opt/ros/jazzy/setup.bash; export ROS_DOMAIN_ID=42; export DISPLAY=:0; ros2 run turtlesim turtlesim_node'
```

Проверка из другого вызова `wsl` (тот же `ROS_DOMAIN_ID`):

```powershell
wsl -e bash -lc 'source /opt/ros/jazzy/setup.bash; export ROS_DOMAIN_ID=42; ros2 node list --no-daemon --spin-time 2; ros2 topic echo /turtle1/pose --once'
```

`turtle_teleop_key` интерактивен и из агентного терминала почти бесполезен; для движения используй `ros2 topic pub`.

## Материалы курса

Сайт: https://ros.lms.ci.nsu.ru

Номер недели — **две цифры** (`01`, не `1`). Практики в URL — `pr01`, не `pr1` и не `PR01`.

| Что | URL |
| --- | --- |
| Список лекций | https://ros.lms.ci.nsu.ru/lectures/ |
| Лекция недели | https://ros.lms.ci.nsu.ru/lectures/{WW}  например `/lectures/01` |
| Список практик | https://ros.lms.ci.nsu.ru/practices/ |
| Текст ПР | https://ros.lms.ci.nsu.ru/practices/pr{WW}  например `/practices/pr01` |
| Runbook сдачи | https://ros.lms.ci.nsu.ru/practices/runbook |
| Диагностика | https://ros.lms.ci.nsu.ru/practices/troubleshooting |
| Course kit | https://ros.lms.ci.nsu.ru/course/course-kit |
| Репозиторий и CI | https://ros.lms.ci.nsu.ru/course/repository-and-ci |

Как читать:

- **ПР** (`/practices/pr01`) — обычный HTML, его хорошо забирает WebFetch/curl.
- **Лекции** — Slidev SPA. curl/WebFetch дают почти только `<title>`. Нужен браузер + скриншот (snapshot пустой) либо CDP `document.body.innerText`.
- **Списки** лекций/практик гидрируются JS (`Загружаем список…`). curl не покажет карточки недель; в браузере подожди или прочитай `innerText`.
- Неопубликованная неделя: HTTP 302 на `/lectures/` или `/practices/` (не 404). Неверный формат (`/lectures/1`, `/practices/pr1`) — 404.
- Не считай, что открыты все 14 недель: смотри актуальный список. Недостающие материалы на сайте помечают «появятся в понедельник».

Checker и шаблоны сдачи: `.course-kit/v1/` (манифесты, `tools/check_practice.py`, шаблон `report.json`). Evidence клади в `evidence/prXX/` рядом с исходниками, без обёртки проекта.

**Course kit обновляется каждую неделю.** Каждый понедельник тот же адрес отдаёт новую накопительную ревизию (`VERSION` вида `v1-wNN`). Перед работой на новой неделе скачай архив и checksum заново и распакуй поверх `.course-kit/`. Текущие `archive`, `version` и `sha256`: `curl -fsS https://ros.lms.ci.nsu.ru/api/course-kit`. В отчёте и CI фиксируй SHA-256 этой ревизии; уже принятое evidence не переписывай.
