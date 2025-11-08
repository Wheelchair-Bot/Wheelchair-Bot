"""Emulated wheelchair drive system."""

import math
from typing import Tuple
from wheelchair.interfaces import WheelchairDrive, WheelchairState
from wheelchair.config import WheelchairConfig


class EmulatedDrive(WheelchairDrive):
    """
    Emulated wheelchair drive system with physics simulation.

    Simulates differential drive kinematics with acceleration limits.
    """

    def __init__(self, config: WheelchairConfig, state: WheelchairState):
        """
        Initialize emulated drive.

        Args:
            config: Wheelchair configuration
            state: Wheelchair state (will be updated by this class)
        """
        self.config = config
        self.state = state
        self._target_left_speed = 0.0
        self._target_right_speed = 0.0
        self._current_left_speed = 0.0
        self._current_right_speed = 0.0

    def set_motor_speeds(self, left: float, right: float) -> None:
        """
        Set target motor speeds.

        Args:
            left: Left motor speed (-1.0 to 1.0)
            right: Right motor speed (-1.0 to 1.0)
        """
        # Clamp to valid range
        self._target_left_speed = max(-1.0, min(1.0, left))
        self._target_right_speed = max(-1.0, min(1.0, right))

    def get_motor_speeds(self) -> Tuple[float, float]:
        """
        Get current motor speeds.

        Returns:
            Tuple of (left, right) motor speeds
        """
        return (self._current_left_speed, self._current_right_speed)

    def emergency_stop(self) -> None:
        """Immediately halt all motors."""
        self._target_left_speed = 0.0
        self._target_right_speed = 0.0
        self._current_left_speed = 0.0
        self._current_right_speed = 0.0
        self.state.left_motor_speed = 0.0
        self.state.right_motor_speed = 0.0
        self.state.linear_velocity = 0.0
        self.state.angular_velocity = 0.0
        self.state.emergency_stop = True

    def update(self, dt: float) -> None:
        """
        Update drive system with acceleration constraints.

        Args:
            dt: Time delta in seconds
        """
        # Apply acceleration limits to motor speeds
        max_speed_change = self.config.max_acceleration * dt / self.config.max_velocity
        self._current_left_speed = self._apply_acceleration_limit(
            self._current_left_speed, self._target_left_speed, max_speed_change
        )
        self._current_right_speed = self._apply_acceleration_limit(
            self._current_right_speed, self._target_right_speed, max_speed_change
        )

        # Update state
        self.state.left_motor_speed = self._current_left_speed
        self.state.right_motor_speed = self._current_right_speed

        # Convert motor speeds to wheel velocities (m/s)
        left_velocity = self._current_left_speed * self.config.max_velocity
        right_velocity = self._current_right_speed * self.config.max_velocity

        # Differential drive kinematics
        # Linear velocity is average of wheel velocities
        self.state.linear_velocity = (left_velocity + right_velocity) / 2.0

        # Angular velocity based on wheel speed difference
        self.state.angular_velocity = (
            (right_velocity - left_velocity) / self.config.wheelbase
        )

        # Limit angular velocity
        if abs(self.state.angular_velocity) > self.config.max_angular_velocity:
            sign = 1.0 if self.state.angular_velocity > 0 else -1.0
            self.state.angular_velocity = sign * self.config.max_angular_velocity

        # Update position using simple Euler integration
        self.state.x += self.state.linear_velocity * math.cos(self.state.theta) * dt
        self.state.y += self.state.linear_velocity * math.sin(self.state.theta) * dt
        self.state.theta += self.state.angular_velocity * dt

        # Normalize theta to [-pi, pi]
        self.state.theta = math.atan2(math.sin(self.state.theta), math.cos(self.state.theta))

    def _apply_acceleration_limit(
        self, current: float, target: float, max_change: float
    ) -> float:
        """
        Apply acceleration limit to speed change.

        Args:
            current: Current speed
            target: Target speed
            max_change: Maximum allowed change

        Returns:
            New speed with acceleration limit applied
        """
        delta = target - current
        if abs(delta) <= max_change:
            return target
        else:
            return current + (max_change if delta > 0 else -max_change)

    def get_power_draw(self) -> float:
        """
        Calculate current power draw.

        Returns:
            Power draw in watts
        """
        # Simple model: power proportional to speed and mass
        avg_speed = (abs(self._current_left_speed) + abs(self._current_right_speed)) / 2.0
        # Base power plus speed-dependent power
        return 10.0 + avg_speed * self.config.mass * 0.5
