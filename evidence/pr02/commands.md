# ПР02. Команды и наблюдения

Среда: WSL2, Ubuntu 24.04, ROS 2 Jazzy, `ROS_DOMAIN_ID=16`.
Корень workspace: `/mnt/e/education/NSU/Robotics/NSU-ROS-tasks`.

## Три команды Linux

### `pwd`

Назначение: показать текущий каталог и убедиться, что команды выполняются из корня репозитория, а не из установленного ROS.

Результат:

```
/mnt/e/education/NSU/Robotics/NSU-ROS-tasks
```

`ros2 pkg prefix turtlesim` в том же терминале вернул `/opt/ros/jazzy`. Это другой путь: установленный пакет дистрибутива, а не рабочий каталог.

### `mkdir -p src evidence/pr02`

Назначение: создать каталог исходников workspace и каталог evidence текущей работы. `-p` создаёт цепочку каталогов и не считает ошибкой, если они уже есть.

Результат: появились `src/` и `evidence/pr02/`. Дальше в `src/` создан пакет `turtle_bringup`.

### `ls -a`

Назначение: увидеть содержимое корня, включая скрытые записи `.` / `..` / `.git` / `.github`.

Результат (фрагмент): `.git`, `.github`, `.gitignore`, `README.md`, `src`, `evidence`. После `colcon` на диске также есть `build/`, `install/`, `log/` — они в `.gitignore` и в Git не входят.

## Чем `>` отличается от `|`

`>` перенаправляет stdout в файл и **заменяет** прежнее содержимое. Так записаны логи сборки: `colcon ... 2>&1 | tee evidence/pr02/build.txt` сочетает оба механизма.

`|` не пишет на диск сам по себе: он передаёт stdout следующей команде. Без `tee` вывод `colcon` ушёл бы только в пайп и не сохранился бы как evidence.

`2>&1` направляет stderr туда же, куда уже идёт stdout, поэтому ошибки сборки попадают в тот же лог.

## Чем `source` отличается от запуска новой программы

`source /opt/ros/jazzy/setup.bash` выполняется **в текущей** оболочке: меняются `PATH`, `ROS_DISTRO`, `AMENT_PREFIX_PATH` этого терминала. Дочерние `ros2` / `colcon` наследуют уже изменённую среду.

Запуск программы (`ros2 launch`, `colcon build`) создаёт новый процесс. Он читает текущее окружение, но не переписывает переменные родительской оболочки. Поэтому `source install/setup.bash` нужно повторять в каждом новом терминале: предыдущий `source` живёт только там, где его вызвали.

## Сборка пустого пакета и пакета с launch

```
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=16
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup \
  2>&1 | tee evidence/pr02/build-empty.txt
```

```
Starting >>> turtle_bringup
Finished <<< turtle_bringup [7.32s]
Summary: 1 package finished [8.27s]
```

После добавления `launch/sim.launch.py` и записи в `data_files` — повтор в свежем терминале, лог `evidence/pr02/build.txt`:

```
Starting >>> turtle_bringup
Finished <<< turtle_bringup [4.41s]
Summary: 1 package finished [4.70s]
```

```
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
```

Результат: `/mnt/e/education/NSU/Robotics/NSU-ROS-tasks/install/turtle_bringup` и файл `sim.launch.py`. Пустой пакет после первой сборки уже находился индексом, но ноды не запускал: сборка и `source` не стартуют процессы.

## Запуск, граф и остановка

Терминал A:

```
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

Открылось одно окно turtlesim. Фрагмент лога launch:

```
[INFO] [turtlesim_node-1]: process started with pid [1454]
[turtlesim_node-1] [INFO] [turtlesim]: Starting turtlesim with node name /turtlesim
[turtlesim_node-1] [INFO] [turtlesim]: Spawning turtle [turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]
```

Проверка графа:

```
ros2 node list --no-daemon --spin-time 2
```

```
/turtlesim
```

После `Ctrl+C` (SIGINT) launch завершается вместе с `turtlesim_node`. Повторный `ros2 node list --no-daemon --spin-time 2` пустой: запущенная нода — это процесс, а не файл `sim.launch.py` на диске. Повторный `ros2 launch turtle_bringup sim.launch.py` снова поднимает `/turtlesim`.

## Команда движения

Teleop остановлен. Тип позы и координаты до команды:

```
ros2 interface show geometry_msgs/msg/Twist
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
```

Тип: `turtlesim/msg/Pose`. Поза до:

```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```

Ожидание: `linear.x = 1.0` сдвигает черепаху вперёд по текущему курсу (ось x тела), `angular.z = 0.5` поворачивает против часовой стрелки. Одна публикация:

```
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

Поза после:

```
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
```

Координаты и `theta` выросли в ожидаемую сторону; скорости снова ноль — без новых сообщений turtlesim останавливается.

## Сбой имени и исправление

### До / сбой

Тот же Twist в другое полное имя:

```
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

`--wait-matching-subscriptions 0` нужен, потому что подписчика на `/cmd_vel` нет: иначе `--once` ждал бы совпадения.

```
ros2 topic info /cmd_vel --verbose
```

```
Type: geometry_msgs/msg/Twist
Publisher count: 1
Node name: _ros2cli_1747
Subscription count: 0
```

```
ros2 topic info /turtle1/cmd_vel --verbose
```

```
Type: geometry_msgs/msg/Twist
Publisher count: 0
Subscription count: 1
Node name: turtlesim
```

Издатель на `/cmd_vel` виден, но конечной точки turtlesim там нет. Подписчик turtlesim остаётся на `/turtle1/cmd_vel`. Поза во время сбоя совпала с позой после одиночной правильной команды:

```
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
```

Черепаха не поехала: обнаружение топика `/cmd_vel` не означает доставку в подписчика `/turtle1/cmd_vel`.

Правильного типа `geometry_msgs/msg/Twist` недостаточно. Сопоставление DDS идёт по **полному имени** топика и типу вместе. Сообщение того же типа в другом имени — другой граф, turtlesim его не читает.

### После

Остановлен издатель `/cmd_vel`. Исправлено только имя:

```
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
  /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

```
ros2 topic info /turtle1/cmd_vel --verbose
```

```
Type: geometry_msgs/msg/Twist
Publisher count: 1
Node name: _ros2cli_1785
Subscription count: 1
Node name: turtlesim
```

Теперь есть и издатель CLI, и подписчик turtlesim на одном имени. Поза во время публикации:

```
x: 3.685398817062378
y: 8.301831245422363
theta: -1.9631853103637695
linear_velocity: 1.0
angular_velocity: 0.5
```

Черепаха снова движется с заданными скоростями. После `Ctrl+C` издателя скорости обнулились:

```
x: 3.588374614715576
y: 7.997252464294434
theta: -1.8031853437423706
linear_velocity: 0.0
angular_velocity: 0.0
```

Топик `/cmd_vel` после остановки ошибочного издателя исчез (`Unknown topic '/cmd_vel'`): он существовал только пока работал CLI-издатель.
