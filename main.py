#!/usr/bin/env python3
"""Main entry point for wheelchair controller application."""

import argparse
import logging
import sys
from wheelchair_controller import WheelchairController, MotorDriver
from wheelchair_controller.keyboard_control import KeyboardControl


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Wheelchair Robot Controller for Raspberry Pi'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock GPIO (for testing without Raspberry Pi)'
    )
    parser.add_argument(
        '--max-speed',
        type=int,
        default=80,
        help='Maximum speed percentage (0-100, default: 80)'
    )
    parser.add_argument(
        '--turn-speed',
        type=int,
        default=60,
        help='Turn speed percentage (0-100, default: 60)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Wheelchair Controller")
        
        # Initialize motor driver
        motor_driver = MotorDriver(use_mock=args.mock)
        
        # Initialize controller
        controller = WheelchairController(
            motor_driver=motor_driver,
            max_speed=args.max_speed,
            turn_speed=args.turn_speed
        )
        
        # Initialize keyboard control
        keyboard_control = KeyboardControl(controller)
        
        # Run control loop
        keyboard_control.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    finally:
        logger.info("Shutting down...")
        if 'controller' in locals():
            controller.cleanup()
    
    logger.info("Shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
