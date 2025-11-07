"""Keyboard control interface for wheelchair controller."""

import logging
import sys
import time
from typing import Optional

logger = logging.getLogger(__name__)


class KeyboardControl:
    """Keyboard control interface for wheelchair."""
    
    def __init__(self, controller):
        """
        Initialize keyboard control.
        
        Args:
            controller: WheelchairController instance
        """
        self.controller = controller
        self.running = False
    
    def print_instructions(self):
        """Print control instructions."""
        print("\n" + "="*50)
        print("Wheelchair Controller - Keyboard Control")
        print("="*50)
        print("Controls:")
        print("  W/w - Move Forward")
        print("  S/s - Move Backward")
        print("  A/a - Turn Left")
        print("  D/d - Turn Right")
        print("  Space - Stop")
        print("  Q/q - Quit")
        print("="*50 + "\n")
    
    def run(self):
        """Run keyboard control loop."""
        self.print_instructions()
        self.running = True
        
        try:
            # Try to use keyboard library if available
            import keyboard
            self._run_with_keyboard_lib()
        except ImportError:
            logger.info("keyboard library not available, using basic input mode")
            self._run_with_input()
    
    def _run_with_input(self):
        """Run control using basic input (works without keyboard library)."""
        print("Enter command (w/s/a/d/space/q): ")
        
        while self.running:
            try:
                command = input("> ").lower().strip()
                
                if command == 'w':
                    print("Moving forward...")
                    self.controller.move_forward()
                elif command == 's':
                    print("Moving backward...")
                    self.controller.move_backward()
                elif command == 'a':
                    print("Turning left...")
                    self.controller.turn_left()
                elif command == 'd':
                    print("Turning right...")
                    self.controller.turn_right()
                elif command == ' ' or command == '':
                    print("Stopping...")
                    self.controller.stop()
                elif command == 'q':
                    print("Quitting...")
                    self.running = False
                else:
                    print(f"Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print("\nKeyboard interrupt received")
                self.running = False
            except EOFError:
                self.running = False
    
    def _run_with_keyboard_lib(self):
        """Run control using keyboard library (real-time key detection)."""
        import keyboard
        
        print("Real-time keyboard control active. Press Q to quit.")
        print("Hold keys for continuous movement.\n")
        
        last_key = None
        
        try:
            while self.running:
                if keyboard.is_pressed('q'):
                    print("Quitting...")
                    self.running = False
                    break
                elif keyboard.is_pressed('w'):
                    if last_key != 'w':
                        print("Moving forward...")
                        self.controller.move_forward()
                        last_key = 'w'
                elif keyboard.is_pressed('s'):
                    if last_key != 's':
                        print("Moving backward...")
                        self.controller.move_backward()
                        last_key = 's'
                elif keyboard.is_pressed('a'):
                    if last_key != 'a':
                        print("Turning left...")
                        self.controller.turn_left()
                        last_key = 'a'
                elif keyboard.is_pressed('d'):
                    if last_key != 'd':
                        print("Turning right...")
                        self.controller.turn_right()
                        last_key = 'd'
                elif keyboard.is_pressed('space'):
                    if last_key != 'space':
                        print("Stopping...")
                        self.controller.stop()
                        last_key = 'space'
                else:
                    if last_key is not None:
                        self.controller.stop()
                        last_key = None
                
                time.sleep(0.05)  # Small delay to prevent CPU spinning
                
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        
        self.controller.stop()
    
    def cleanup(self):
        """Cleanup resources."""
        self.running = False
        self.controller.stop()
