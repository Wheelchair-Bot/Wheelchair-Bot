"""
Speed and acceleration limiters for safety
"""

from typing import Tuple
import time


class SpeedLimiter:
    """
    Limits maximum speed for safety.
    """
    
    def __init__(self, max_linear: float = 1.0, max_angular: float = 1.0):
        """
        Initialize speed limiter.
        
        Args:
            max_linear: Maximum linear speed (0.0 to 1.0)
            max_angular: Maximum angular speed (0.0 to 1.0)
        """
        self.max_linear = max(0.0, min(1.0, max_linear))
        self.max_angular = max(0.0, min(1.0, max_angular))
    
    def limit(self, linear: float, angular: float) -> Tuple[float, float]:
        """
        Apply speed limits.
        
        Args:
            linear: Desired linear velocity
            angular: Desired angular velocity
            
        Returns:
            Tuple of limited (linear, angular) velocities
        """
        limited_linear = max(-self.max_linear, min(self.max_linear, linear))
        limited_angular = max(-self.max_angular, min(self.max_angular, angular))
        return (limited_linear, limited_angular)
    
    def set_max_linear(self, max_linear: float) -> None:
        """Set maximum linear speed."""
        self.max_linear = max(0.0, min(1.0, max_linear))
    
    def set_max_angular(self, max_angular: float) -> None:
        """Set maximum angular speed."""
        self.max_angular = max(0.0, min(1.0, max_angular))


class AccelerationLimiter:
    """
    Limits acceleration rate for smooth control.
    """
    
    def __init__(self, max_linear_accel: float = 0.5, max_angular_accel: float = 0.5):
        """
        Initialize acceleration limiter.
        
        Args:
            max_linear_accel: Maximum linear acceleration per second
            max_angular_accel: Maximum angular acceleration per second
        """
        self.max_linear_accel = max_linear_accel
        self.max_angular_accel = max_angular_accel
        self._last_linear = 0.0
        self._last_angular = 0.0
        self._last_time = time.time()
    
    def limit(self, linear: float, angular: float) -> Tuple[float, float]:
        """
        Apply acceleration limits.
        
        Args:
            linear: Desired linear velocity
            angular: Desired angular velocity
            
        Returns:
            Tuple of acceleration-limited (linear, angular) velocities
        """
        current_time = time.time()
        dt = current_time - self._last_time
        
        if dt <= 0:
            dt = 0.01  # Minimum time step
        
        # Calculate maximum change allowed
        max_linear_change = self.max_linear_accel * dt
        max_angular_change = self.max_angular_accel * dt
        
        # Limit linear acceleration
        linear_diff = linear - self._last_linear
        if abs(linear_diff) > max_linear_change:
            linear_sign = 1.0 if linear_diff > 0 else -1.0
            limited_linear = self._last_linear + linear_sign * max_linear_change
        else:
            limited_linear = linear
        
        # Limit angular acceleration
        angular_diff = angular - self._last_angular
        if abs(angular_diff) > max_angular_change:
            angular_sign = 1.0 if angular_diff > 0 else -1.0
            limited_angular = self._last_angular + angular_sign * max_angular_change
        else:
            limited_angular = angular
        
        # Update state
        self._last_linear = limited_linear
        self._last_angular = limited_angular
        self._last_time = current_time
        
        return (limited_linear, limited_angular)
    
    def reset(self) -> None:
        """Reset the limiter state."""
        self._last_linear = 0.0
        self._last_angular = 0.0
        self._last_time = time.time()
