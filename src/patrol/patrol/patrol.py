"""Patrol node: remember the latest turtle pose and publish Twist."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim.msg import Pose

LINEAR_SPEED = 0.5
ANGULAR_SPEED = 0.3
MAX_LINEAR = 1.0
MAX_ANGULAR = 1.0


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


def command_from_pose(pose):
    """Return a zero command without a pose, otherwise the constant patrol speeds."""
    if pose is None:
        return limited_command(0.0, 0.0)
    return limited_command(LINEAR_SPEED, ANGULAR_SPEED)


class Patrol(Node):
    """Store the latest pose and publish a timer-driven Twist on relative cmd_vel."""

    def __init__(self):
        super().__init__('patrol')
        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_pose(self, message):
        """Remember the newest pose. The timer reads it on the next tick."""
        self.latest_pose = message

    def on_timer(self):
        """Publish the command selected from the stored pose."""
        linear_x, angular_z = command_from_pose(self.latest_pose)
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
