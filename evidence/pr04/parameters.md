# ПР04. Параметры patrol

Среда: WSL2, Ubuntu 24.04, ROS 2 Jazzy, `ROS_DOMAIN_ID=16`.
Тип позы: `turtlesim/msg/Pose`.

Симулятор: `ros2 launch turtle_bringup sim.launch.py`.
Нода: `ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel`.

В графе один издатель `/turtle1/cmd_vel` (patrol) и один подписчик (turtlesim).

## Параметры и поток команды

Объявлены `publish_hz=10.0`, `linear_speed=0.5`, `turn_rate=0.3`.

```
$ ros2 param get /patrol publish_hz
Double value is: 10.0
```

`timeout 10s ros2 topic hz /turtle1/cmd_vel` при 10 Гц:

```
average rate: 10.011
	min: 0.098s max: 0.101s std dev: 0.00053s window: 11
average rate: 10.007
	min: 0.098s max: 0.102s std dev: 0.00058s window: 22
```

Допустимая смена частоты:

```
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
```

Нода пересоздала таймер (`recreated timer for 5.0 Hz`). Тот же издатель остался один.
После последующего отказа нуля поток держался около 5 Гц:

```
average rate: 5.002
	min: 0.199s max: 0.200s std dev: 0.00046s window: 6
```

Нулевая частота отклонена, значение не изменилось:

```
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be between 1.0 and 30.0 Hz

$ ros2 param get /patrol publish_hz
Double value is: 5.0
```

Чистые тесты отклоняют 0, отрицательное значение и NaN; допустимо 5 Гц.
Тест ноды: `set_parameters_atomically(publish_hz=0.0)` возвращает
`successful=False`, объект таймера тот же.

## Сервис /clear и действие rotate_absolute

```
$ ros2 service type /clear
std_srvs/srv/Empty

$ ros2 service call /clear std_srvs/srv/Empty '{}'
requester: making request: std_srvs.srv.Empty_Request()
response:
std_srvs.srv.Empty_Response()

$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim/action/RotateAbsolute]
```

Поза после `/clear` сохранилась (черепаха продолжала ехать: ненулевые
координаты и скорости). `/reset` здесь не вызывался.

Запрос сервиса — один вызов и один ответ: клиент дождался Empty и на этом
обмен закончился. Цель action живёт дольше запроса: сервер сначала принимает
её, затем шлёт feedback и итоговый статус, а отмену клиент запрашивает отдельно.

## Дефект: проверка частоты отключена

Временно `validate_values` принимал любое число, включая 0. Тот же
`publish_hz=0.0` дошёл до `apply`, где период считается как `1.0 / publish_hz`:

```
ZeroDivisionError: float division by zero
DEFECT_REPRODUCED
```

После возврата проверки тот же `ros2 param set /patrol publish_hz 0.0`
отклоняется, параметр остаётся 5.0, поток ~5 Гц продолжается.
