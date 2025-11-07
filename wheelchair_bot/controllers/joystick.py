"""
Joystick controller implementation
"""

from wheelchair_bot.controllers.base import Controller
from typing import Tuple


class JoystickController(Controller):
    """
    Joystick controller for wheelchairs.
    
    This is a wrapper that can work with various joystick types.
    For actual hardware integration, this would interface with
    specific joystick hardware (e.g., via serial, I2C, or ADC).
    """
    
    def __init__(self, joystick_type: str = "analog"):
        """
        Initialize joystick controller.
        
        Args:
            joystick_type: Type of joystick ("analog", "digital", etc.)
        """
        super().__init__(f"Joystick_{joystick_type}")
        self.joystick_type = joystick_type
        self._connected = False
        self._linear = 0.0
        self._angular = 0.0
        
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
        
        # Apply deadzone
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
