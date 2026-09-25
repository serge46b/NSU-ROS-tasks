# ПР03. Нода patrol: поза и команда

Личный репозиторий курса. Пакет `turtle_bringup` по-прежнему только запускает
`turtlesim`. Своя нода — пакет `patrol`: подписка на `/turtle1/pose` и таймер,
который публикует `geometry_msgs/msg/Twist` в относительный `cmd_vel`.

Среда: WSL2, Ubuntu 24.04, ROS 2 Jazzy. Рабочий домен: **16**.

## Подготовка

В каждом терминале:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
cd "$(git rev-parse --show-toplevel)"
```

Остановите прежние `turtlesim`, `turtle_teleop_key` и `patrol` через `Ctrl+C`.

## Сборка и тесты команды

```bash
colcon build --symlink-install --packages-select patrol
source install/setup.bash
python3 -m pytest src/patrol/test
```

Чистая функция без позы даёт нулевой Twist. Обычное сообщение `turtlesim/msg/Pose`
даёт `linear.x = 0.5` и `angular.z = 0.3`. Слишком большие значения обрезаются
до `±1`, знак сохраняется.

## Запуск

Терминал A:

```bash
ros2 launch turtle_bringup sim.launch.py
```

Терминал B, без remap — публикация идёт в `/cmd_vel`, turtlesim её не читает:

```bash
ros2 run patrol patrol
```

Тот же процесс с исправлением имени при запуске:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Пока нода работает, в третьем терминале:

```bash
ros2 node info /patrol
ros2 topic info /turtle1/cmd_vel --verbose
timeout 10s ros2 topic hz /turtle1/cmd_vel
```

`Ctrl+C` останавливает `spin`. Нода при этом не публикует нулевую команду:
turtlesim ещё короткое время исполняет последний Twist и останавливается сам.
Исчезновение процесса — не мгновенное торможение.

## Проверка отчёта

```bash
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

Course kit: ревизия `v1-w03`, SHA-256 архива
`7fbfd3e8161ab6c6ebefc7663efdaf77d9a7d490399743507f33dcefbd5ac522`.
