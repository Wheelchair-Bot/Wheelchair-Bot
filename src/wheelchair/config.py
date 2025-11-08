"""Configuration management for wheelchair emulator."""

from typing import Optional
from pydantic import BaseModel, Field
import yaml


class WheelchairConfig(BaseModel):
    """Wheelchair physical parameters."""

    wheelbase: float = Field(0.6, description="Distance between wheels in meters")
    wheel_radius: float = Field(0.15, description="Wheel radius in meters")
    max_velocity: float = Field(2.0, description="Maximum velocity in m/s")
    max_acceleration: float = Field(1.0, description="Maximum acceleration in m/s^2")
    max_angular_velocity: float = Field(1.5, description="Maximum angular velocity in rad/s")
    mass: float = Field(100.0, description="Total mass in kg")


class SensorConfig(BaseModel):
    """Sensor configuration."""

    imu_noise_stddev: float = Field(0.01, description="IMU noise standard deviation")
    proximity_range: float = Field(5.0, description="Maximum proximity sensor range in meters")
    proximity_noise_stddev: float = Field(0.05, description="Proximity noise in meters")
    proximity_update_rate: float = Field(10.0, description="Proximity sensor update rate in Hz")


class PowerConfig(BaseModel):
    """Power system configuration."""

    battery_capacity: float = Field(50.0, description="Battery capacity in Ah")
    nominal_voltage: float = Field(24.0, description="Nominal battery voltage")
    min_voltage: float = Field(20.0, description="Minimum operating voltage")
    max_voltage: float = Field(29.4, description="Maximum voltage (fully charged)")
    idle_power: float = Field(10.0, description="Idle power consumption in watts")
    motor_efficiency: float = Field(0.8, description="Motor efficiency (0-1)")


class SafetyConfig(BaseModel):
    """Safety system configuration."""

    deadman_timeout: float = Field(0.5, description="Deadman switch timeout in seconds")
    obstacle_stop_distance: float = Field(0.5, description="Emergency stop distance in meters")
    obstacle_slow_distance: float = Field(1.5, description="Slow down distance in meters")
    max_safe_speed: float = Field(1.0, description="Maximum safe speed in m/s")


class SimulationConfig(BaseModel):
    """Simulation parameters."""

    update_rate: float = Field(50.0, description="Simulation update rate in Hz")
    realtime_factor: float = Field(1.0, description="Simulation speed multiplier")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class EmulatorConfig(BaseModel):
    """Complete emulator configuration."""

    wheelchair: WheelchairConfig = Field(default_factory=WheelchairConfig)
    sensors: SensorConfig = Field(default_factory=SensorConfig)
    power: PowerConfig = Field(default_factory=PowerConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)

    @classmethod
    def from_yaml(cls, path: str) -> "EmulatorConfig":
        """
        Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            EmulatorConfig instance
        """
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_toml(cls, path: str) -> "EmulatorConfig":
        """
        Load configuration from TOML file.

        Args:
            path: Path to TOML configuration file

        Returns:
            EmulatorConfig instance
        """
        try:
            import tomli
        except ImportError:
            import tomllib as tomli

        with open(path, "rb") as f:
            data = tomli.load(f)
        return cls(**data)

    def to_yaml(self, path: str) -> None:
        """
        Save configuration to YAML file.

        Args:
            path: Path to save YAML file
        """
        with open(path, "w") as f:
            yaml.safe_dump(self.model_dump(), f, default_flow_style=False)
