"""
Base controller class
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional

# Import controller family support from emulator
try:
    from wheelchair.controller_families import (
        ControllerFamily,
        BaseControllerFamily,
        ControllerSignals,
        create_controller_family,
    )
    CONTROLLER_FAMILY_SUPPORT = True
except ImportError:
    CONTROLLER_FAMILY_SUPPORT = False
    ControllerFamily = None
    BaseControllerFamily = None


class Controller(ABC):
    """
    Base class for wheelchair controllers.
    
    Handles input from various controller types (joystick, gamepad, etc.)
    Supports controller family emulation for realistic hardware simulation.
    """
    
    def __init__(self, name: str, controller_family: Optional['ControllerFamily'] = None):
        """
        Initialize controller.
        
        Args:
            name: Name of the controller
            controller_family: Optional controller family for realistic hardware emulation
        """
        self.name = name
        self._deadzone = 0.1  # 10% deadzone by default
        
        # Controller family support
        self._controller_family: Optional['BaseControllerFamily'] = None
        if CONTROLLER_FAMILY_SUPPORT and controller_family is not None:
            self._controller_family = create_controller_family(controller_family)
            # Use family-specific deadzone
            chars = self._controller_family.get_signal_characteristics()
            if 'deadzone' in chars:
                # Extract numeric deadzone (e.g., "15.0%" -> 0.15)
                deadzone_str = chars['deadzone']
                if isinstance(deadzone_str, str) and '%' in deadzone_str:
                    self._deadzone = float(deadzone_str.rstrip('%')) / 100.0
        
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
    
    def get_controller_family(self) -> Optional['ControllerFamily']:
        """
        Get the current controller family.
        
        Returns:
            Controller family if set, None otherwise
        """
        if not CONTROLLER_FAMILY_SUPPORT or self._controller_family is None:
            return None
        return self._controller_family.family
    
    def get_signal_characteristics(self) -> Optional[dict]:
        """
        Get signal characteristics of the controller family.
        
        Returns:
            Dictionary with controller characteristics, or None if no family set
        """
        if not CONTROLLER_FAMILY_SUPPORT or self._controller_family is None:
            return None
        return self._controller_family.get_signal_characteristics()
        
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
