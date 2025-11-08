"""Simulation event loop for wheelchair emulator."""

import time
from typing import Optional, Callable
from wheelchair.interfaces import (
    WheelchairDrive,
    Controller,
    SensorSuite,
    PowerSystem,
    SafetyMonitor,
    WheelchairState,
)
from wheelchair.config import EmulatorConfig


class SimulationLoop:
    """
    Main simulation loop for wheelchair emulator.

    Coordinates updates across all subsystems at fixed time steps.
    """

    def __init__(
        self,
        config: EmulatorConfig,
        drive: WheelchairDrive,
        controller: Controller,
        sensors: SensorSuite,
        power: PowerSystem,
        safety: SafetyMonitor,
        state: WheelchairState,
    ):
        """
        Initialize simulation loop.

        Args:
            config: Emulator configuration
            drive: Drive system
            controller: Controller input
            sensors: Sensor suite
            power: Power system
            safety: Safety monitor
            state: Wheelchair state
        """
        self.config = config
        self.drive = drive
        self.controller = controller
        self.sensors = sensors
        self.power = power
        self.safety = safety
        self.state = state

        self._running = False
        self._paused = False
        self._step_count = 0
        self._sim_time = 0.0
        self._callbacks = []

    def add_callback(self, callback: Callable[[WheelchairState, float], None]) -> None:
        """
        Add a callback to be called each simulation step.

        Args:
            callback: Function taking (state, dt) as arguments
        """
        self._callbacks.append(callback)

    def step(self) -> None:
        """Execute one simulation step."""
        dt = 1.0 / self.config.simulation.update_rate

        # Read controller input
        controller_input = self.controller.read_input()

        # Update sensors
        self.sensors.update(dt)
        sensor_data = self.sensors.read_sensors()

        # Check safety
        is_safe = self.safety.check_safety(self.state, sensor_data, controller_input)
        speed_limit = self.safety.should_limit_speed(self.state, sensor_data)

        # Update state
        self.state.deadman_active = controller_input.deadman_pressed

        # Apply control or emergency stop
        if not is_safe or controller_input.emergency_stop:
            self.drive.emergency_stop()
        else:
            # Convert controller input to motor speeds
            left_speed, right_speed = self._controller_to_motors(
                controller_input.linear, controller_input.angular
            )

            # Apply speed limiting if needed
            if speed_limit is not None:
                left_speed *= speed_limit
                right_speed *= speed_limit

            self.drive.set_motor_speeds(left_speed, right_speed)

        # Update drive system
        self.drive.update(dt)

        # Update power system
        power_draw = getattr(self.drive, "get_power_draw", lambda: 10.0)()
        self.power.update(dt, power_draw)

        # Update state battery info
        self.state.battery_voltage = self.power.get_voltage()
        self.state.battery_percent = self.power.get_percent()

        # Update simulation time
        self._sim_time += dt
        self._step_count += 1

        # Call callbacks
        for callback in self._callbacks:
            callback(self.state, dt)

    def _controller_to_motors(self, linear: float, angular: float) -> tuple:
        """
        Convert controller input to motor speeds.

        Args:
            linear: Linear input (-1.0 to 1.0)
            angular: Angular input (-1.0 to 1.0)

        Returns:
            Tuple of (left_speed, right_speed)
        """
        # Simple differential drive conversion
        # Linear moves both motors same direction
        # Angular creates difference between motors

        left_speed = linear - angular
        right_speed = linear + angular

        # Normalize if needed
        max_speed = max(abs(left_speed), abs(right_speed))
        if max_speed > 1.0:
            left_speed /= max_speed
            right_speed /= max_speed

        return (left_speed, right_speed)

    def run(self, duration: Optional[float] = None) -> None:
        """
        Run simulation loop.

        Args:
            duration: Optional duration in seconds (None for infinite)
        """
        self._running = True
        self._paused = False

        dt = 1.0 / self.config.simulation.update_rate
        sleep_time = dt / self.config.simulation.realtime_factor

        start_time = time.time()

        try:
            while self._running:
                if not self._paused:
                    step_start = time.time()

                    self.step()

                    # Check duration
                    if duration is not None and self._sim_time >= duration:
                        break

                    # Sleep to maintain update rate
                    elapsed = time.time() - step_start
                    if elapsed < sleep_time:
                        time.sleep(sleep_time - elapsed)

        except KeyboardInterrupt:
            print("\nSimulation interrupted by user")
        finally:
            self._running = False

    def stop(self) -> None:
        """Stop the simulation loop."""
        self._running = False

    def pause(self) -> None:
        """Pause the simulation."""
        self._paused = True

    def resume(self) -> None:
        """Resume the simulation."""
        self._paused = False

    def reset(self) -> None:
        """Reset simulation state."""
        self._step_count = 0
        self._sim_time = 0.0
        self.state.__init__()  # Reset to defaults
        if hasattr(self.power, "reset"):
            self.power.reset()
        if hasattr(self.safety, "reset"):
            self.safety.reset()

    def get_stats(self) -> dict:
        """
        Get simulation statistics.

        Returns:
            Dictionary with simulation stats
        """
        return {
            "step_count": self._step_count,
            "sim_time": self._sim_time,
            "running": self._running,
            "paused": self._paused,
        }
