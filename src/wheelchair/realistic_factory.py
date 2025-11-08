"""Enhanced factory for creating realistic wheelchair emulator instances."""

import random
from typing import Optional, Dict, Any
from wheelchair.interfaces import WheelchairState
from wheelchair.config import EmulatorConfig
from wheelchair.emulator.loop import SimulationLoop
from wheelchair.emulator.controller import EmulatedController
from wheelchair.emulator.safety import EmulatedSafetyMonitor

# Import realistic components
from wheelchair.emulator.realistic_drive import (
    RealisticEmulatedDrive, 
    TerrainProperties, 
    EnvironmentalConditions
)
from wheelchair.emulator.realistic_sensors import RealisticSensorSuite
from wheelchair.emulator.realistic_power import RealisticPowerSystem


def create_realistic_emulator(config: EmulatorConfig = None, 
                            scenario: str = "default") -> SimulationLoop:
    """
    Factory function to create a realistic emulator system with enhanced physics.

    Args:
        config: Emulator configuration (uses defaults if None)
        scenario: Predefined scenario to set up ("default", "urban", "outdoor", "testing")

    Returns:
        Configured SimulationLoop with realistic components
    """
    if config is None:
        config = EmulatorConfig()

    # Create shared state
    state = WheelchairState()

    # Create realistic subsystems
    drive = RealisticEmulatedDrive(config.wheelchair, state)
    controller = EmulatedController()
    sensors = RealisticSensorSuite(config.sensors, state, config.simulation.seed)
    power = RealisticPowerSystem(config.power, state)
    safety = EmulatedSafetyMonitor(config.safety)

    # Apply scenario-specific settings
    apply_scenario(drive, sensors, power, scenario)

    # Create simulation loop
    loop = SimulationLoop(config, drive, controller, sensors, power, safety, state)

    return loop


def apply_scenario(drive: RealisticEmulatedDrive, 
                  sensors: RealisticSensorSuite, 
                  power: RealisticPowerSystem,
                  scenario: str) -> None:
    """
    Apply scenario-specific settings to the emulator components.
    
    Args:
        drive: Drive system to configure
        sensors: Sensor suite to configure  
        power: Power system to configure
        scenario: Scenario name
    """
    
    if scenario == "urban":
        # Urban environment - smooth surfaces, many obstacles
        terrain = TerrainProperties(
            friction_coefficient=0.9,
            rolling_resistance=0.015,
            slope_angle=0.0,
            surface_roughness=0.1,
            wetness=0.0
        )
        
        environment = EnvironmentalConditions(
            temperature=25.0,
            humidity=0.6,
            wind_speed=1.0,
            wind_direction=0.0,
            precipitation=0.0
        )
        
        drive.set_terrain(terrain)
        drive.set_environment(environment)
        
        # Urban has more obstacles and electromagnetic interference
        sensors.set_visibility(0.8)  # Reduced visibility due to buildings/smog
        
    elif scenario == "outdoor":
        # Outdoor environment - varied terrain, weather effects
        terrain = TerrainProperties(
            friction_coefficient=0.7,  # Grass/dirt
            rolling_resistance=0.03,   # Higher resistance on natural surfaces
            slope_angle=0.05,          # Slight hill
            surface_roughness=0.3,     # Bumpy natural terrain
            wetness=0.2               # Slightly damp
        )
        
        environment = EnvironmentalConditions(
            temperature=15.0,          # Cooler outdoor temperature
            humidity=0.8,
            wind_speed=3.0,            # More wind outdoors
            wind_direction=1.57,       # 90 degrees
            precipitation=0.1          # Light rain
        )
        
        drive.set_terrain(terrain)
        drive.set_environment(environment)
        
        # Outdoor conditions affect sensors
        sensors.set_visibility(0.9)
        power.set_ambient_temperature(15.0)
        
    elif scenario == "testing":
        # Testing scenario - controlled conditions with known challenges
        terrain = TerrainProperties(
            friction_coefficient=0.8,
            rolling_resistance=0.02,
            slope_angle=0.0,
            surface_roughness=0.05,
            wetness=0.0
        )
        
        environment = EnvironmentalConditions(
            temperature=20.0,
            humidity=0.5,
            wind_speed=0.0,
            wind_direction=0.0,
            precipitation=0.0
        )
        
        drive.set_terrain(terrain)
        drive.set_environment(environment)
        
        # Add some controlled obstacles for testing
        sensors.inject_obstacle("front", 2.0)
        
        # Simulate some battery wear for testing
        power.set_consumer_state("cooling", False)  # Disable cooling to test thermal effects
        
    elif scenario == "extreme":
        # Extreme conditions - stress testing
        terrain = TerrainProperties(
            friction_coefficient=0.5,  # Slippery surface
            rolling_resistance=0.05,   # High resistance
            slope_angle=0.1,           # 10% grade
            surface_roughness=0.5,     # Very rough
            wetness=0.7               # Very wet
        )
        
        environment = EnvironmentalConditions(
            temperature=35.0,          # Hot temperature
            humidity=0.9,
            wind_speed=5.0,            # Strong wind
            wind_direction=3.14,       # Headwind
            precipitation=0.5          # Heavy rain
        )
        
        drive.set_terrain(terrain)
        drive.set_environment(environment)
        
        sensors.set_visibility(0.5)   # Poor visibility
        power.set_ambient_temperature(35.0)
        
        # Inject GPS errors for extreme conditions
        sensors.inject_gps_error("multipath", 5.0)
        
    else:  # "default" scenario
        # Standard indoor/controlled environment
        terrain = TerrainProperties()  # Use defaults
        environment = EnvironmentalConditions()  # Use defaults
        
        drive.set_terrain(terrain)
        drive.set_environment(environment)


def create_emulator_with_custom_config(wheelchair_config: Dict[str, Any],
                                     sensor_config: Dict[str, Any] = None,
                                     power_config: Dict[str, Any] = None) -> SimulationLoop:
    """
    Create emulator with custom component configurations.
    
    Args:
        wheelchair_config: Wheelchair physical parameters
        sensor_config: Sensor configuration parameters
        power_config: Power system configuration parameters
        
    Returns:
        Configured SimulationLoop
    """
    # Create config from dictionaries
    config = EmulatorConfig()
    
    # Update wheelchair config
    for key, value in wheelchair_config.items():
        if hasattr(config.wheelchair, key):
            setattr(config.wheelchair, key, value)
    
    # Update sensor config if provided
    if sensor_config:
        for key, value in sensor_config.items():
            if hasattr(config.sensors, key):
                setattr(config.sensors, key, value)
    
    # Update power config if provided
    if power_config:
        for key, value in power_config.items():
            if hasattr(config.power, key):
                setattr(config.power, key, value)
    
    return create_realistic_emulator(config)


def create_degraded_emulator(wear_factor: float = 0.8,
                           battery_health: float = 0.9) -> SimulationLoop:
    """
    Create emulator simulating an aged/worn wheelchair.
    
    Args:
        wear_factor: Motor wear factor (0.0 = completely worn, 1.0 = new)
        battery_health: Battery health factor (0.0 = dead, 1.0 = new)
        
    Returns:
        SimulationLoop with degraded components
    """
    config = EmulatorConfig()
    
    # Reduce performance to simulate wear
    config.wheelchair.max_velocity *= wear_factor
    config.wheelchair.max_acceleration *= wear_factor
    config.power.battery_capacity *= battery_health
    
    # Create emulator
    loop = create_realistic_emulator(config)
    
    # Apply additional wear effects to motors
    if hasattr(loop.drive, 'left_motor'):
        loop.drive.left_motor.wear_factor = wear_factor
        loop.drive.left_motor.efficiency *= 0.9  # Reduced efficiency
        
    if hasattr(loop.drive, 'right_motor'):
        loop.drive.right_motor.wear_factor = wear_factor
        loop.drive.right_motor.efficiency *= 0.9
    
    # Simulate battery cell degradation
    if hasattr(loop.power, 'cells'):
        for series_group in loop.power.cells:
            for cell in series_group:
                cell.health = battery_health
                cell.cycle_count = int(1000 * (1.0 - battery_health))  # Simulate usage history
    
    return loop


def create_fault_injection_emulator(faults: Dict[str, Any]) -> SimulationLoop:
    """
    Create emulator with injected faults for testing.
    
    Args:
        faults: Dictionary of faults to inject
                Example: {
                    "left_motor_fault": True,
                    "gps_error": 10.0,  # meters
                    "sensor_noise": 2.0,  # multiplier
                    "battery_cell_failure": 2  # number of failed cells
                }
    
    Returns:
        SimulationLoop with injected faults
    """
    loop = create_realistic_emulator()
    
    # Inject motor faults
    if faults.get("left_motor_fault", False):
        if hasattr(loop.drive, 'left_motor'):
            loop.drive.left_motor.efficiency = 0.3
            loop.drive.left_motor.wear_factor = 0.2
    
    if faults.get("right_motor_fault", False):
        if hasattr(loop.drive, 'right_motor'):
            loop.drive.right_motor.efficiency = 0.3
            loop.drive.right_motor.wear_factor = 0.2
    
    # Inject sensor faults
    if "gps_error" in faults:
        loop.sensors.inject_gps_error("multipath", faults["gps_error"])
    
    if "sensor_noise" in faults:
        noise_multiplier = faults["sensor_noise"]
        # Would need to modify sensor noise parameters
        # This is a simplified example
        pass
    
    # Inject battery faults
    if "battery_cell_failure" in faults and hasattr(loop.power, 'cells'):
        failed_cells = faults["battery_cell_failure"]
        cell_count = 0
        for series_group in loop.power.cells:
            for cell in series_group:
                if cell_count < failed_cells:
                    cell.health = 0.1  # Nearly dead cell
                    cell.internal_resistance *= 10.0  # High resistance
                cell_count += 1
                if cell_count >= failed_cells:
                    break
    
    return loop


# Predefined wheelchair models for testing
WHEELCHAIR_MODELS = {
    "standard": {
        "wheelbase": 0.6,
        "wheel_radius": 0.15,
        "max_velocity": 2.0,
        "max_acceleration": 1.0,
        "mass": 100.0
    },
    
    "heavy_duty": {
        "wheelbase": 0.65,
        "wheel_radius": 0.18,
        "max_velocity": 1.5,
        "max_acceleration": 0.8,
        "mass": 150.0
    },
    
    "lightweight": {
        "wheelbase": 0.55,
        "wheel_radius": 0.12,
        "max_velocity": 2.5,
        "max_acceleration": 1.5,
        "mass": 80.0
    },
    
    "racing": {  # For testing extreme performance
        "wheelbase": 0.7,
        "wheel_radius": 0.2,
        "max_velocity": 4.0,
        "max_acceleration": 2.0,
        "mass": 90.0
    }
}


def create_model_emulator(model: str) -> SimulationLoop:
    """
    Create emulator for a specific wheelchair model.
    
    Args:
        model: Model name from WHEELCHAIR_MODELS
        
    Returns:
        SimulationLoop configured for the specified model
    """
    if model not in WHEELCHAIR_MODELS:
        raise ValueError(f"Unknown model: {model}. Available models: {list(WHEELCHAIR_MODELS.keys())}")
    
    return create_emulator_with_custom_config(WHEELCHAIR_MODELS[model])


# Legacy compatibility
def create_emulator(config: EmulatorConfig = None) -> SimulationLoop:
    """Legacy function for backward compatibility."""
    return create_realistic_emulator(config)