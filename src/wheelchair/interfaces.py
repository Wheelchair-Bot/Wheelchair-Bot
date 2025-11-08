"""Abstract interfaces for wheelchair subsystems.

These interfaces define the contract that both emulator and real hardware
implementations must follow, enabling dependency injection and testing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum


class DriveMode(Enum):
    """Wheelchair drive modes."""

    MANUAL = "manual"
    AUTONOMOUS = "autonomous"
    ASSISTED = "assisted"


@dataclass
class WheelchairState:
    """Current state of the wheelchair."""

    # Position and velocity (meters, meters/second)
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0  # heading in radians
    linear_velocity: float = 0.0
    angular_velocity: float = 0.0

    # Motor speeds (-1.0 to 1.0)
    left_motor_speed: float = 0.0
    right_motor_speed: float = 0.0

    # Safety state
    emergency_stop: bool = False
    deadman_active: bool = False

    # Battery
    battery_voltage: float = 24.0
    battery_percent: float = 100.0


@dataclass
class SensorData:
    """Sensor readings from the wheelchair."""

    # IMU data
    accel_x: float = 0.0
    accel_y: float = 0.0
    accel_z: float = 0.0
    gyro_x: float = 0.0
    gyro_y: float = 0.0
    gyro_z: float = 0.0

    # Proximity sensors (meters, None if no obstacle detected)
    proximity_front: Optional[float] = None
    proximity_rear: Optional[float] = None
    proximity_left: Optional[float] = None
    proximity_right: Optional[float] = None


@dataclass
class ControllerInput:
    """Input from a controller (joystick, gamepad, etc.)."""

    # Normalized values from -1.0 to 1.0
    linear: float = 0.0  # forward/backward
    angular: float = 0.0  # left/right turn

    # Buttons
    emergency_stop: bool = False
    deadman_pressed: bool = False
    mode_switch: bool = False


class WheelchairDrive(ABC):
    """Interface for wheelchair drive system (motors and movement)."""

    @abstractmethod
    def set_motor_speeds(self, left: float, right: float) -> None:
        """
        Set motor speeds.

        Args:
            left: Left motor speed (-1.0 to 1.0)
            right: Right motor speed (-1.0 to 1.0)
        """
        pass

    @abstractmethod
    def get_motor_speeds(self) -> Tuple[float, float]:
        """
        Get current motor speeds.

        Returns:
            Tuple of (left, right) motor speeds
        """
        pass

    @abstractmethod
    def emergency_stop(self) -> None:
        """Immediately halt all motors."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update drive system state.

        Args:
            dt: Time delta in seconds since last update
        """
        pass


class Controller(ABC):
    """Interface for controller input (joystick, buttons, etc.)."""

    @abstractmethod
    def read_input(self) -> ControllerInput:
        """
        Read current input from controller.

        Returns:
            ControllerInput with current state
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if controller is connected.

        Returns:
            True if connected, False otherwise
        """
        pass


class SensorSuite(ABC):
    """Interface for sensor suite (IMU, proximity, etc.)."""

    @abstractmethod
    def read_sensors(self) -> SensorData:
        """
        Read all sensor data.

        Returns:
            SensorData with current readings
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update sensor readings.

        Args:
            dt: Time delta in seconds since last update
        """
        pass


class PowerSystem(ABC):
    """Interface for power system (battery monitoring)."""

    @abstractmethod
    def get_voltage(self) -> float:
        """
        Get battery voltage.

        Returns:
            Battery voltage in volts
        """
        pass

    @abstractmethod
    def get_percent(self) -> float:
        """
        Get battery percentage.

        Returns:
            Battery percentage (0-100)
        """
        pass

    @abstractmethod
    def update(self, dt: float, power_draw: float) -> None:
        """
        Update power system state.

        Args:
            dt: Time delta in seconds
            power_draw: Current power draw in watts
        """
        pass


class SafetyMonitor(ABC):
    """Interface for safety monitoring system."""

    @abstractmethod
    def check_safety(
        self, state: WheelchairState, sensors: SensorData, controller: ControllerInput
    ) -> bool:
        """
        Check if it's safe to operate.

        Args:
            state: Current wheelchair state
            sensors: Current sensor readings
            controller: Current controller input

        Returns:
            True if safe to operate, False if emergency stop needed
        """
        pass

    @abstractmethod
    def should_limit_speed(
        self, state: WheelchairState, sensors: SensorData
    ) -> Optional[float]:
        """
        Check if speed should be limited.

        Args:
            state: Current wheelchair state
            sensors: Current sensor readings

        Returns:
            Maximum allowed speed factor (0-1) if limiting needed, None otherwise
        """
        pass
