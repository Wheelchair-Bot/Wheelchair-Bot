"""Emulated sensor suite."""

import random
import math
from wheelchair.interfaces import SensorSuite, SensorData, WheelchairState
from wheelchair.config import SensorConfig


class EmulatedSensorSuite(SensorSuite):
    """
    Emulated sensor suite with configurable noise.

    Simulates IMU and proximity sensors.
    """

    def __init__(self, config: SensorConfig, state: WheelchairState, seed: int = None):
        """
        Initialize emulated sensors.

        Args:
            config: Sensor configuration
            state: Wheelchair state to read from
            seed: Random seed for reproducibility
        """
        self.config = config
        self.state = state
        self._rng = random.Random(seed)
        self._sensor_data = SensorData()
        self._time_since_proximity_update = 0.0

    def read_sensors(self) -> SensorData:
        """
        Read all sensor data.

        Returns:
            SensorData with current readings
        """
        return self._sensor_data

    def update(self, dt: float) -> None:
        """
        Update sensor readings with noise.

        Args:
            dt: Time delta in seconds
        """
        # Update IMU data from state with noise
        # Accelerometer (including gravity and motion)
        gravity_z = 9.81  # m/s^2

        # Linear acceleration from velocity change
        # For simplicity, estimate from current velocity (would need velocity history)
        self._sensor_data.accel_x = self._add_noise(
            0.0, self.config.imu_noise_stddev  # Simplified - no actual acceleration tracking
        )
        self._sensor_data.accel_y = self._add_noise(0.0, self.config.imu_noise_stddev)
        self._sensor_data.accel_z = self._add_noise(gravity_z, self.config.imu_noise_stddev)

        # Gyroscope
        self._sensor_data.gyro_x = self._add_noise(0.0, self.config.imu_noise_stddev)
        self._sensor_data.gyro_y = self._add_noise(0.0, self.config.imu_noise_stddev)
        self._sensor_data.gyro_z = self._add_noise(
            self.state.angular_velocity, self.config.imu_noise_stddev
        )

        # Update proximity sensors at specified rate
        self._time_since_proximity_update += dt
        proximity_interval = 1.0 / self.config.proximity_update_rate

        if self._time_since_proximity_update >= proximity_interval:
            self._time_since_proximity_update = 0.0
            self._update_proximity_sensors()

    def _update_proximity_sensors(self) -> None:
        """Update proximity sensor readings."""
        # For emulator, simulate random obstacles
        # In real scenario, this would use world/environment model

        # Random chance of detecting obstacle
        for sensor_name in ["front", "rear", "left", "right"]:
            if self._rng.random() < 0.1:  # 10% chance of obstacle
                # Random distance within range
                distance = self._rng.uniform(0.5, self.config.proximity_range)
                distance = self._add_noise(distance, self.config.proximity_noise_stddev)
                distance = max(0.0, min(self.config.proximity_range, distance))
                setattr(self._sensor_data, f"proximity_{sensor_name}", distance)
            else:
                setattr(self._sensor_data, f"proximity_{sensor_name}", None)

    def _add_noise(self, value: float, stddev: float) -> float:
        """
        Add Gaussian noise to a value.

        Args:
            value: Base value
            stddev: Standard deviation of noise

        Returns:
            Value with noise added
        """
        return value + self._rng.gauss(0.0, stddev)

    def inject_obstacle(self, direction: str, distance: float) -> None:
        """
        Manually inject an obstacle detection for testing.

        Args:
            direction: Sensor direction (front, rear, left, right)
            distance: Distance to obstacle in meters
        """
        if direction not in ["front", "rear", "left", "right"]:
            raise ValueError(f"Invalid direction: {direction}")

        distance = max(0.0, min(self.config.proximity_range, distance))
        setattr(self._sensor_data, f"proximity_{direction}", distance)

    def clear_obstacles(self) -> None:
        """Clear all obstacle detections."""
        self._sensor_data.proximity_front = None
        self._sensor_data.proximity_rear = None
        self._sensor_data.proximity_left = None
        self._sensor_data.proximity_right = None
