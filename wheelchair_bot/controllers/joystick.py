"""
Joystick controller implementation
"""

from wheelchair_bot.controllers.base import Controller, CONTROLLER_FAMILY_SUPPORT
from typing import Tuple, Optional

if CONTROLLER_FAMILY_SUPPORT:
    from wheelchair.controller_families import ControllerFamily, ControllerSignals


class JoystickController(Controller):
    """
    Joystick controller for wheelchairs.
    
    This is a wrapper that can work with various joystick types.
    For actual hardware integration, this would interface with
    specific joystick hardware (e.g., via serial, I2C, or ADC).
    
    Supports controller family emulation for realistic wheelchair controller behavior.
    """
    
    def __init__(
        self,
        joystick_type: str = "analog",
        controller_family: Optional['ControllerFamily'] = None
    ):
        """
        Initialize joystick controller.
        
        Args:
            joystick_type: Type of joystick ("analog", "digital", etc.)
            controller_family: Optional controller family for hardware emulation
        """
        super().__init__(f"Joystick_{joystick_type}", controller_family=controller_family)
        self.joystick_type = joystick_type
        self._connected = False
        self._linear = 0.0
        self._angular = 0.0
        
        # Raw signal values for controller family processing
        self._axis_x_voltage = 2.5
        self._axis_y_voltage = 2.5
        self._enable_line = False
        self._speed_pot_voltage = 5.0
        
    def connect(self) -> bool:
        """
        Connect to the joystick.
        
        Returns:
            True if connection successful, False otherwise
        """
        # In a real implementation, this would initialize hardware interfaces
        # For now, we'll simulate a successful connection
        print(f"Connecting to {self.joystick_type} joystick...")
        self._connected = True
        return True
    
    def disconnect(self) -> None:
        """Disconnect from the joystick."""
        self._connected = False
        self._linear = 0.0
        self._angular = 0.0
        
    def is_connected(self) -> bool:
        """
        Check if joystick is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected
    
    def read_input(self) -> Tuple[float, float]:
        """
        Read input from joystick.
        
        Returns:
            Tuple of (linear, angular) values normalized to -1.0 to 1.0
        """
        if not self.is_connected():
            return (0.0, 0.0)
        
        # If controller family is set, process through family
        if CONTROLLER_FAMILY_SUPPORT and self._controller_family is not None:
            signals = ControllerSignals(
                axis_x_voltage=self._axis_x_voltage,
                axis_y_voltage=self._axis_y_voltage,
                enable_line=self._enable_line,
                speed_pot_voltage=self._speed_pot_voltage,
            )
            controller_input = self._controller_family.process_signals(signals)
            return (controller_input.linear, controller_input.angular)
        
        # Legacy behavior: apply deadzone directly
        linear = self.apply_deadzone(self._linear)
        angular = self.apply_deadzone(self._angular)
        
        return (linear, angular)
    
    def set_input(self, linear: float, angular: float) -> None:
        """
        Set joystick input (for testing/simulation).
        
        Args:
            linear: Linear velocity (-1.0 to 1.0)
            angular: Angular velocity (-1.0 to 1.0)
        """
        self._linear = max(-1.0, min(1.0, linear))
        self._angular = max(-1.0, min(1.0, angular))
        
        # Update voltage signals for controller family processing
        if CONTROLLER_FAMILY_SUPPORT and self._controller_family is not None:
            chars = self._controller_family.get_signal_characteristics()
            # Map normalized values to voltage based on family
            if 'voltage_range' in chars:
                if '3.3V' in chars['voltage_range']:
                    # Shark/DX uses 0-3.3V with 1.65V center
                    self._axis_x_voltage = 1.65 + (angular * 1.65)
                    self._axis_y_voltage = 1.65 + (linear * 1.65)
                else:
                    # Most use 0-5V with 2.5V center
                    self._axis_x_voltage = 2.5 + (angular * 2.5)
                    self._axis_y_voltage = 2.5 + (linear * 2.5)
    
    def set_raw_signals(
        self,
        axis_x_voltage: float = 2.5,
        axis_y_voltage: float = 2.5,
        enable_line: bool = False,
        speed_pot_voltage: float = 5.0,
    ) -> None:
        """
        Set raw hardware signals for controller family processing.
        
        Args:
            axis_x_voltage: X-axis voltage (for angular movement)
            axis_y_voltage: Y-axis voltage (for linear movement)
            enable_line: Enable/deadman switch state
            speed_pot_voltage: Speed potentiometer voltage (VR2 family)
        """
        self._axis_x_voltage = axis_x_voltage
        self._axis_y_voltage = axis_y_voltage
        self._enable_line = enable_line
        self._speed_pot_voltage = speed_pot_voltage
    
    def read_raw_values(self) -> Tuple[float, float]:
        """
        Read raw ADC values from joystick hardware.
        
        In a real implementation, this would read from ADC pins.
        
        Returns:
            Tuple of (x_axis, y_axis) raw values
        """
        # Placeholder for hardware integration
        # In real implementation: read from ADC, I2C, or serial interface
        return (self._angular, self._linear)
