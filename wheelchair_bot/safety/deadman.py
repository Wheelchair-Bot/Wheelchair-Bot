"""
Deadman switch for safety
"""

import time


class DeadmanSwitch:
    """
    Deadman switch that requires periodic confirmation.
    
    If not confirmed within timeout period, triggers emergency stop.
    """
    
    def __init__(self, timeout: float = 0.5):
        """
        Initialize deadman switch.
        
        Args:
            timeout: Timeout in seconds before triggering
        """
        self.timeout = timeout
        self._last_confirm_time = time.time()
        self._active = False
    
    def confirm(self) -> None:
        """Confirm that operator is in control."""
        self._last_confirm_time = time.time()
        self._active = True
    
    def is_active(self) -> bool:
        """
        Check if deadman switch is active.
        
        Returns:
            True if active, False if timed out
        """
        if not self._active:
            return False
            
        elapsed = time.time() - self._last_confirm_time
        if elapsed > self.timeout:
            self._active = False
            return False
        
        return True
    
    def reset(self) -> None:
        """Reset the deadman switch."""
        self._active = False
        self._last_confirm_time = time.time()
    
    def set_timeout(self, timeout: float) -> None:
        """
        Set timeout period.
        
        Args:
            timeout: Timeout in seconds
        """
        self.timeout = max(0.1, timeout)
