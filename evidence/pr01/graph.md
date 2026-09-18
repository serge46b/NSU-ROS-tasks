# ПР01. Граф turtlesim

Среда: WSL2, Ubuntu 24.04.5 LTS, ROS 2 Jazzy, `ROS_DOMAIN_ID` 16 (рабочий) и 17 (разрыв).
Во всех терминалах: `source /opt/ros/jazzy/setup.bash`.

## Ноды и роли

| Нода | Пакет / программа | Роль |
| --- | --- | --- |
| `/turtlesim` | `turtlesim` / `turtlesim_node` | симулятор: подписывается на `/turtle1/cmd_vel`, публикует `/turtle1/pose` |
| `/teleop_turtle` | `turtlesim` / `turtle_teleop_key` | управление с клавиатуры: публикует `geometry_msgs/msg/Twist` в `/turtle1/cmd_vel` |

## Исправный граф (домен 16)

Запуск:

```bash
export ROS_DOMAIN_ID=16
ros2 run turtlesim turtlesim_node          # терминал A
ros2 run turtlesim turtle_teleop_key       # терминал B
```

`ros2 node list --no-daemon --spin-time 2`:

```
/teleop_turtle
/turtlesim
```

`ros2 topic list -t`:

```
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

`ros2 topic type /turtle1/pose` → `turtlesim/msg/Pose`.

`/turtlesim` подписан на `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`) и публикует `/turtle1/pose` (`turtlesim/msg/Pose`). `/teleop_turtle` публикует `/turtle1/cmd_vel`.

После стрелок `ros2 topic echo /turtle1/pose --once`:

```
x: 7.58825159072876
y: 5.413462162017822
theta: -0.06400000303983688
linear_velocity: 0.0
angular_velocity: 0.0
```

`timeout 15s ros2 topic hz /turtle1/pose` (длительность 15.295 с, завершение `exit=124` от `timeout`):

```
average rate: 62.497
	min: 0.013s max: 0.018s std dev: 0.00078s window: 820
```

Фактическая частота около 62.5 Гц, совпадает с таймером turtlesim 16 мс.

## Разрыв связи (домен 17) и восстановление (домен 16)

Симулятор в терминале A всё время работал с `ROS_DOMAIN_ID=16`. `POSE_TYPE=turtlesim/msg/Pose` сохранён с шага выше.

| Стадия | Домены | `ros2 node list --no-daemon --spin-time 2` | `timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once` |
| --- | --- | --- | --- |
| до | A=16, B=16, C=16 | `/teleop_turtle`, `/turtlesim` | поза получена |
| сбой | A=16, B=17, C=17 | `/teleop_turtle` | пустой вывод, `exit=124` |
| после | A=16, B=16, C=16 | `/teleop_turtle`, `/turtlesim` | поза получена, `exit=0` |

Сбой, файл `pose-broken.txt` пустой (сообщений нет), код:

```
exit=124
```

После возврата teleop и CLI в домен 16, `pose-fixed.txt`:

```
x: 7.58825159072876
y: 5.413462162017822
theta: -0.06400000303983688
linear_velocity: 0.0
angular_velocity: 0.0
---
```

`exit=0`. Стрелки снова двигают черепаху; после повторных клавиш поза стала `x: 9.588`, `y: 5.156`.

## Почему перезапускали только teleop

`ROS_DOMAIN_ID` читается при старте ноды. `export` в уже работающем процессе turtlesim ничего не меняет, поэтому симулятор и установку ROS трогать не нужно. Teleop, запущенный в домене 17, не входит в DDS-область симулятора: стрелки не доходят до `/turtle1/cmd_vel` издателя в домене 16, а CLI в домене 17 не видит `/turtlesim` и не получает `/turtle1/pose`. После перезапуска teleop в домене 16 обе ноды снова обнаруживаются, поза приходит, управление восстанавливается.
