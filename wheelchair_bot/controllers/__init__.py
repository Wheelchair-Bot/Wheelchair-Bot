"""
Controller input handlers
"""

from wheelchair_bot.controllers.base import Controller, CONTROLLER_FAMILY_SUPPORT
from wheelchair_bot.controllers.gamepad import GamepadController
from wheelchair_bot.controllers.joystick import JoystickController

# Export controller family support if available
if CONTROLLER_FAMILY_SUPPORT:
    from wheelchair.controller_families import ControllerFamily
    __all__ = ["Controller", "GamepadController", "JoystickController", "ControllerFamily", "CONTROLLER_FAMILY_SUPPORT"]
else:
    __all__ = ["Controller", "GamepadController", "JoystickController", "CONTROLLER_FAMILY_SUPPORT"]
