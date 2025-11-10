"""
Gamepad controller implementation
"""

from wheelchair_bot.controllers.base import Controller, CONTROLLER_FAMILY_SUPPORT
from typing import Tuple, Optional
import time

if CONTROLLER_FAMILY_SUPPORT:
    from wheelchair.controller_families import ControllerFamily, ControllerSignals


class GamepadController(Controller):
    """
    Gamepad controller for wheelchairs (Xbox, PlayStation, etc.).
    
    Uses pygame for gamepad input handling.
    Supports controller family emulation for realistic wheelchair controller behavior.
    """
    
    def __init__(
        self,
        controller_id: int = 0,
        controller_family: Optional['ControllerFamily'] = None
    ):
        """
        Initialize gamepad controller.
        
        Args:
            controller_id: ID of the gamepad to use (default: 0)
            controller_family: Optional controller family for hardware emulation
        """
        super().__init__(f"Gamepad_{controller_id}", controller_family=controller_family)
        self.controller_id = controller_id
        self._joystick = None
        self._pygame_initialized = False
        
    def connect(self) -> bool:
        """
        Connect to the gamepad.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            import pygame
            
            if not self._pygame_initialized:
                pygame.init()
                pygame.joystick.init()
                self._pygame_initialized = True
            
            joystick_count = pygame.joystick.get_count()
            
            if joystick_count == 0:
                print("No gamepads detected")
                return False
                
            if self.controller_id >= joystick_count:
                print(f"Gamepad {self.controller_id} not found. Only {joystick_count} gamepad(s) available.")
                return False
            
            self._joystick = pygame.joystick.Joystick(self.controller_id)
            self._joystick.init()
            
            print(f"Connected to: {self._joystick.get_name()}")
            return True
            
        except ImportError:
            print("pygame not installed. Install with: pip install pygame")
            return False
        except Exception as e:
            print(f"Error connecting to gamepad: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the gamepad."""
        if self._joystick:
            self._joystick.quit()
            self._joystick = None
    
    def is_connected(self) -> bool:
        """
        Check if gamepad is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self._joystick is not None and self._joystick.get_init()
    
    def read_input(self) -> Tuple[float, float]:
        """
        Read input from gamepad.
        
        Uses left stick for movement:
        - Y-axis (vertical) for linear velocity
        - X-axis (horizontal) for angular velocity
        
        Returns:
            Tuple of (linear, angular) values normalized to -1.0 to 1.0
        """
        if not self.is_connected():
            return (0.0, 0.0)
        
        try:
            import pygame
            pygame.event.pump()  # Process event queue
            
            # Left stick: axis 0 = horizontal, axis 1 = vertical
            # Invert Y-axis (up is negative in pygame, we want up to be positive)
            linear = -self._joystick.get_axis(1)
            angular = self._joystick.get_axis(0)
            
            # If controller family is set, process through family
            if CONTROLLER_FAMILY_SUPPORT and self._controller_family is not None:
                chars = self._controller_family.get_signal_characteristics()
                
                # Convert normalized values to voltage based on family
                if 'voltage_range' in chars:
                    if '3.3V' in chars['voltage_range']:
                        # Shark/DX uses 0-3.3V with 1.65V center
                        axis_x_voltage = 1.65 + (angular * 1.65)
                        axis_y_voltage = 1.65 + (linear * 1.65)
                    else:
                        # Most use 0-5V with 2.5V center
                        axis_x_voltage = 2.5 + (angular * 2.5)
                        axis_y_voltage = 2.5 + (linear * 2.5)
                else:
                    # Default to 5V
                    axis_x_voltage = 2.5 + (angular * 2.5)
                    axis_y_voltage = 2.5 + (linear * 2.5)
                
                signals = ControllerSignals(
                    axis_x_voltage=axis_x_voltage,
                    axis_y_voltage=axis_y_voltage,
                    enable_line=True,  # Gamepad is always enabled when connected
                )
                controller_input = self._controller_family.process_signals(signals)
                return (controller_input.linear, controller_input.angular)
            
            # Legacy behavior: apply deadzone directly
            linear = self.apply_deadzone(linear)
            angular = self.apply_deadzone(angular)
            
            return (linear, angular)
            
        except Exception as e:
            print(f"Error reading gamepad input: {e}")
            return (0.0, 0.0)
    
    def get_button_state(self, button_id: int) -> bool:
        """
        Get state of a specific button.
        
        Args:
            button_id: Button ID to check
            
        Returns:
            True if button is pressed, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            import pygame
            pygame.event.pump()
            return self._joystick.get_button(button_id)
        except Exception:
            return False
