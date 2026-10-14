"""Patrol node: remember the latest turtle pose and publish Twist."""

import math

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim.msg import Pose

DEFAULT_LINEAR_SPEED = 0.5
DEFAULT_TURN_RATE = 0.3
DEFAULT_PUBLISH_HZ = 10.0
MAX_LINEAR = 1.0
MAX_ANGULAR = 1.0
MIN_PUBLISH_HZ = 1.0
MAX_PUBLISH_HZ = 30.0
MIN_LINEAR_SPEED = 0.0
MAX_LINEAR_SPEED = 1.0
MIN_TURN_RATE = -1.0
MAX_TURN_RATE = 1.0


def clamp(value, limit):
    """Keep a command component inside [-limit, limit] without flipping its sign."""
    if value > limit:
        return float(limit)
    if value < -limit:
        return float(-limit)
    return float(value)


def limited_command(linear_x, angular_z, max_linear=MAX_LINEAR, max_angular=MAX_ANGULAR):
    """Return speeds clamped to the limits, keeping sign and in-range values."""
    return clamp(linear_x, max_linear), clamp(angular_z, max_angular)


def command_from_pose(
        pose, linear_speed=DEFAULT_LINEAR_SPEED, turn_rate=DEFAULT_TURN_RATE):
    """Return a zero command without a pose, otherwise the patrol speeds."""
    if pose is None:
        return limited_command(0.0, 0.0)
    return limited_command(linear_speed, turn_rate)


def _is_finite_number(value):
    """Return True when value converts to a finite float."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number)


def validate_values(publish_hz, linear_speed, turn_rate):
    """Accept only finite numbers in the allowed ranges. Do not change state."""
    if not _is_finite_number(publish_hz):
        return False, 'publish_hz must be a finite number'
    if not _is_finite_number(linear_speed):
        return False, 'linear_speed must be a finite number'
    if not _is_finite_number(turn_rate):
        return False, 'turn_rate must be a finite number'
    hz = float(publish_hz)
    speed = float(linear_speed)
    turn = float(turn_rate)
    if hz < MIN_PUBLISH_HZ or hz > MAX_PUBLISH_HZ:
        return False, (
            f'publish_hz must be between {MIN_PUBLISH_HZ} and '
            f'{MAX_PUBLISH_HZ} Hz')
    if speed < MIN_LINEAR_SPEED or speed > MAX_LINEAR_SPEED:
        return False, (
            f'linear_speed must be between {MIN_LINEAR_SPEED} and '
            f'{MAX_LINEAR_SPEED} m/s')
    if turn < MIN_TURN_RATE or turn > MAX_TURN_RATE:
        return False, (
            f'turn_rate must be between {MIN_TURN_RATE} and '
            f'{MAX_TURN_RATE} rad/s')
    return True, ''


class Patrol(Node):
    """Store the latest pose and publish a timer-driven Twist on relative cmd_vel."""

    def __init__(self):
        super().__init__('patrol')
        self.declare_parameter('publish_hz', DEFAULT_PUBLISH_HZ)
        self.declare_parameter('linear_speed', DEFAULT_LINEAR_SPEED)
        self.declare_parameter('turn_rate', DEFAULT_TURN_RATE)

        self.publish_hz = self.get_parameter('publish_hz').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.turn_rate = self.get_parameter('turn_rate').value

        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(1.0 / self.publish_hz, self.on_timer)

        self.add_on_set_parameters_callback(self.validate)
        self.add_post_set_parameters_callback(self.apply)

    def validate(self, updates):
        """Reject out-of-range values without touching the timer or fields."""
        proposed = {param.name: param.value for param in updates}
        ok, reason = validate_values(
            proposed.get('publish_hz', self.publish_hz),
            proposed.get('linear_speed', self.linear_speed),
            proposed.get('turn_rate', self.turn_rate))
        return SetParametersResult(successful=ok, reason=reason)

    def apply(self, updates):
        """Copy accepted values and rebuild the timer only when frequency changes."""
        old_hz = self.publish_hz
        for param in updates:
            if param.name == 'publish_hz':
                self.publish_hz = param.value
            elif param.name == 'linear_speed':
                self.linear_speed = param.value
            elif param.name == 'turn_rate':
                self.turn_rate = param.value
        if self.publish_hz != old_hz:
            self.timer.cancel()
            self.destroy_timer(self.timer)
            self.timer = self.create_timer(
                1.0 / self.publish_hz, self.on_timer)
            self.get_logger().info(
                f'recreated timer for {self.publish_hz} Hz')

    def on_pose(self, message):
        """Remember the newest pose. The timer reads it on the next tick."""
        self.latest_pose = message

    def on_timer(self):
        """Publish the command selected from the stored pose and parameters."""
        linear_x, angular_z = command_from_pose(
            self.latest_pose, self.linear_speed, self.turn_rate)
        command = Twist()
        command.linear.x = linear_x
        command.angular.z = angular_z
        self.cmd_pub.publish(command)


def main(args=None):
    """Initialize ROS, spin until Ctrl+C, then release the node."""
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
