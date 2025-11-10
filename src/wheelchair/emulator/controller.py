"""Emulated controller input."""

from typing import List, Optional
from wheelchair.interfaces import Controller, ControllerInput
from wheelchair.controller_families import (
    ControllerFamily,
    BaseControllerFamily,
    ControllerSignals,
    create_controller_family,
)


class EmulatedController(Controller):
    """
    Emulated controller that can be scripted or controlled via API.

    Supports different controller families (R-Net, VR2, Shark, LiNX, Q-Logic)
    for realistic simulation of commercial wheelchair controllers.

    Useful for testing and automated scenarios.
    """

    def __init__(self, controller_family: Optional[ControllerFamily] = None):
        """Initialize emulated controller.

        Args:
            controller_family: Optional controller family to emulate.
                             If None, uses direct input mode (legacy behavior).
        """
        self._input = ControllerInput()
        self._connected = True
        self._script: List[ControllerInput] = []
        self._script_index = 0

        # Controller family support
        self._controller_family: Optional[BaseControllerFamily] = None
        self._signals = ControllerSignals()
        if controller_family is not None:
            self.set_controller_family(controller_family)

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

        # If controller family is set, process signals through it
        if self._controller_family is not None:
            self._input = self._controller_family.process_signals(self._signals)

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

    def set_controller_family(self, family: ControllerFamily) -> None:
        """Set the controller family to emulate.

        Args:
            family: Controller family to emulate
        """
        self._controller_family = create_controller_family(family)
        self._signals = ControllerSignals()

    def get_controller_family(self) -> Optional[ControllerFamily]:
        """Get the current controller family.

        Returns:
            Current controller family, or None if not set
        """
        return self._controller_family.family if self._controller_family else None

    def set_raw_signals(
        self,
        axis_x_voltage: float = 2.5,
        axis_y_voltage: float = 2.5,
        enable_line: bool = False,
        mode_button: bool = False,
        emergency_stop: bool = False,
        speed_pot_voltage: float = 5.0,
        profile_select: int = 0,
        bus_data: Optional[dict] = None,
    ) -> None:
        """Set raw controller signals for family-based processing.

        This simulates the raw hardware signals that would come from
        a real controller. Only applies when a controller family is set.

        Args:
            axis_x_voltage: X-axis voltage (default 2.5V = center)
            axis_y_voltage: Y-axis voltage (default 2.5V = center)
            enable_line: Enable/deadman switch state
            mode_button: Mode button state
            emergency_stop: Emergency stop button state
            speed_pot_voltage: Speed potentiometer voltage (default 5.0V = max)
            profile_select: Drive profile selector (0-3)
            bus_data: Digital bus data for LiNX/Q-Logic controllers
        """
        self._signals = ControllerSignals(
            axis_x_voltage=axis_x_voltage,
            axis_y_voltage=axis_y_voltage,
            enable_line=enable_line,
            mode_button=mode_button,
            emergency_stop=emergency_stop,
            speed_pot_voltage=speed_pot_voltage,
            profile_select=profile_select,
            bus_data=bus_data,
        )
        # Clear script when raw signals are set
        self._script = []
        self._script_index = 0

    def get_signal_characteristics(self) -> Optional[dict]:
        """Get characteristics of the current controller family.

        Returns:
            Dictionary with controller family characteristics, or None if no family set
        """
        if self._controller_family is None:
            return None
        return self._controller_family.get_signal_characteristics()

