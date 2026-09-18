# ПР02. Терминал, пакет и запуск turtlesim

Личный репозиторий курса. Пакет `turtle_bringup` собирает установленный
`turtlesim` через `sim.launch.py`. Своей ноды нет: команда движения
отправляется CLI.

Среда: WSL2, Ubuntu 24.04, ROS 2 Jazzy. Рабочий домен: **16**.

## Подготовка

В каждом терминале:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
cd "$(git rev-parse --show-toplevel)"
```

Остановите прежние `turtlesim` / `turtle_teleop_key` через `Ctrl+C`.

## Сборка

Из корня репозитория, только с базовой ROS (`source /opt/ros/jazzy/setup.bash`):

```bash
colcon build --symlink-install --packages-select turtle_bringup
```

После сборки в новом терминале `ros2 pkg prefix turtle_bringup` должен
указывать в `install/` этого workspace.

## Запуск

Терминал A:

```bash
ros2 launch turtle_bringup sim.launch.py
```

Должно открыться одно окно. Проверка графа в другом терминале:

```bash
ros2 node list --no-daemon --spin-time 2
```

`Ctrl+C` в A завершает launch и запущенный им turtlesim.

## Команда движения

Teleop должен быть остановлен. Поза до команды, затем одна публикация:

```bash
ros2 topic echo /turtle1/pose --once
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
ros2 topic echo /turtle1/pose --once
```

Одна публикация не задаёт бесконечное движение.

## Сбой имени топика

Издатель с тем же Twist, но другим именем:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Пока он работает:

```bash
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
```

На `/cmd_vel` есть издатель и нет подписчика turtlesim. После замены только
имени на `/turtle1/cmd_vel` команда снова доходит до черепахи.

## Проверка отчёта

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

Course kit: ревизия `v1-w02`, SHA-256 архива
`5d210c431e32418f45e2cffa9dd2028116c7a9520a36f3c7079c778cd73437a8`.
