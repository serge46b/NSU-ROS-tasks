# ПР01. Окружение и граф ROS 2

Личный репозиторий курса. На этой неделе запускаются готовые ноды `turtlesim`,
описывается граф и проверяется изоляция `ROS_DOMAIN_ID`.

Среда: WSL2, Ubuntu 24.04, ROS 2 Jazzy. Выделенная пара доменов: **16** (рабочий)
и **17** (разрыв связи).

## Подготовка терминалов

Откройте три Bash-терминала в одной WSL-среде. В каждом:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
```

Остановите прежние `turtlesim` / `turtle_teleop_key` через `Ctrl+C`.

В терминале C, из корня репозитория:

```bash
mkdir -p evidence/pr01
ros2 doctor --report > evidence/pr01/doctor.txt 2>&1
```

## Исправный граф

Терминал A (занимает терминал до `Ctrl+C`):

```bash
ros2 run turtlesim turtlesim_node
```

Терминал B:

```bash
ros2 run turtlesim turtle_teleop_key
```

Стрелки работают, пока фокус в терминале B. Терминал C:

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
POSE_TYPE=$(ros2 topic type /turtle1/pose)
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

Последнюю команду держите не меньше 10 секунд и завершите `Ctrl+C`. Поза
публикуется и у неподвижной черепахи. Тип на Jazzy: `turtlesim/msg/Pose`.
Команда движения приходит в `/turtle1/cmd_vel`.

Наблюдения сводятся в `evidence/pr01/graph.md`.

## Разрыв и восстановление связи

Симулятор в терминале A всё время работает в домене 16.

В терминале B остановите teleop и запустите его в другом домене:

```bash
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

Стрелки больше не управляют черепахой. В терминале C:

```bash
export ROS_DOMAIN_ID=17
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```

Ожидается `/teleop_turtle` без `/turtlesim`, поза не приходит, `exit=124`.

Затем в B остановите teleop, верните `ROS_DOMAIN_ID=16` и запустите снова.
В C повторите тот же тест:

```bash
export ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?"
```

Обе ноды видны, приходит поза, `exit=0`, стрелки снова двигают черепаху.

`export` не перенастраивает уже запущенную ноду: симулятор и установку ROS
менять не нужно, достаточно перезапустить teleop и CLI в исходном домене.

## Проверка отчёта

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```

Course kit: ревизия `v1-w02`, SHA-256 архива
`5d210c431e32418f45e2cffa9dd2028116c7a9520a36f3c7079c778cd73437a8`.
