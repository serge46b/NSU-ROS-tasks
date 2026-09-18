# Декларация использования ИИ

- Использован ИИ: да
- Модель и версия: Cursor Grok 4.6
- Среда или интерфейс агента: Cursor Agent, репозиторий NSU-ROS-tasks, ROS 2 Jazzy в WSL2
- Затронутые компоненты: `src/turtle_bringup/`, README, `.github/workflows/ci.yml`, `.gitignore`, `evidence/pr02/*`, `AI_USAGE.md`
- Характер помощи: создание пакета и launch, съёмка логов colcon/CLI, оформление evidence и CI по условию ПР02
- Как результат был проверен независимо: `colcon build`, `ros2 pkg prefix`, живой `ros2 launch` и `topic pub`/`topic info` (сбой `/cmd_vel` и исправление `/turtle1/cmd_vel`), `python3 -m py_compile`, `check_practice.py PR02`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
