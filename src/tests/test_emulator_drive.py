"""Tests for emulated drive system."""

import pytest
import math
from wheelchair.interfaces import WheelchairState
from wheelchair.config import WheelchairConfig
from wheelchair.emulator.drive import EmulatedDrive


class TestEmulatedDrive:
    """Test cases for EmulatedDrive."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return WheelchairConfig(
            wheelbase=0.6,
            wheel_radius=0.15,
            max_velocity=2.0,
            max_acceleration=1.0,
            max_angular_velocity=1.5,
            mass=100.0,
        )

    @pytest.fixture
    def state(self):
        """Create test state."""
        return WheelchairState()

    @pytest.fixture
    def drive(self, config, state):
        """Create drive instance."""
        return EmulatedDrive(config, state)

    def test_initialization(self, drive):
        """Test drive system initializes correctly."""
        assert drive is not None
        left, right = drive.get_motor_speeds()
        assert left == 0.0
        assert right == 0.0

    def test_set_motor_speeds(self, drive):
        """Test setting motor speeds."""
        drive.set_motor_speeds(0.5, 0.5)
        # Speeds should be set but not applied immediately
        assert drive._target_left_speed == 0.5
        assert drive._target_right_speed == 0.5

    def test_motor_speed_clamping(self, drive):
        """Test motor speeds are clamped to valid range."""
        drive.set_motor_speeds(1.5, -1.5)
        assert drive._target_left_speed == 1.0
        assert drive._target_right_speed == -1.0

    def test_emergency_stop(self, drive, state):
        """Test emergency stop immediately halts motors."""
        drive.set_motor_speeds(0.8, 0.8)
        drive.update(0.1)
        drive.emergency_stop()

        assert drive._current_left_speed == 0.0
        assert drive._current_right_speed == 0.0
        assert state.linear_velocity == 0.0
        assert state.angular_velocity == 0.0
        assert state.emergency_stop is True

    def test_acceleration_limits(self, drive, config, state):
        """Test acceleration limits are respected."""
        # Request full speed
        drive.set_motor_speeds(1.0, 1.0)

        # After one timestep, should not be at full speed
        dt = 0.02  # 50 Hz
        drive.update(dt)

        # Speed change should be limited by max_acceleration
        max_speed_change = config.max_acceleration * dt / config.max_velocity
        assert abs(drive._current_left_speed) <= max_speed_change * 1.1  # Small tolerance

    def test_forward_movement(self, drive, state):
        """Test forward movement updates position."""
        drive.set_motor_speeds(0.5, 0.5)

        # Run for 1 second at 50Hz
        for _ in range(50):
            drive.update(0.02)

        # Should have moved forward
        assert state.x > 0.0
        assert abs(state.y) < 0.01  # Should stay on x-axis
        assert state.linear_velocity > 0.0

    def test_turning(self, drive, state):
        """Test turning changes heading."""
        initial_theta = state.theta
        drive.set_motor_speeds(0.5, -0.5)  # Turn in place

        # Run for 1 second
        for _ in range(50):
            drive.update(0.02)

        # Heading should have changed
        assert abs(state.theta - initial_theta) > 0.1
        assert state.angular_velocity != 0.0

    def test_differential_drive_kinematics(self, drive, state):
        """Test differential drive produces correct velocities."""
        # Equal speeds = pure linear motion
        drive.set_motor_speeds(0.5, 0.5)
        for _ in range(50):
            drive.update(0.02)

        # Should have linear velocity, minimal angular
        assert state.linear_velocity > 0.0
        assert abs(state.angular_velocity) < 0.1

    def test_theta_normalization(self, drive, state):
        """Test theta is normalized to [-pi, pi]."""
        # Spin for a while
        drive.set_motor_speeds(1.0, -1.0)
        for _ in range(500):
            drive.update(0.02)

        # Theta should be normalized
        assert -math.pi <= state.theta <= math.pi

    def test_power_draw_calculation(self, drive):
        """Test power draw increases with speed."""
        idle_power = drive.get_power_draw()

        drive.set_motor_speeds(0.8, 0.8)
        for _ in range(10):
            drive.update(0.02)

        active_power = drive.get_power_draw()
        assert active_power > idle_power
