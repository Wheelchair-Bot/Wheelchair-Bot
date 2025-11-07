"""
Example: Testing with simulated joystick
"""

from wheelchair_bot.wheelchairs.models import PrideJazzy
from wheelchair_bot.controllers.joystick import JoystickController
from wheelchair_bot.motors.differential import DifferentialDriveController
from wheelchair_bot.system import WheelchairControlSystem
import time


def main():
    """Run simulated control example."""
    
    # Create wheelchair instance
    wheelchair = PrideJazzy()
    print(f"Wheelchair: {wheelchair.name}")
    
    # Create joystick controller
    controller = JoystickController(joystick_type="analog")
    
    # Create motor controller
    motor_controller = DifferentialDriveController()
    
    # Create control system
    control_system = WheelchairControlSystem(
        wheelchair=wheelchair,
        controller=controller,
        motor_controller=motor_controller,
    )
    
    # Start the system
    if not control_system.start():
        print("Failed to start control system")
        return
    
    print("\nRunning simulation...")
    
    # Simulate different movements
    movements = [
        ("Forward", 0.5, 0.0, 2.0),
        ("Turn Right", 0.3, 0.5, 2.0),
        ("Turn Left", 0.3, -0.5, 2.0),
        ("Backward", -0.5, 0.0, 2.0),
        ("Stop", 0.0, 0.0, 1.0),
    ]
    
    try:
        for name, linear, angular, duration in movements:
            print(f"\n{name}: linear={linear:.2f}, angular={angular:.2f}")
            
            # Set joystick input
            controller.set_input(linear, angular)
            
            # Run for duration
            start = time.time()
            while time.time() - start < duration:
                control_system.deadman_switch.confirm()
                control_system.update()
                
                # Print status
                status = control_system.get_status()
                vel = status["velocity"]
                motors = status["motor_speeds"]
                print(f"  Vel: L={vel['linear']:.2f} A={vel['angular']:.2f} | "
                      f"Motors: L={motors['left']:.2f} R={motors['right']:.2f}", end="\r")
                
                time.sleep(0.1)
            
            print()  # New line after movement
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        control_system.stop()
    
    print("\nSimulation complete")


if __name__ == "__main__":
    main()
