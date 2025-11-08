"""Emulated safety monitor."""

from typing import Optional
from wheelchair.interfaces import SafetyMonitor, WheelchairState, SensorData, ControllerInput
from wheelchair.config import SafetyConfig
import time


class EmulatedSafetyMonitor(SafetyMonitor):
    """
    Emulated safety monitoring system.

    Monitors deadman switch, obstacle proximity, and other safety conditions.
    """

    def __init__(self, config: SafetyConfig):
        """
        Initialize emulated safety monitor.

        Args:
            config: Safety configuration
        """
        self.config = config
        self._last_deadman_time = time.time()
        self._deadman_active = False

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
        # Check emergency stop button
        if controller.emergency_stop:
            return False

        # Check deadman switch
        if controller.deadman_pressed:
            self._last_deadman_time = time.time()
            self._deadman_active = True
        else:
            elapsed = time.time() - self._last_deadman_time
            if elapsed > self.config.deadman_timeout:
                self._deadman_active = False

        # Require deadman for operation (if it was ever activated)
        if not self._deadman_active and hasattr(self, "_ever_activated"):
            return False

        if controller.deadman_pressed:
            self._ever_activated = True

        # Check for imminent collision
        if self._check_collision_risk(state, sensors):
            return False

        return True

    def should_limit_speed(
        self, state: WheelchairState, sensors: SensorData
    ) -> Optional[float]:
        """
        Check if speed should be limited based on obstacles.

        Args:
            state: Current wheelchair state
            sensors: Current sensor readings

        Returns:
            Maximum allowed speed factor (0-1) if limiting needed, None otherwise
        """
        min_distance = self._get_min_obstacle_distance(state, sensors)

        if min_distance is None:
            return None  # No obstacles, no limiting

        # Stop if too close
        if min_distance < self.config.obstacle_stop_distance:
            return 0.0

        # Slow down if within slow zone
        if min_distance < self.config.obstacle_slow_distance:
            # Linear interpolation between stop and slow distances
            range_distance = (
                self.config.obstacle_slow_distance - self.config.obstacle_stop_distance
            )
            factor = (min_distance - self.config.obstacle_stop_distance) / range_distance
            return max(0.0, min(1.0, factor))

        return None

    def _check_collision_risk(
        self, state: WheelchairState, sensors: SensorData
    ) -> bool:
        """
        Check for imminent collision.

        Args:
            state: Current wheelchair state
            sensors: Current sensor readings

        Returns:
            True if collision risk detected
        """
        # Check front proximity when moving forward
        if state.linear_velocity > 0.1:
            if sensors.proximity_front is not None:
                if sensors.proximity_front < self.config.obstacle_stop_distance:
                    return True

        # Check rear proximity when moving backward
        if state.linear_velocity < -0.1:
            if sensors.proximity_rear is not None:
                if sensors.proximity_rear < self.config.obstacle_stop_distance:
                    return True

        return False

    def _get_min_obstacle_distance(
        self, state: WheelchairState, sensors: SensorData
    ) -> Optional[float]:
        """
        Get minimum obstacle distance considering direction of travel.

        Args:
            state: Current wheelchair state
            sensors: Current sensor readings

        Returns:
            Minimum distance to obstacle, or None if no obstacles
        """
        distances = []

        # Only consider relevant sensors based on direction
        if state.linear_velocity > 0.1:  # Moving forward
            if sensors.proximity_front is not None:
                distances.append(sensors.proximity_front)
        elif state.linear_velocity < -0.1:  # Moving backward
            if sensors.proximity_rear is not None:
                distances.append(sensors.proximity_rear)

        # Always check side sensors
        if sensors.proximity_left is not None:
            distances.append(sensors.proximity_left)
        if sensors.proximity_right is not None:
            distances.append(sensors.proximity_right)

        return min(distances) if distances else None

    def reset(self) -> None:
        """Reset safety monitor state."""
        self._last_deadman_time = time.time()
        self._deadman_active = False
        if hasattr(self, "_ever_activated"):
            delattr(self, "_ever_activated")
