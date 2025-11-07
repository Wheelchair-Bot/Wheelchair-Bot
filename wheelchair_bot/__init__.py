"""
Wheelchair Bot - Interface for controlling electric wheelchairs
"""

__version__ = "0.1.0"

from wheelchair_bot.wheelchairs.base import Wheelchair
from wheelchair_bot.controllers.base import Controller
from wheelchair_bot.motors.base import MotorController

__all__ = ["Wheelchair", "Controller", "MotorController"]
