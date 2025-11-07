"""
Base controller class
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional


class Controller(ABC):
    """
    Base class for wheelchair controllers.
    
    Handles input from various controller types (joystick, gamepad, etc.)
    """
    
    def __init__(self, name: str):
        """
        Initialize controller.
        
        Args:
            name: Name of the controller
        """
        self.name = name
        self._deadzone = 0.1  # 10% deadzone by default
        
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the controller.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the controller."""
        pass
    
    @abstractmethod
    def read_input(self) -> Tuple[float, float]:
        """
        Read input from controller.
        
        Returns:
            Tuple of (linear, angular) values normalized to -1.0 to 1.0
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if controller is connected.
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    def set_deadzone(self, deadzone: float) -> None:
        """
        Set controller deadzone.
        
        Args:
            deadzone: Deadzone value (0.0 to 1.0)
        """
        self._deadzone = max(0.0, min(1.0, deadzone))
        
    def apply_deadzone(self, value: float) -> float:
        """
        Apply deadzone to controller input.
        
        Args:
            value: Raw input value
            
        Returns:
            Value with deadzone applied
        """
        if abs(value) < self._deadzone:
            return 0.0
        # Scale the value to maintain smooth transition
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self._deadzone) / (1.0 - self._deadzone)
        return sign * scaled
