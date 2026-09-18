# Декларация использования ИИ

- Использован ИИ: да
- Модель и версия: Cursor Grok 4.6
- Среда или интерфейс агента: Cursor Agent, репозиторий NSU-ROS-tasks, ROS 2 Jazzy в WSL2
- Затронутые компоненты: README, `.github/workflows/ci.yml`, `.gitignore`, `evidence/pr01/*`, `AI_USAGE.md`
- Характер помощи: повтор опыта turtlesim/teleop, съёмка логов, оформление evidence и CI по условию ПР01
- Как результат был проверен независимо: живой запуск в WSL (`node list`, `topic hz`, `timeout 5s ros2 topic echo` в доменах 16 и 17), `python3 -m json.tool`, `check_practice.py PR01`

Полные чаты и личные промпты не прикладываются. Не включайте ключи, секреты,
персональные данные и hidden tests.
