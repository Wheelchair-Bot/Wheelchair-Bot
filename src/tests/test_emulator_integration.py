"""Integration tests for complete emulator system."""

import pytest
from wheelchair.config import EmulatorConfig
from wheelchair.factory import create_emulator
from wheelchair.interfaces import ControllerInput


class TestEmulatorIntegration:
    """Integration tests for complete emulator."""

    @pytest.fixture
    def emulator(self):
        """Create emulator instance."""
        config = EmulatorConfig()
        config.simulation.seed = 42  # Deterministic
        return create_emulator(config)

    def test_emulator_creation(self, emulator):
        """Test emulator can be created."""
        assert emulator is not None
        assert emulator.drive is not None
        assert emulator.controller is not None
        assert emulator.sensors is not None
        assert emulator.power is not None
        assert emulator.safety is not None

    def test_single_step(self, emulator):
        """Test emulator can execute one step."""
        initial_time = emulator._sim_time
        emulator.step()
        assert emulator._sim_time > initial_time
        assert emulator._step_count == 1

    def test_multiple_steps(self, emulator):
        """Test emulator can run multiple steps."""
        for _ in range(10):
            emulator.step()
        assert emulator._step_count == 10

    def test_state_progression(self, emulator):
        """Test state updates through simulation."""
        # Set controller to move forward
        emulator.controller.set_input(linear=0.5, deadman_pressed=True)

        initial_x = emulator.state.x

        # Run for 100 steps
        for _ in range(100):
            emulator.step()

        # Position should have changed
        assert emulator.state.x > initial_x

    def test_battery_discharge_during_operation(self, emulator):
        """Test battery discharges during operation."""
        initial_percent = emulator.state.battery_percent

        # Run with motors active
        emulator.controller.set_input(linear=0.8, deadman_pressed=True)

        for _ in range(1000):
            emulator.step()

        # Battery should have discharged
        assert emulator.state.battery_percent < initial_percent

    def test_emergency_stop_halts_motion(self, emulator):
        """Test emergency stop halts all motion."""
        # Start moving
        emulator.controller.set_input(linear=0.8, deadman_pressed=True)
        for _ in range(50):
            emulator.step()

        # Verify moving
        assert emulator.state.linear_velocity > 0.0

        # Emergency stop
        emulator.controller.set_input(emergency_stop=True)
        emulator.step()

        # Should be stopped
        assert emulator.state.linear_velocity == 0.0
        assert emulator.state.left_motor_speed == 0.0

    def test_obstacle_triggers_safety(self, emulator):
        """Test obstacle detection triggers safety response."""
        # Start moving forward
        emulator.controller.set_input(linear=0.5, deadman_pressed=True)
        for _ in range(10):
            emulator.step()

        # Inject close obstacle
        emulator.sensors.inject_obstacle("front", 0.3)

        # Next step should stop due to safety
        emulator.step()

        # Should have stopped or limited speed
        assert emulator.state.linear_velocity < 0.5

    def test_callback_execution(self, emulator):
        """Test callbacks are executed each step."""
        callback_count = [0]

        def test_callback(state, dt):
            callback_count[0] += 1

        emulator.add_callback(test_callback)

        for _ in range(10):
            emulator.step()

        assert callback_count[0] == 10

    def test_pause_and_resume(self, emulator):
        """Test pausing and resuming simulation."""
        emulator._running = True
        emulator.pause()
        assert emulator._paused is True

        emulator.resume()
        assert emulator._paused is False

    def test_reset(self, emulator):
        """Test resetting emulator state."""
        # Run for a while
        emulator.controller.set_input(linear=0.5, deadman_pressed=True)
        for _ in range(100):
            emulator.step()

        # Reset
        emulator.reset()

        # Should be back to initial state
        assert emulator._step_count == 0
        assert emulator._sim_time == 0.0
        assert emulator.state.x == 0.0
        assert emulator.state.y == 0.0

    def test_stats(self, emulator):
        """Test getting simulation statistics."""
        for _ in range(50):
            emulator.step()

        stats = emulator.get_stats()
        assert stats["step_count"] == 50
        assert stats["sim_time"] > 0.0

    def test_timing_consistency(self, emulator):
        """Test simulation timing is consistent."""
        dt = 1.0 / emulator.config.simulation.update_rate

        for _ in range(10):
            emulator.step()

        expected_time = 10 * dt
        assert abs(emulator._sim_time - expected_time) < 0.001

    def test_scripted_scenario(self, emulator):
        """Test running a scripted controller scenario."""
        script = [
            ControllerInput(linear=0.5, deadman_pressed=True),  # Move forward
            ControllerInput(linear=0.5, deadman_pressed=True),
            ControllerInput(linear=0.5, deadman_pressed=True),
            ControllerInput(linear=0.0, angular=0.5, deadman_pressed=True),  # Turn
            ControllerInput(linear=0.0, angular=0.5, deadman_pressed=True),
            ControllerInput(linear=0.0, deadman_pressed=True),  # Stop
        ]

        emulator.controller.load_script(script)

        for _ in range(len(script)):
            emulator.step()

        # Should have executed script
        assert emulator._step_count == len(script)

    def test_differential_drive_accuracy(self, emulator):
        """Test differential drive produces expected motion."""
        # Pure rotation - equal opposite speeds
        emulator.controller.set_input(linear=0.0, angular=1.0, deadman_pressed=True)

        for _ in range(50):
            emulator.step()

        # Should have rotated but not translated much
        distance = (emulator.state.x**2 + emulator.state.y**2) ** 0.5
        assert distance < 0.1  # Minimal translation
        assert abs(emulator.state.theta) > 0.1  # Significant rotation
