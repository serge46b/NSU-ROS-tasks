# Декларация использования ИИ

## PR02

- Использован ИИ: да
- Модель и версия: Cursor Grok 4.6
- Среда или интерфейс агента: Cursor Agent, репозиторий NSU-ROS-tasks, ROS 2 Jazzy в WSL2
- Затронутые компоненты: `src/turtle_bringup/`, README, `.github/workflows/ci.yml`, `.gitignore`, `evidence/pr02/*`, `AI_USAGE.md`
- Характер помощи: создание пакета и launch, съёмка логов colcon/CLI, оформление evidence и CI по условию ПР02
- Как результат был проверен независимо: `colcon build`, `ros2 pkg prefix`, живой `ros2 launch` и `topic pub`/`topic info` (сбой `/cmd_vel` и исправление `/turtle1/cmd_vel`), `python3 -m py_compile`, `check_practice.py PR02`

## PR03

- Использован ИИ: да (`ai_used: true` в отчёте этой ПР).
- Модель и версия: Cursor Grok 4.7
- Среда или интерфейс агента: Cursor Agent, репозиторий NSU-ROS-tasks, ROS 2 Jazzy в WSL2
- Затронутые компоненты: `src/patrol/`, README, `.github/workflows/ci.yml`, `.gitignore`, `evidence/pr03/*`, `AI_USAGE.md`
- Характер помощи: нода с подпиской и таймером, чистые тесты команды, съёмка графа до и после remap, оформление evidence и CI по условию ПР03
- Как результат был проверен независимо: `colcon build`, `python3 -m pytest src/patrol/test`, `colcon test` пакетов `patrol` и `turtle_bringup`, живой `ros2 launch` и `ros2 run patrol` без remap и с `-r cmd_vel:=/turtle1/cmd_vel`, `topic info`, `topic echo` и `timeout 10s ros2 topic hz`, `check_practice.py PR03`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
