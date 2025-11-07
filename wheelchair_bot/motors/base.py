"""
Base motor controller class
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict


class MotorController(ABC):
    """
    Base class for motor controllers.
    
    Handles conversion of velocity commands to motor outputs.
    """
    
    def __init__(self, name: str):
        """
        Initialize motor controller.
        
        Args:
            name: Name of the motor controller
        """
        self.name = name
        self._enabled = False
        
    @abstractmethod
    def set_motor_speeds(self, left: float, right: float) -> None:
        """
        Set motor speeds.
        
        Args:
            left: Left motor speed (-1.0 to 1.0)
            right: Right motor speed (-1.0 to 1.0)
        """
        pass
    
    @abstractmethod
    def get_motor_speeds(self) -> Tuple[float, float]:
        """
        Get current motor speeds.
        
        Returns:
            Tuple of (left, right) motor speeds
        """
        pass
    
    @abstractmethod
    def enable(self) -> None:
        """Enable motor controller."""
        pass
    
    @abstractmethod
    def disable(self) -> None:
        """Disable motor controller."""
        pass
    
    def is_enabled(self) -> bool:
        """
        Check if motor controller is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self._enabled
    
    def emergency_stop(self) -> None:
        """Emergency stop - immediately halt all motors."""
        self.set_motor_speeds(0.0, 0.0)
        self.disable()
