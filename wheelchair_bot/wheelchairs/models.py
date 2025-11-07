"""
Popular wheelchair models with their specifications
"""

from wheelchair_bot.wheelchairs.base import Wheelchair
from typing import Dict


class PermobilM3Corpus(Wheelchair):
    """
    Permobil M3 Corpus - Mid-wheel drive power wheelchair.
    
    Popular high-end power wheelchair with excellent maneuverability.
    """
    
    def __init__(self):
        super().__init__(
            name="Permobil M3 Corpus",
            max_speed=2.2,  # m/s (about 5 mph)
            wheel_base=0.45,  # meters
            wheel_diameter=0.35,  # meters
        )
        
    def get_motor_config(self) -> Dict:
        return {
            "type": "mid_wheel_drive",
            "motor_count": 2,
            "motor_type": "brushless_dc",
            "max_voltage": 24,
            "max_current": 50,
        }


class QuantumQ6Edge(Wheelchair):
    """
    Quantum Q6 Edge - Mid-wheel drive power wheelchair.
    
    Popular mid-range power wheelchair with good outdoor performance.
    """
    
    def __init__(self):
        super().__init__(
            name="Quantum Q6 Edge",
            max_speed=2.68,  # m/s (about 6 mph)
            wheel_base=0.42,  # meters
            wheel_diameter=0.33,  # meters
        )
        
    def get_motor_config(self) -> Dict:
        return {
            "type": "mid_wheel_drive",
            "motor_count": 2,
            "motor_type": "brushed_dc",
            "max_voltage": 24,
            "max_current": 45,
        }


class InvacareTPG(Wheelchair):
    """
    Invacare TDX SP2 - Rear-wheel drive power wheelchair.
    
    Popular rear-wheel drive wheelchair with excellent stability.
    """
    
    def __init__(self):
        super().__init__(
            name="Invacare TDX SP2",
            max_speed=2.24,  # m/s (about 5 mph)
            wheel_base=0.50,  # meters
            wheel_diameter=0.36,  # meters
        )
        
    def get_motor_config(self) -> Dict:
        return {
            "type": "rear_wheel_drive",
            "motor_count": 2,
            "motor_type": "brushed_dc",
            "max_voltage": 24,
            "max_current": 40,
        }


class PrideJazzy(Wheelchair):
    """
    Pride Jazzy Elite HD - Front-wheel drive power wheelchair.
    
    Popular front-wheel drive wheelchair with good indoor maneuverability.
    """
    
    def __init__(self):
        super().__init__(
            name="Pride Jazzy Elite HD",
            max_speed=1.79,  # m/s (about 4 mph)
            wheel_base=0.48,  # meters
            wheel_diameter=0.30,  # meters
        )
        
    def get_motor_config(self) -> Dict:
        return {
            "type": "front_wheel_drive",
            "motor_count": 2,
            "motor_type": "brushed_dc",
            "max_voltage": 24,
            "max_current": 35,
        }
