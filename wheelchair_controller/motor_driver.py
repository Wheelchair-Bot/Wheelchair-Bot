"""Motor driver interface for controlling wheelchair motors via GPIO."""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class Direction(Enum):
    """Motor direction enumeration."""
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"


class MotorDriver:
    """
    Motor driver class for controlling wheelchair motors.
    
    This class interfaces with GPIO pins on Raspberry Pi to control
    two DC motors for differential drive wheelchair control.
    """
    
    def __init__(self, 
                 left_forward_pin: int = 17,
                 left_backward_pin: int = 18,
                 right_forward_pin: int = 22,
                 right_backward_pin: int = 23,
                 left_enable_pin: int = 12,
                 right_enable_pin: int = 13,
                 use_mock: bool = False):
        """
        Initialize motor driver.
        
        Args:
            left_forward_pin: GPIO pin for left motor forward
            left_backward_pin: GPIO pin for left motor backward
            right_forward_pin: GPIO pin for right motor forward
            right_backward_pin: GPIO pin for right motor backward
            left_enable_pin: GPIO pin for left motor PWM enable
            right_enable_pin: GPIO pin for right motor PWM enable
            use_mock: Use mock GPIO for testing (default: False)
        """
        self.use_mock = use_mock
        self.left_forward = left_forward_pin
        self.left_backward = left_backward_pin
        self.right_forward = right_forward_pin
        self.right_backward = right_backward_pin
        self.left_enable = left_enable_pin
        self.right_enable = right_enable_pin
        
        self.left_pwm = None
        self.right_pwm = None
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Setup GPIO pins for motor control."""
        try:
            if not self.use_mock:
                import RPi.GPIO as GPIO
                self.GPIO = GPIO
                self.GPIO.setmode(GPIO.BCM)
            else:
                # Use mock GPIO for testing
                from unittest.mock import MagicMock
                self.GPIO = MagicMock()
                logger.info("Using mock GPIO interface")
            
            # Setup motor control pins as outputs
            self.GPIO.setup(self.left_forward, self.GPIO.OUT)
            self.GPIO.setup(self.left_backward, self.GPIO.OUT)
            self.GPIO.setup(self.right_forward, self.GPIO.OUT)
            self.GPIO.setup(self.right_backward, self.GPIO.OUT)
            self.GPIO.setup(self.left_enable, self.GPIO.OUT)
            self.GPIO.setup(self.right_enable, self.GPIO.OUT)
            
            # Setup PWM for speed control
            self.left_pwm = self.GPIO.PWM(self.left_enable, 1000)
            self.right_pwm = self.GPIO.PWM(self.right_enable, 1000)
            self.left_pwm.start(0)
            self.right_pwm.start(0)
            
            logger.info("GPIO setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup GPIO: {e}")
            if not self.use_mock:
                raise
    
    def set_motor_speed(self, left_speed: int, right_speed: int):
        """
        Set speed for both motors.
        
        Args:
            left_speed: Speed for left motor (-100 to 100)
            right_speed: Speed for right motor (-100 to 100)
        """
        # Clamp speeds to valid range
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        # Set left motor
        if left_speed > 0:
            self.GPIO.output(self.left_forward, self.GPIO.HIGH)
            self.GPIO.output(self.left_backward, self.GPIO.LOW)
            self.left_pwm.ChangeDutyCycle(abs(left_speed))
        elif left_speed < 0:
            self.GPIO.output(self.left_forward, self.GPIO.LOW)
            self.GPIO.output(self.left_backward, self.GPIO.HIGH)
            self.left_pwm.ChangeDutyCycle(abs(left_speed))
        else:
            self.GPIO.output(self.left_forward, self.GPIO.LOW)
            self.GPIO.output(self.left_backward, self.GPIO.LOW)
            self.left_pwm.ChangeDutyCycle(0)
        
        # Set right motor
        if right_speed > 0:
            self.GPIO.output(self.right_forward, self.GPIO.HIGH)
            self.GPIO.output(self.right_backward, self.GPIO.LOW)
            self.right_pwm.ChangeDutyCycle(abs(right_speed))
        elif right_speed < 0:
            self.GPIO.output(self.right_forward, self.GPIO.LOW)
            self.GPIO.output(self.right_backward, self.GPIO.HIGH)
            self.right_pwm.ChangeDutyCycle(abs(right_speed))
        else:
            self.GPIO.output(self.right_forward, self.GPIO.LOW)
            self.GPIO.output(self.right_backward, self.GPIO.LOW)
            self.right_pwm.ChangeDutyCycle(0)
        
        logger.debug(f"Motor speeds set - Left: {left_speed}, Right: {right_speed}")
    
    def stop(self):
        """Stop both motors."""
        self.set_motor_speed(0, 0)
        logger.info("Motors stopped")
    
    def cleanup(self):
        """Cleanup GPIO resources."""
        self.stop()
        if self.left_pwm:
            self.left_pwm.stop()
        if self.right_pwm:
            self.right_pwm.stop()
        if not self.use_mock:
            self.GPIO.cleanup()
        logger.info("GPIO cleanup completed")
