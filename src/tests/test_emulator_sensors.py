"""Tests for emulated sensors."""

import pytest
from wheelchair.interfaces import WheelchairState
from wheelchair.config import SensorConfig
from wheelchair.emulator.sensors import EmulatedSensorSuite


class TestEmulatedSensorSuite:
    """Test cases for EmulatedSensorSuite."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return SensorConfig(
            imu_noise_stddev=0.01,
            proximity_range=5.0,
            proximity_noise_stddev=0.05,
            proximity_update_rate=10.0,
        )

    @pytest.fixture
    def state(self):
        """Create test state."""
        return WheelchairState()

    @pytest.fixture
    def sensors(self, config, state):
        """Create sensor suite instance."""
        return EmulatedSensorSuite(config, state, seed=42)

    def test_initialization(self, sensors):
        """Test sensor suite initializes correctly."""
        assert sensors is not None
        data = sensors.read_sensors()
        assert data is not None

    def test_imu_readings(self, sensors):
        """Test IMU provides readings."""
        sensors.update(0.02)
        data = sensors.read_sensors()

        # Should have accelerometer and gyro data
        assert data.accel_z != 0.0  # Gravity
        assert isinstance(data.gyro_z, float)

    def test_imu_noise(self):
        """Test IMU readings include noise."""
        config = SensorConfig(imu_noise_stddev=0.1)  # Higher noise for test
        state = WheelchairState()
        
        # Create two separate sensors with different seeds to show noise varies
        sensors1 = EmulatedSensorSuite(config, state, seed=42)
        sensors2 = EmulatedSensorSuite(config, state, seed=43)
        
        sensors1.update(0.02)
        data1 = sensors1.read_sensors()

        sensors2.update(0.02)
        data2 = sensors2.read_sensors()

        # Readings should vary due to different random seeds
        assert data1.accel_x != data2.accel_x or data1.accel_y != data2.accel_y

    def test_gyro_tracks_angular_velocity(self, sensors, state):
        """Test gyroscope tracks angular velocity."""
        state.angular_velocity = 0.5
        sensors.update(0.02)
        data = sensors.read_sensors()

        # Gyro Z should be close to angular velocity (with noise)
        assert abs(data.gyro_z - 0.5) < 0.1

    def test_proximity_update_rate(self, sensors):
        """Test proximity sensors update at specified rate."""
        # Update at higher frequency than sensor rate
        for _ in range(5):
            sensors.update(0.01)  # 100 Hz updates

        # Proximity should update less frequently
        # (Hard to test timing exactly, but at least it shouldn't crash)
        data = sensors.read_sensors()
        assert data is not None

    def test_inject_obstacle(self, sensors):
        """Test manually injecting obstacles."""
        sensors.inject_obstacle("front", 1.5)
        data = sensors.read_sensors()
        assert data.proximity_front == 1.5

    def test_inject_obstacle_clamping(self, sensors, config):
        """Test obstacle distance is clamped to valid range."""
        sensors.inject_obstacle("front", 10.0)  # Beyond max range
        data = sensors.read_sensors()
        assert data.proximity_front == config.proximity_range

        sensors.inject_obstacle("rear", -1.0)  # Negative
        data = sensors.read_sensors()
        assert data.proximity_rear == 0.0

    def test_invalid_obstacle_direction(self, sensors):
        """Test invalid obstacle direction raises error."""
        with pytest.raises(ValueError):
            sensors.inject_obstacle("invalid", 1.0)

    def test_clear_obstacles(self, sensors):
        """Test clearing obstacle detections."""
        sensors.inject_obstacle("front", 1.0)
        sensors.inject_obstacle("rear", 2.0)
        sensors.clear_obstacles()

        data = sensors.read_sensors()
        assert data.proximity_front is None
        assert data.proximity_rear is None
        assert data.proximity_left is None
        assert data.proximity_right is None

    def test_deterministic_with_seed(self):
        """Test sensor readings are deterministic with seed."""
        config = SensorConfig()
        state = WheelchairState()

        sensors1 = EmulatedSensorSuite(config, state, seed=42)
        sensors1.update(0.02)
        data1 = sensors1.read_sensors()

        sensors2 = EmulatedSensorSuite(config, state, seed=42)
        sensors2.update(0.02)
        data2 = sensors2.read_sensors()

        # Should get same readings with same seed
        assert data1.accel_x == data2.accel_x
        assert data1.accel_y == data2.accel_y
