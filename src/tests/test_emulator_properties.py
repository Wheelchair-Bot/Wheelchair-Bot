"""Property-based tests using Hypothesis."""

import pytest
from hypothesis import given, strategies as st, settings
from wheelchair.interfaces import WheelchairState, ControllerInput
from wheelchair.config import WheelchairConfig, SensorConfig, PowerConfig, SafetyConfig
from wheelchair.emulator.drive import EmulatedDrive
from wheelchair.emulator.controller import EmulatedController
from wheelchair.emulator.power import EmulatedPowerSystem
from wheelchair.emulator.safety import EmulatedSafetyMonitor
from wheelchair.interfaces import SensorData


class TestPropertyBased:
    """Property-based tests for emulator components."""

    @given(
        left=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
        right=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_motor_speeds_always_clamped(self, left, right):
        """Test motor speeds are always clamped regardless of input."""
        config = WheelchairConfig()
        state = WheelchairState()
        drive = EmulatedDrive(config, state)

        drive.set_motor_speeds(left, right)

        # Target speeds should always be in valid range
        assert -1.0 <= drive._target_left_speed <= 1.0
        assert -1.0 <= drive._target_right_speed <= 1.0

    @given(
        linear=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
        angular=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_controller_input_always_clamped(self, linear, angular):
        """Test controller input is always clamped."""
        controller = EmulatedController()
        controller.set_input(linear=linear, angular=angular)

        input_data = controller.read_input()
        assert -1.0 <= input_data.linear <= 1.0
        assert -1.0 <= input_data.angular <= 1.0

    @given(
        steps=st.integers(min_value=1, max_value=100),
        motor_speed=st.floats(min_value=-1.0, max_value=1.0),
    )
    @settings(max_examples=50)
    def test_velocity_never_exceeds_max(self, steps, motor_speed):
        """Test velocity never exceeds configured maximum."""
        config = WheelchairConfig(max_velocity=2.0)
        state = WheelchairState()
        drive = EmulatedDrive(config, state)

        drive.set_motor_speeds(motor_speed, motor_speed)

        for _ in range(steps):
            drive.update(0.02)

        # Velocity should never exceed max
        assert abs(state.linear_velocity) <= config.max_velocity * 1.01  # Small tolerance

    @given(
        percent=st.floats(min_value=-50.0, max_value=150.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100)
    def test_battery_percent_always_valid(self, percent):
        """Test battery percentage always stays in valid range."""
        config = PowerConfig()
        power = EmulatedPowerSystem(config)

        power.set_charge_level(percent)

        result_percent = power.get_percent()
        assert 0.0 <= result_percent <= 100.0

    @given(
        power_draw=st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        time=st.floats(min_value=0.0, max_value=3600.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_battery_discharge_monotonic(self, power_draw, time):
        """Test battery always discharges (never increases) with consumption."""
        config = PowerConfig()
        power = EmulatedPowerSystem(config)

        initial_percent = power.get_percent()
        power.update(time, power_draw)
        final_percent = power.get_percent()

        # Battery should never increase
        assert final_percent <= initial_percent

    @given(
        distance=st.floats(min_value=-1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        direction=st.sampled_from(["front", "rear", "left", "right"]),
    )
    @settings(max_examples=100)
    def test_obstacle_distance_always_valid(self, distance, direction):
        """Test obstacle distances are always clamped to valid range."""
        from wheelchair.emulator.sensors import EmulatedSensorSuite

        config = SensorConfig(proximity_range=5.0)
        state = WheelchairState()
        sensors = EmulatedSensorSuite(config, state)

        try:
            sensors.inject_obstacle(direction, distance)
            data = sensors.read_sensors()

            obstacle_distance = getattr(data, f"proximity_{direction}")
            if obstacle_distance is not None:
                assert 0.0 <= obstacle_distance <= config.proximity_range
        except ValueError:
            # Invalid direction is okay to reject
            pass

    @given(
        linear_vel=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
        obstacle_dist=st.floats(min_value=0.0, max_value=3.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=100)
    def test_speed_limit_always_valid(self, linear_vel, obstacle_dist):
        """Test speed limit is always in valid range."""
        config = SafetyConfig()
        safety = EmulatedSafetyMonitor(config)

        state = WheelchairState(linear_velocity=linear_vel)
        sensors = SensorData(proximity_front=obstacle_dist)

        limit = safety.should_limit_speed(state, sensors)

        if limit is not None:
            assert 0.0 <= limit <= 1.0

    @given(
        steps=st.integers(min_value=1, max_value=1000),
    )
    @settings(max_examples=20)
    def test_theta_always_normalized(self, steps):
        """Test heading angle is always normalized to [-pi, pi]."""
        import math

        config = WheelchairConfig()
        state = WheelchairState()
        drive = EmulatedDrive(config, state)

        # Spin rapidly
        drive.set_motor_speeds(1.0, -1.0)

        for _ in range(steps):
            drive.update(0.02)

        # Theta should always be normalized
        assert -math.pi <= state.theta <= math.pi

    @given(
        left_speed=st.floats(min_value=-1.0, max_value=1.0),
        right_speed=st.floats(min_value=-1.0, max_value=1.0),
        steps=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=50)
    def test_position_never_nan(self, left_speed, right_speed, steps):
        """Test position values never become NaN."""
        import math

        config = WheelchairConfig()
        state = WheelchairState()
        drive = EmulatedDrive(config, state)

        drive.set_motor_speeds(left_speed, right_speed)

        for _ in range(steps):
            drive.update(0.02)

        # Position should always be valid numbers
        assert not math.isnan(state.x)
        assert not math.isnan(state.y)
        assert not math.isnan(state.theta)
        assert not math.isnan(state.linear_velocity)
        assert not math.isnan(state.angular_velocity)
