"""
Main wheelchair control system integration
"""

from wheelchair_bot.wheelchairs.base import Wheelchair
from wheelchair_bot.controllers.base import Controller
from wheelchair_bot.motors.base import MotorController
from wheelchair_bot.safety.limiter import SpeedLimiter, AccelerationLimiter
from wheelchair_bot.safety.deadman import DeadmanSwitch
from typing import Optional
import time


class WheelchairControlSystem:
    """
    Main wheelchair control system.
    
    Integrates wheelchair model, controller input, motor control, and safety features.
    """
    
    def __init__(
        self,
        wheelchair: Wheelchair,
        controller: Controller,
        motor_controller: MotorController,
    ):
        """
        Initialize wheelchair control system.
        
        Args:
            wheelchair: Wheelchair model instance
            controller: Controller input instance
            motor_controller: Motor controller instance
        """
        self.wheelchair = wheelchair
        self.controller = controller
        self.motor_controller = motor_controller
        
        # Safety features
        self.speed_limiter = SpeedLimiter(max_linear=0.8, max_angular=0.8)
        self.accel_limiter = AccelerationLimiter(max_linear_accel=1.0, max_angular_accel=1.0)
        self.deadman_switch = DeadmanSwitch(timeout=0.5)
        
        self._running = False
        self._emergency_stop = False
    
    def start(self) -> bool:
        """
        Start the control system.
        
        Returns:
            True if started successfully, False otherwise
        """
        # Connect controller
        if not self.controller.connect():
            print("Failed to connect controller")
            return False
        
        # Enable motors
        self.motor_controller.enable()
        
        self._running = True
        self._emergency_stop = False
        print(f"Control system started for {self.wheelchair.name}")
        return True
    
    def stop(self) -> None:
        """Stop the control system."""
        self._running = False
        self.wheelchair.stop()
        self.motor_controller.disable()
        self.controller.disconnect()
        print("Control system stopped")
    
    def emergency_stop_trigger(self) -> None:
        """Trigger emergency stop."""
        self._emergency_stop = True
        self.wheelchair.stop()
        self.motor_controller.emergency_stop()
        print("EMERGENCY STOP ACTIVATED")
    
    def update(self) -> None:
        """
        Update control system (call this in your main loop).
        """
        if not self._running or self._emergency_stop:
            return
        
        # Check deadman switch
        if not self.deadman_switch.is_active():
            print("Deadman switch inactive - stopping")
            self.wheelchair.stop()
            self.motor_controller.set_motor_speeds(0.0, 0.0)
            return
        
        # Read controller input
        linear, angular = self.controller.read_input()
        
        # Apply safety limits
        linear, angular = self.speed_limiter.limit(linear, angular)
        linear, angular = self.accel_limiter.limit(linear, angular)
        
        # Update wheelchair velocity
        self.wheelchair.set_velocity(linear, angular)
        
        # Convert to motor commands
        self.motor_controller.set_velocity(linear, angular)
    
    def run(self, duration: Optional[float] = None) -> None:
        """
        Run the control system.
        
        Args:
            duration: How long to run in seconds (None = run indefinitely)
        """
        if not self.start():
            return
        
        start_time = time.time()
        
        try:
            print("Control system running. Press Ctrl+C to stop.")
            while self._running:
                # Confirm deadman switch
                self.deadman_switch.confirm()
                
                # Update control
                self.update()
                
                # Check duration
                if duration is not None and (time.time() - start_time) >= duration:
                    break
                
                # Small delay to prevent CPU spinning
                time.sleep(0.02)  # 50Hz update rate
                
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.stop()
    
    def get_status(self) -> dict:
        """
        Get current system status.
        
        Returns:
            Dictionary with system status information
        """
        linear, angular = self.wheelchair.get_velocity()
        left_motor, right_motor = self.motor_controller.get_motor_speeds()
        
        return {
            "running": self._running,
            "emergency_stop": self._emergency_stop,
            "wheelchair": self.wheelchair.get_info(),
            "controller_connected": self.controller.is_connected(),
            "motors_enabled": self.motor_controller.is_enabled(),
            "velocity": {
                "linear": linear,
                "angular": angular,
            },
            "motor_speeds": {
                "left": left_motor,
                "right": right_motor,
            },
            "deadman_active": self.deadman_switch.is_active(),
        }
