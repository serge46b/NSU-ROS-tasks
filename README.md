# ПР04. Параметры patrol (тот же пакет, что в ПР03)

Личный репозиторий курса. Пакет `turtle_bringup` запускает `turtlesim`.
Пакет `patrol` — та же нода, что в ПР03: подписка на `/turtle1/pose` и
таймер с `geometry_msgs/msg/Twist` в относительный `cmd_vel`. В ПР04
скорость, поворот и частота стали параметрами с проверкой до смены таймера.

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

## Сборка и тесты

```bash
colcon build --symlink-install --packages-select patrol
source install/setup.bash
python3 -m pytest src/patrol/test
```

Без позы команда нулевая. Обычное `turtlesim/msg/Pose` даёт `linear.x = 0.5`
и `angular.z = 0.3`. Частота 5 Гц принимается; 0, отрицательное значение и
NaN отклоняются, активный таймер не заменяется.

## Запуск

Терминал A:

```bash
ros2 launch turtle_bringup sim.launch.py
```

Терминал B с remap из ПР03:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Без remap публикация идёт в `/cmd_vel`, turtlesim её не читает.

## Параметры

Пока нода работает:

```bash
ros2 param get /patrol publish_hz
timeout 10s ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol publish_hz 5.0
ros2 param get /patrol publish_hz
timeout 10s ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
```

Допустимые конечные числа: `linear_speed` 0–1 м/с, `turn_rate` −1–1 рад/с,
`publish_hz` 1–30 Гц. Нулевая частота отклоняется, прежнее значение и поток
сохраняются. Допустимая смена частоты останавливает старый таймер и создаёт
новый с периодом `1/publish_hz`.

Готовый сервис и действие turtlesim:

```bash
ros2 service call /clear std_srvs/srv/Empty '{}'
ros2 action list -t
```

## Проверка отчёта

```bash
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```

Course kit: ревизия `v1-w06`, SHA-256 архива
`6eda53e1c566f7f0a7e09d7afe1e5a6f3b98397175a7e57dede9a84c6d14d0fe`.
