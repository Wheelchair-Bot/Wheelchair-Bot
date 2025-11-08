"""Emulated power system."""

from wheelchair.interfaces import PowerSystem
from wheelchair.config import PowerConfig


class EmulatedPowerSystem(PowerSystem):
    """
    Emulated battery/power system.

    Simulates battery discharge based on power consumption.
    """

    def __init__(self, config: PowerConfig):
        """
        Initialize emulated power system.

        Args:
            config: Power system configuration
        """
        self.config = config
        self._capacity_ah = config.battery_capacity
        self._voltage = config.max_voltage
        self._percent = 100.0
        self._consumed_ah = 0.0

    def get_voltage(self) -> float:
        """
        Get battery voltage.

        Returns:
            Battery voltage in volts
        """
        return self._voltage

    def get_percent(self) -> float:
        """
        Get battery percentage.

        Returns:
            Battery percentage (0-100)
        """
        return self._percent

    def update(self, dt: float, power_draw: float) -> None:
        """
        Update power system state based on consumption.

        Args:
            dt: Time delta in seconds
            power_draw: Current power draw in watts
        """
        # Calculate current draw in amps
        current_draw = power_draw / self._voltage

        # Update consumed capacity (Ah = A * hours)
        self._consumed_ah += current_draw * (dt / 3600.0)

        # Calculate remaining percentage
        self._percent = max(
            0.0, 100.0 * (1.0 - self._consumed_ah / self._capacity_ah)
        )

        # Update voltage based on discharge curve (simple linear model)
        voltage_range = self.config.max_voltage - self.config.min_voltage
        self._voltage = self.config.min_voltage + (self._percent / 100.0) * voltage_range

        # Clamp values
        self._voltage = max(self.config.min_voltage, min(self.config.max_voltage, self._voltage))
        self._percent = max(0.0, min(100.0, self._percent))

    def reset(self) -> None:
        """Reset battery to full charge."""
        self._voltage = self.config.max_voltage
        self._percent = 100.0
        self._consumed_ah = 0.0

    def set_charge_level(self, percent: float) -> None:
        """
        Set battery charge level for testing.

        Args:
            percent: Battery percentage (0-100)
        """
        self._percent = max(0.0, min(100.0, percent))
        self._consumed_ah = self._capacity_ah * (1.0 - self._percent / 100.0)

        # Update voltage
        voltage_range = self.config.max_voltage - self.config.min_voltage
        self._voltage = self.config.min_voltage + (self._percent / 100.0) * voltage_range
