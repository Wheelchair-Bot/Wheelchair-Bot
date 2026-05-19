#!/usr/bin/env python3
"""Main entry point for wheelchair controller application.

Phase-0 cleanup (audit gap G-09): the hardware drive is now constructed
through the canonical ``wheelchair.drives.hardware.l298n.L298NDrive``
ABC implementation. The legacy ``WheelchairController`` from
``wheelchair_controller`` is kept for back-compat — it consumes the
underlying ``MotorDriver`` instance that ``L298NDrive`` already manages
via its ``motor_driver`` property.

End-state (after Phase 0 deletions): main.py will be replaced by a
thin shim around ``wheelchair.cli`` and the legacy
``wheelchair_controller`` package will be deleted entirely.
"""

import argparse
import logging
import sys

from wheelchair.drives.hardware.l298n import L298NDrive
from wheelchair_controller import WheelchairController
from wheelchair_controller.keyboard_control import KeyboardControl


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Wheelchair Robot Controller for Raspberry Pi'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock GPIO (for testing without Raspberry Pi)',
    )
    parser.add_argument(
        '--max-speed',
        type=int,
        default=80,
        help='Maximum speed percentage (0-100, default: 80)',
    )
    parser.add_argument(
        '--turn-speed',
        type=int,
        default=60,
        help='Turn speed percentage (0-100, default: 60)',
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging',
    )

    args = parser.parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    controller = None
    try:
        logger.info("Starting Wheelchair Controller")

        # Canonical drive (Phase 0 / G-09): WheelchairDrive ABC wrapping
        # the legacy MotorDriver. We hand the wrapped MotorDriver to
        # WheelchairController for back-compat with the keyboard loop.
        drive = L298NDrive(use_mock=args.mock)

        controller = WheelchairController(
            motor_driver=drive.motor_driver,
            max_speed=args.max_speed,
            turn_speed=args.turn_speed,
        )

        keyboard_control = KeyboardControl(controller)
        keyboard_control.run()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    finally:
        logger.info("Shutting down...")
        if controller is not None:
            controller.cleanup()

    logger.info("Shutdown complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
