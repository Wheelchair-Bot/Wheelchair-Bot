"""
Example: Basic wheelchair control with gamepad
"""

from wheelchair_bot.wheelchairs.models import QuantumQ6Edge
from wheelchair_bot.controllers.gamepad import GamepadController
from wheelchair_bot.motors.differential import DifferentialDriveController
from wheelchair_bot.system import WheelchairControlSystem


def main():
    """Run basic wheelchair control example."""
    
    # Create wheelchair instance
    wheelchair = QuantumQ6Edge()
    print(f"Wheelchair: {wheelchair.name}")
    print(f"Max Speed: {wheelchair.max_speed} m/s")
    
    # Create controller
    controller = GamepadController(controller_id=0)
    
    # Create motor controller
    motor_controller = DifferentialDriveController()
    
    # Create control system
    control_system = WheelchairControlSystem(
        wheelchair=wheelchair,
        controller=controller,
        motor_controller=motor_controller,
    )
    
    # Configure safety settings
    control_system.speed_limiter.set_max_linear(0.5)  # 50% max speed
    control_system.speed_limiter.set_max_angular(0.5)
    
    print("\nStarting control system...")
    print("Use gamepad left stick to control wheelchair")
    print("Press Ctrl+C to stop\n")
    
    # Run the control system
    control_system.run()


if __name__ == "__main__":
    main()
