"""Pure and node tests for patrol parameter validation."""

from patrol.patrol import command_from_pose
from patrol.patrol import Patrol
from patrol.patrol import validate_values
import rclpy
from rclpy.parameter import Parameter
from turtlesim.msg import Pose


def test_valid_frequency_change_is_accepted():
    """A change from 10 Hz to 5 Hz stays inside the allowed range."""
    ok, reason = validate_values(5.0, 0.5, 0.3)
    assert ok
    assert reason == ''


def test_zero_frequency_is_rejected():
    """Zero hertz is not a finite period and must be rejected."""
    ok, _reason = validate_values(0.0, 0.5, 0.3)
    assert not ok


def test_negative_frequency_is_rejected():
    """A negative frequency is outside 1-30 Hz."""
    ok, _reason = validate_values(-1.0, 0.5, 0.3)
    assert not ok


def test_nan_frequency_is_rejected():
    """Reject a not-a-number frequency because it is not finite."""
    ok, _reason = validate_values(float('nan'), 0.5, 0.3)
    assert not ok


def test_command_uses_parameter_speeds():
    """A pose with custom speeds requests those values, not the defaults."""
    pose = Pose()
    pose.x = 5.54
    pose.y = 5.54
    pose.theta = 0.0
    assert command_from_pose(pose, 0.2, -0.4) == (0.2, -0.4)


def test_zero_hz_rejected_keeps_timer():
    """An invalid set leaves the live timer object unchanged."""
    rclpy.init()
    node = Patrol()
    try:
        old_timer = node.timer
        result = node.set_parameters_atomically([
            Parameter('publish_hz', Parameter.Type.DOUBLE, 0.0),
        ])
        assert not result.successful
        assert node.timer is old_timer
        assert node.get_parameter('publish_hz').value == 10.0
        assert node.publish_hz == 10.0
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


def test_valid_hz_change_replaces_timer():
    """A valid frequency change destroys the old timer and creates a new one."""
    rclpy.init()
    node = Patrol()
    try:
        old_timer = node.timer
        result = node.set_parameters_atomically([
            Parameter('publish_hz', Parameter.Type.DOUBLE, 5.0),
        ])
        assert result.successful
        assert node.timer is not old_timer
        assert node.get_parameter('publish_hz').value == 5.0
        assert node.publish_hz == 5.0
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
