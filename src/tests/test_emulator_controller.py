"""Tests for emulated controller."""

import pytest
from wheelchair.interfaces import ControllerInput
from wheelchair.emulator.controller import EmulatedController


class TestEmulatedController:
    """Test cases for EmulatedController."""

    @pytest.fixture
    def controller(self):
        """Create controller instance."""
        return EmulatedController()

    def test_initialization(self, controller):
        """Test controller initializes correctly."""
        assert controller.is_connected()
        input_data = controller.read_input()
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_set_input(self, controller):
        """Test setting controller input."""
        controller.set_input(linear=0.5, angular=-0.3)
        input_data = controller.read_input()
        assert input_data.linear == 0.5
        assert input_data.angular == -0.3

    def test_input_clamping(self, controller):
        """Test input values are clamped to valid range."""
        controller.set_input(linear=1.5, angular=-1.5)
        input_data = controller.read_input()
        assert input_data.linear == 1.0
        assert input_data.angular == -1.0

    def test_emergency_stop_button(self, controller):
        """Test emergency stop button."""
        controller.set_input(emergency_stop=True)
        input_data = controller.read_input()
        assert input_data.emergency_stop is True

    def test_deadman_switch(self, controller):
        """Test deadman switch."""
        controller.set_input(deadman_pressed=True)
        input_data = controller.read_input()
        assert input_data.deadman_pressed is True

    def test_script_playback(self, controller):
        """Test scripted input playback."""
        script = [
            ControllerInput(linear=0.5, angular=0.0),
            ControllerInput(linear=0.0, angular=0.5),
            ControllerInput(linear=0.0, angular=0.0),
        ]
        controller.load_script(script)

        # Read through script
        assert controller.read_input().linear == 0.5
        assert controller.read_input().angular == 0.5
        assert controller.read_input().linear == 0.0

    def test_script_reset(self, controller):
        """Test resetting script playback."""
        script = [
            ControllerInput(linear=0.5, angular=0.0),
            ControllerInput(linear=0.0, angular=0.5),
        ]
        controller.load_script(script)

        controller.read_input()  # Read first
        controller.reset_script()  # Reset

        # Should read first again
        assert controller.read_input().linear == 0.5

    def test_clear_script(self, controller):
        """Test clearing script."""
        script = [ControllerInput(linear=0.5, angular=0.0)]
        controller.load_script(script)
        controller.clear_script()

        input_data = controller.read_input()
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_manual_overrides_script(self, controller):
        """Test manual input clears script."""
        script = [ControllerInput(linear=0.5, angular=0.0)]
        controller.load_script(script)

        controller.set_input(linear=0.8, angular=0.0)

        # Script should be cleared
        assert len(controller._script) == 0

    def test_disconnect(self, controller):
        """Test controller disconnect."""
        controller.disconnect()
        assert not controller.is_connected()

    def test_reconnect(self, controller):
        """Test controller reconnect."""
        controller.disconnect()
        controller.connect()
        assert controller.is_connected()
