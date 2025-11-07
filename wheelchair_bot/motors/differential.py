"""
Differential drive motor controller
"""

from wheelchair_bot.motors.base import MotorController
from typing import Tuple


class DifferentialDriveController(MotorController):
    """
    Differential drive motor controller.
    
    Converts linear and angular velocity to left/right motor speeds.
    Used by most electric wheelchairs.
    """
    
    def __init__(self):
        """Initialize differential drive controller."""
        super().__init__("Differential_Drive")
        self._left_speed = 0.0
        self._right_speed = 0.0
        
    def set_velocity(self, linear: float, angular: float) -> None:
        """
        Set velocity using differential drive kinematics.
        
        Args:
            linear: Linear velocity (-1.0 to 1.0)
            angular: Angular velocity (-1.0 to 1.0)
        """
        # Differential drive: mix linear and angular velocities
        # Left motor = linear - angular
        # Right motor = linear + angular
        left = linear - angular
        right = linear + angular
        
        # Normalize if any value exceeds 1.0
        max_val = max(abs(left), abs(right))
        if max_val > 1.0:
            left /= max_val
            right /= max_val
        
        self.set_motor_speeds(left, right)
    
    def set_motor_speeds(self, left: float, right: float) -> None:
        """
        Set motor speeds directly.
        
        Args:
            left: Left motor speed (-1.0 to 1.0)
            right: Right motor speed (-1.0 to 1.0)
        """
        if not self._enabled:
            print("Warning: Motor controller is disabled")
            return
            
        self._left_speed = max(-1.0, min(1.0, left))
        self._right_speed = max(-1.0, min(1.0, right))
    
    def get_motor_speeds(self) -> Tuple[float, float]:
        """
        Get current motor speeds.
        
        Returns:
            Tuple of (left, right) motor speeds
        """
        return (self._left_speed, self._right_speed)
    
    def enable(self) -> None:
        """Enable motor controller."""
        self._enabled = True
        print("Motor controller enabled")
    
    def disable(self) -> None:
        """Disable motor controller and stop motors."""
        self._enabled = False
        self._left_speed = 0.0
        self._right_speed = 0.0
        print("Motor controller disabled")
    
    def get_velocity(self) -> Tuple[float, float]:
        """
        Get velocity from motor speeds.
        
        Returns:
            Tuple of (linear, angular) velocity
        """
        # Inverse differential drive kinematics
        linear = (self._left_speed + self._right_speed) / 2.0
        angular = (self._right_speed - self._left_speed) / 2.0
        return (linear, angular)
