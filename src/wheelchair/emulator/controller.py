"""Emulated controller input."""

from typing import List, Optional
from wheelchair.interfaces import Controller, ControllerInput


class EmulatedController(Controller):
    """
    Emulated controller that can be scripted or controlled via API.

    Useful for testing and automated scenarios.
    """

    def __init__(self):
        """Initialize emulated controller."""
        self._input = ControllerInput()
        self._connected = True
        self._script: List[ControllerInput] = []
        self._script_index = 0

    def read_input(self) -> ControllerInput:
        """
        Read current input from controller.

        Returns:
            ControllerInput with current state
        """
        # If script is active, advance through it
        if self._script and self._script_index < len(self._script):
            self._input = self._script[self._script_index]
            self._script_index += 1
        return self._input

    def is_connected(self) -> bool:
        """
        Check if controller is connected.

        Returns:
            True if connected
        """
        return self._connected

    def set_input(
        self,
        linear: float = 0.0,
        angular: float = 0.0,
        emergency_stop: bool = False,
        deadman_pressed: bool = False,
        mode_switch: bool = False,
    ) -> None:
        """
        Manually set controller input.

        Args:
            linear: Linear input (-1.0 to 1.0)
            angular: Angular input (-1.0 to 1.0)
            emergency_stop: Emergency stop button state
            deadman_pressed: Deadman switch state
            mode_switch: Mode switch button state
        """
        self._input = ControllerInput(
            linear=max(-1.0, min(1.0, linear)),
            angular=max(-1.0, min(1.0, angular)),
            emergency_stop=emergency_stop,
            deadman_pressed=deadman_pressed,
            mode_switch=mode_switch,
        )
        # Clear script when manual input is set
        self._script = []
        self._script_index = 0

    def load_script(self, script: List[ControllerInput]) -> None:
        """
        Load a scripted sequence of inputs.

        Args:
            script: List of ControllerInput to play back
        """
        self._script = script
        self._script_index = 0

    def reset_script(self) -> None:
        """Reset script playback to beginning."""
        self._script_index = 0

    def clear_script(self) -> None:
        """Clear the current script."""
        self._script = []
        self._script_index = 0
        self._input = ControllerInput()

    def disconnect(self) -> None:
        """Simulate controller disconnect."""
        self._connected = False
        self._input = ControllerInput()

    def connect(self) -> None:
        """Simulate controller connect."""
        self._connected = True
