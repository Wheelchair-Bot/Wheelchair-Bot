"""Main wheelchair controller class."""

import logging
import time
from typing import Optional
from .motor_driver import MotorDriver, Direction

logger = logging.getLogger(__name__)


class WheelchairController:
    """
    Main controller for wheelchair robot.
    
    Provides high-level control interface for wheelchair movement
    with safety features and smooth control.
    """
    
    def __init__(self, 
                 motor_driver: Optional[MotorDriver] = None,
                 max_speed: int = 80,
                 turn_speed: int = 60,
                 acceleration_rate: int = 10):
        """
        Initialize wheelchair controller.
        
        Args:
            motor_driver: MotorDriver instance (creates default if None)
            max_speed: Maximum speed percentage (0-100)
            turn_speed: Speed for turning (0-100)
            acceleration_rate: Rate of speed change for smooth control
        """
        self.motor_driver = motor_driver or MotorDriver(use_mock=True)
        self.max_speed = max(0, min(100, max_speed))
        self.turn_speed = max(0, min(100, turn_speed))
        self.acceleration_rate = acceleration_rate
        
        self.current_left_speed = 0
        self.current_right_speed = 0
        self.is_running = False
        
        logger.info(f"Wheelchair controller initialized - Max speed: {self.max_speed}%")
    
    def move_forward(self, speed: Optional[int] = None):
        """
        Move wheelchair forward.
        
        Args:
            speed: Speed percentage (uses max_speed if None)
        """
        speed = speed or self.max_speed
        speed = max(0, min(100, speed))
        self.motor_driver.set_motor_speed(speed, speed)
        self.current_left_speed = speed
        self.current_right_speed = speed
        logger.info(f"Moving forward at {speed}% speed")
    
    def move_backward(self, speed: Optional[int] = None):
        """
        Move wheelchair backward.
        
        Args:
            speed: Speed percentage (uses max_speed if None)
        """
        speed = speed or self.max_speed
        speed = max(0, min(100, speed))
        self.motor_driver.set_motor_speed(-speed, -speed)
        self.current_left_speed = -speed
        self.current_right_speed = -speed
        logger.info(f"Moving backward at {speed}% speed")
    
    def turn_left(self, speed: Optional[int] = None):
        """
        Turn wheelchair left (in place).
        
        Args:
            speed: Turn speed percentage (uses turn_speed if None)
        """
        speed = speed or self.turn_speed
        speed = max(0, min(100, speed))
        self.motor_driver.set_motor_speed(-speed, speed)
        self.current_left_speed = -speed
        self.current_right_speed = speed
        logger.info(f"Turning left at {speed}% speed")
    
    def turn_right(self, speed: Optional[int] = None):
        """
        Turn wheelchair right (in place).
        
        Args:
            speed: Turn speed percentage (uses turn_speed if None)
        """
        speed = speed or self.turn_speed
        speed = max(0, min(100, speed))
        self.motor_driver.set_motor_speed(speed, -speed)
        self.current_left_speed = speed
        self.current_right_speed = -speed
        logger.info(f"Turning right at {speed}% speed")
    
    def stop(self):
        """Stop wheelchair movement."""
        self.motor_driver.stop()
        self.current_left_speed = 0
        self.current_right_speed = 0
        logger.info("Wheelchair stopped")
    
    def emergency_stop(self):
        """Emergency stop - immediate halt."""
        logger.warning("EMERGENCY STOP activated")
        self.stop()
    
    def move(self, direction: Direction, speed: Optional[int] = None):
        """
        Move wheelchair in specified direction.
        
        Args:
            direction: Direction to move
            speed: Speed percentage (optional)
        """
        if direction == Direction.FORWARD:
            self.move_forward(speed)
        elif direction == Direction.BACKWARD:
            self.move_backward(speed)
        elif direction == Direction.LEFT:
            self.turn_left(speed)
        elif direction == Direction.RIGHT:
            self.turn_right(speed)
        elif direction == Direction.STOP:
            self.stop()
        else:
            logger.error(f"Unknown direction: {direction}")
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop()
        self.motor_driver.cleanup()
        logger.info("Controller cleanup completed")
