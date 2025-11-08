"""Tests for emulated safety monitor."""

import pytest
import time
from wheelchair.interfaces import WheelchairState, SensorData, ControllerInput
from wheelchair.config import SafetyConfig
from wheelchair.emulator.safety import EmulatedSafetyMonitor


class TestEmulatedSafetyMonitor:
    """Test cases for EmulatedSafetyMonitor."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return SafetyConfig(
            deadman_timeout=0.5,
            obstacle_stop_distance=0.5,
            obstacle_slow_distance=1.5,
            max_safe_speed=1.0,
        )

    @pytest.fixture
    def safety(self, config):
        """Create safety monitor instance."""
        return EmulatedSafetyMonitor(config)

    @pytest.fixture
    def state(self):
        """Create test state."""
        return WheelchairState()

    @pytest.fixture
    def sensors(self):
        """Create test sensor data."""
        return SensorData()

    @pytest.fixture
    def controller(self):
        """Create test controller input."""
        return ControllerInput()

    def test_initialization(self, safety):
        """Test safety monitor initializes correctly."""
        assert safety is not None

    def test_emergency_stop_button(self, safety, state, sensors, controller):
        """Test emergency stop button triggers safety."""
        controller.emergency_stop = True
        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is False

    def test_deadman_activation(self, safety, state, sensors, controller):
        """Test deadman switch activation."""
        # Initially safe without deadman being activated
        controller.deadman_pressed = False
        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is True  # Safe when never activated

        # Activate deadman
        controller.deadman_pressed = True
        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is True

    def test_deadman_timeout(self, safety, state, sensors, controller):
        """Test deadman switch times out."""
        # Activate deadman
        controller.deadman_pressed = True
        safety.check_safety(state, sensors, controller)

        # Release deadman and wait
        controller.deadman_pressed = False
        time.sleep(0.6)  # Longer than timeout

        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is False  # Should timeout

    def test_obstacle_stop_distance(self, safety, state, sensors, controller):
        """Test emergency stop for close obstacles."""
        state.linear_velocity = 1.0  # Moving forward
        sensors.proximity_front = 0.3  # Very close

        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is False

    def test_obstacle_direction_aware(self, safety, state, sensors, controller):
        """Test obstacle detection is direction-aware."""
        # Obstacle in front, but moving backward
        state.linear_velocity = -1.0  # Moving backward
        sensors.proximity_front = 0.3  # Close obstacle in front

        # Should be safe since moving away from obstacle
        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is True

        # Now test rear obstacle while moving backward
        sensors.proximity_rear = 0.3
        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is False

    def test_speed_limiting_near_obstacle(self, safety, state, sensors):
        """Test speed is limited near obstacles."""
        state.linear_velocity = 1.0
        sensors.proximity_front = 1.0  # In slow zone

        limit = safety.should_limit_speed(state, sensors)
        assert limit is not None
        assert 0.0 < limit < 1.0

    def test_no_limiting_far_from_obstacles(self, safety, state, sensors):
        """Test no speed limiting far from obstacles."""
        sensors.proximity_front = 3.0  # Far away

        limit = safety.should_limit_speed(state, sensors)
        assert limit is None  # No limiting needed

    def test_full_stop_very_close_obstacle(self, safety, state, sensors):
        """Test full stop for very close obstacles."""
        state.linear_velocity = 0.5  # Moving forward
        sensors.proximity_front = 0.3  # Very close

        limit = safety.should_limit_speed(state, sensors)
        assert limit == 0.0

    def test_speed_limit_interpolation(self, safety, state, sensors, config):
        """Test speed limit interpolates correctly."""
        # Test at different distances
        sensors.proximity_front = config.obstacle_slow_distance
        limit_far = safety.should_limit_speed(state, sensors)

        sensors.proximity_front = (
            config.obstacle_stop_distance + config.obstacle_slow_distance
        ) / 2
        limit_mid = safety.should_limit_speed(state, sensors)

        sensors.proximity_front = config.obstacle_stop_distance + 0.01
        limit_near = safety.should_limit_speed(state, sensors)

        # Limits should decrease as obstacle gets closer
        if limit_far is not None and limit_mid is not None:
            assert limit_far > limit_mid
        if limit_mid is not None:
            assert limit_mid > limit_near

    def test_reset(self, safety, state, sensors, controller):
        """Test resetting safety monitor."""
        # Activate deadman
        controller.deadman_pressed = True
        safety.check_safety(state, sensors, controller)

        # Reset
        safety.reset()

        # Should be back to initial state
        controller.deadman_pressed = False
        is_safe = safety.check_safety(state, sensors, controller)
        assert is_safe is True  # Safe again before activation

    def test_multiple_obstacles(self, safety, state, sensors):
        """Test handling multiple obstacles."""
        sensors.proximity_front = 2.0
        sensors.proximity_left = 0.8
        sensors.proximity_right = 1.5

        # Should use closest obstacle for limiting
        limit = safety.should_limit_speed(state, sensors)
        assert limit is not None
