"""Pure tests for the patrol command, without spinning a node."""

from patrol.patrol import command_from_pose
from patrol.patrol import limited_command
from turtlesim.msg import Pose


def test_missing_pose_is_zero_command():
    """No pose yet must not request motion."""
    assert command_from_pose(None) == (0.0, 0.0)


def test_pose_message_requests_constant_motion():
    """A received Pose selects forward speed 0.5 and turn 0.3."""
    pose = Pose()
    pose.x = 5.54
    pose.y = 5.54
    pose.theta = 0.0
    assert command_from_pose(pose) == (0.5, 0.3)


def test_zero_command_stays_zero():
    """Zero speed and turn stay a zero command."""
    assert limited_command(0.0, 0.0) == (0.0, 0.0)


def test_in_range_command_keeps_sign_and_magnitude():
    """A value inside the limit is not rewritten."""
    assert limited_command(0.5, -0.3) == (0.5, -0.3)


def test_command_is_clamped_without_flipping_sign():
    """Overspeed is cut to the limit and keeps its sign."""
    assert limited_command(2.0, -3.0) == (1.0, -1.0)
