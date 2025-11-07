"""
Motor control interfaces
"""

from wheelchair_bot.motors.base import MotorController
from wheelchair_bot.motors.differential import DifferentialDriveController

__all__ = ["MotorController", "DifferentialDriveController"]
