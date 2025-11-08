"""Factory for creating emulator instances."""

from wheelchair.interfaces import WheelchairState
from wheelchair.config import EmulatorConfig
from wheelchair.emulator import (
    EmulatedDrive,
    EmulatedController,
    EmulatedSensorSuite,
    EmulatedPowerSystem,
    EmulatedSafetyMonitor,
)
from wheelchair.emulator.loop import SimulationLoop


def create_emulator(config: EmulatorConfig = None) -> SimulationLoop:
    """
    Factory function to create a complete emulator system.

    Args:
        config: Emulator configuration (uses defaults if None)

    Returns:
        Configured SimulationLoop ready to run
    """
    if config is None:
        config = EmulatorConfig()

    # Create shared state
    state = WheelchairState()

    # Create subsystems
    drive = EmulatedDrive(config.wheelchair, state)
    controller = EmulatedController()
    sensors = EmulatedSensorSuite(config.sensors, state, config.simulation.seed)
    power = EmulatedPowerSystem(config.power)
    safety = EmulatedSafetyMonitor(config.safety)

    # Create simulation loop
    loop = SimulationLoop(config, drive, controller, sensors, power, safety, state)

    return loop
