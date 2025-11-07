#!/usr/bin/env python3
"""Demo script showing basic wheelchair controller functionality."""

import time
import logging
from wheelchair_controller import WheelchairController, MotorDriver

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_demo():
    """Run a demonstration of wheelchair controller capabilities."""
    
    print("\n" + "="*60)
    print("Wheelchair Controller Demo")
    print("="*60)
    print("\nThis demo will show basic movement patterns.")
    print("Using MOCK GPIO - safe to run without hardware.\n")
    
    # Initialize with mock GPIO
    motor_driver = MotorDriver(use_mock=True)
    controller = WheelchairController(
        motor_driver=motor_driver,
        max_speed=70,
        turn_speed=50
    )
    
    try:
        # Demo sequence
        movements = [
            ("Forward", lambda: controller.move_forward(50), 2),
            ("Stop", controller.stop, 1),
            ("Backward", lambda: controller.move_backward(50), 2),
            ("Stop", controller.stop, 1),
            ("Turn Left", lambda: controller.turn_left(), 2),
            ("Stop", controller.stop, 1),
            ("Turn Right", lambda: controller.turn_right(), 2),
            ("Stop", controller.stop, 1),
            ("Forward (fast)", lambda: controller.move_forward(70), 2),
            ("Emergency Stop", controller.emergency_stop, 1),
        ]
        
        for name, action, duration in movements:
            print(f"\n{name}...")
            action()
            time.sleep(duration)
        
        print("\n" + "="*60)
        print("Demo Complete!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Error during demo: {e}", exc_info=True)
    finally:
        print("\nCleaning up...")
        controller.cleanup()
        print("Cleanup complete.")


if __name__ == "__main__":
    run_demo()
