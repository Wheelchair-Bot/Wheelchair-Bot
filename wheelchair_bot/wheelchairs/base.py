"""
Base wheelchair class
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional


class Wheelchair(ABC):
    """
    Base class for electric wheelchair interfaces.
    
    Represents a wheelchair with its physical properties and motor control.
    """
    
    def __init__(
        self,
        name: str,
        max_speed: float,
        wheel_base: float,
        wheel_diameter: float,
    ):
        """
        Initialize wheelchair.
        
        Args:
            name: Name/model of the wheelchair
            max_speed: Maximum speed in meters per second
            wheel_base: Distance between wheels in meters
            wheel_diameter: Wheel diameter in meters
        """
        self.name = name
        self.max_speed = max_speed
        self.wheel_base = wheel_base
        self.wheel_diameter = wheel_diameter
        self._current_speed = 0.0
        self._current_direction = 0.0
        
    @abstractmethod
    def get_motor_config(self) -> Dict:
        """
        Get motor configuration for this wheelchair model.
        
        Returns:
            Dictionary containing motor configuration
        """
        pass
    
    def set_velocity(self, linear: float, angular: float) -> None:
        """
        Set wheelchair velocity.
        
        Args:
            linear: Linear velocity (-1.0 to 1.0, normalized)
            angular: Angular velocity (-1.0 to 1.0, normalized)
        """
        self._current_speed = max(-1.0, min(1.0, linear))
        self._current_direction = max(-1.0, min(1.0, angular))
        
    def get_velocity(self) -> Tuple[float, float]:
        """
        Get current wheelchair velocity.
        
        Returns:
            Tuple of (linear, angular) velocity
        """
        return (self._current_speed, self._current_direction)
    
    def stop(self) -> None:
        """Emergency stop the wheelchair."""
        self._current_speed = 0.0
        self._current_direction = 0.0
        
    def get_info(self) -> Dict:
        """
        Get wheelchair information.
        
        Returns:
            Dictionary containing wheelchair specifications
        """
        return {
            "name": self.name,
            "max_speed": self.max_speed,
            "wheel_base": self.wheel_base,
            "wheel_diameter": self.wheel_diameter,
        }
