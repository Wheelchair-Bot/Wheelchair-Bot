"""Enhanced realistic wheelchair drive system."""

import math
import random
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from wheelchair.interfaces import WheelchairDrive, WheelchairState
from wheelchair.config import WheelchairConfig


@dataclass
class TerrainProperties:
    """Properties of terrain affecting wheelchair movement."""
    
    friction_coefficient: float = 0.8  # Surface friction (0.0 = ice, 1.0 = ideal)
    rolling_resistance: float = 0.02   # Rolling resistance coefficient
    slope_angle: float = 0.0          # Terrain slope in radians
    surface_roughness: float = 0.0    # Surface roughness (0.0 = smooth, 1.0 = very rough)
    wetness: float = 0.0              # Surface wetness (0.0 = dry, 1.0 = wet)


@dataclass
class MotorState:
    """State of an individual motor."""
    
    temperature: float = 20.0         # Motor temperature in Celsius
    efficiency: float = 0.85          # Current efficiency
    wear_factor: float = 1.0          # Wear factor (1.0 = new, 0.0 = completely worn)
    torque: float = 0.0              # Current torque output
    rpm: float = 0.0                 # Current RPM
    power_draw: float = 0.0          # Current power draw in watts
    total_runtime: float = 0.0       # Total runtime in hours
    

@dataclass
class EnvironmentalConditions:
    """Environmental conditions affecting wheelchair operation."""
    
    temperature: float = 20.0         # Ambient temperature in Celsius
    humidity: float = 0.5            # Relative humidity (0.0 - 1.0)
    wind_speed: float = 0.0          # Wind speed in m/s
    wind_direction: float = 0.0      # Wind direction in radians
    precipitation: float = 0.0       # Precipitation intensity (0.0 - 1.0)


class RealisticEmulatedDrive(WheelchairDrive):
    """
    Enhanced emulated wheelchair drive system with realistic physics.
    
    Features:
    - Motor heating and efficiency curves
    - Terrain-dependent friction and resistance
    - Battery voltage effects on motor performance
    - Component wear simulation
    - Environmental effects (temperature, humidity, wind)
    - Wheel slip simulation
    - Mechanical backlash and play
    """

    def __init__(self, config: WheelchairConfig, state: WheelchairState):
        """Initialize realistic emulated drive."""
        self.config = config
        self.state = state
        
        # Motor control
        self._target_left_speed = 0.0
        self._target_right_speed = 0.0
        self._current_left_speed = 0.0
        self._current_right_speed = 0.0
        
        # Motor states
        self.left_motor = MotorState()
        self.right_motor = MotorState()
        
        # Environmental conditions
        self.terrain = TerrainProperties()
        self.environment = EnvironmentalConditions()
        
        # Physics state
        self._velocity_history = []  # For acceleration calculation
        self._last_velocity = 0.0
        self._wheel_slip_left = 0.0
        self._wheel_slip_right = 0.0
        
        # Motor characteristics (realistic curves)
        self.motor_max_torque = 50.0  # Nm
        self.motor_max_rpm = 3000.0   # RPM
        self.gear_ratio = 20.0        # Gearbox ratio
        self.motor_resistance = 0.5   # Ohms
        self.motor_kv = 100.0         # RPM/V constant
        
        # Mechanical properties
        self.backlash_angle = 0.02    # Mechanical backlash in radians
        self._backlash_state_left = 0.0
        self._backlash_state_right = 0.0

    def set_motor_speeds(self, left: float, right: float) -> None:
        """Set target motor speeds with realistic constraints."""
        # Apply input filtering (real motors don't respond instantly)
        filter_factor = 0.9
        self._target_left_speed = (filter_factor * self._target_left_speed + 
                                  (1 - filter_factor) * max(-1.0, min(1.0, left)))
        self._target_right_speed = (filter_factor * self._target_right_speed + 
                                   (1 - filter_factor) * max(-1.0, min(1.0, right)))

    def get_motor_speeds(self) -> Tuple[float, float]:
        """Get current motor speeds."""
        return (self._current_left_speed, self._current_right_speed)

    def emergency_stop(self) -> None:
        """Realistic emergency stop with motor dynamics."""
        # Motors don't stop instantly - apply maximum braking
        self._target_left_speed = 0.0
        self._target_right_speed = 0.0
        
        # Simulate regenerative braking heating
        braking_energy_left = abs(self._current_left_speed) * 0.5
        braking_energy_right = abs(self._current_right_speed) * 0.5
        
        self.left_motor.temperature += braking_energy_left * 10.0
        self.right_motor.temperature += braking_energy_right * 10.0
        
        self.state.emergency_stop = True

    def update(self, dt: float) -> None:
        """Update drive system with enhanced physics simulation."""
        # Update environmental effects
        self._update_environmental_effects(dt)
        
        # Update motor temperatures and wear
        self._update_motor_thermal_dynamics(dt)
        self._update_motor_wear(dt)
        
        # Calculate motor performance based on current conditions
        left_performance = self._calculate_motor_performance(self.left_motor)
        right_performance = self._calculate_motor_performance(self.right_motor)
        
        # Apply motor dynamics with performance factors
        self._update_motor_speeds(dt, left_performance, right_performance)
        
        # Calculate forces and motion
        self._simulate_vehicle_dynamics(dt)
        
        # Update position with slip and environmental effects
        self._update_position(dt)
        
        # Update motor states based on actual loads
        self._update_motor_states(dt)

    def _update_environmental_effects(self, dt: float) -> None:
        """Update environmental conditions affecting performance."""
        # Temperature effects on motor efficiency
        temp_factor = 1.0 - abs(self.environment.temperature - 25.0) * 0.01
        
        # Humidity effects on electrical systems
        humidity_factor = 1.0 - self.environment.humidity * 0.05
        
        # Apply environmental effects to motor efficiency
        base_efficiency = 0.85
        self.left_motor.efficiency = base_efficiency * temp_factor * humidity_factor
        self.right_motor.efficiency = base_efficiency * temp_factor * humidity_factor

    def _update_motor_thermal_dynamics(self, dt: float) -> None:
        """Simulate motor heating and cooling."""
        # Heat generation from motor load
        left_heat_gen = self.left_motor.power_draw * (1.0 - self.left_motor.efficiency) * 0.1
        right_heat_gen = self.right_motor.power_draw * (1.0 - self.right_motor.efficiency) * 0.1
        
        # Heat dissipation (Newton's cooling law)
        cooling_factor = 0.1  # Heat transfer coefficient
        left_cooling = cooling_factor * (self.left_motor.temperature - self.environment.temperature)
        right_cooling = cooling_factor * (self.right_motor.temperature - self.environment.temperature)
        
        # Update temperatures
        thermal_mass = 5.0  # Motor thermal mass
        self.left_motor.temperature += (left_heat_gen - left_cooling) * dt / thermal_mass
        self.right_motor.temperature += (right_heat_gen - right_cooling) * dt / thermal_mass
        
        # Prevent unrealistic temperatures
        self.left_motor.temperature = max(self.environment.temperature, 
                                        min(120.0, self.left_motor.temperature))
        self.right_motor.temperature = max(self.environment.temperature, 
                                         min(120.0, self.right_motor.temperature))

    def _update_motor_wear(self, dt: float) -> None:
        """Simulate component wear over time."""
        # Wear based on load, temperature, and runtime
        hours_per_second = dt / 3600.0
        
        for motor in [self.left_motor, self.right_motor]:
            motor.total_runtime += hours_per_second
            
            # Calculate wear rate based on conditions
            load_factor = abs(motor.torque) / self.motor_max_torque
            temp_factor = max(0.0, (motor.temperature - 40.0) / 80.0)  # Wear increases with heat
            
            wear_rate = (0.00001 + load_factor * 0.00005 + temp_factor * 0.00002) * hours_per_second
            motor.wear_factor = max(0.1, motor.wear_factor - wear_rate)  # Minimum 10% performance

    def _calculate_motor_performance(self, motor: MotorState) -> float:
        """Calculate motor performance factor based on current conditions."""
        # Performance degrades with temperature and wear
        temp_derating = max(0.3, 1.0 - (motor.temperature - 60.0) / 60.0)
        wear_factor = motor.wear_factor
        efficiency_factor = motor.efficiency
        
        return temp_derating * wear_factor * efficiency_factor

    def _update_motor_speeds(self, dt: float, left_perf: float, right_perf: float) -> None:
        """Update motor speeds with realistic dynamics and performance factors."""
        # Calculate maximum acceleration based on motor performance
        base_accel_limit = self.config.max_acceleration * dt / self.config.max_velocity
        
        left_accel_limit = base_accel_limit * left_perf
        right_accel_limit = base_accel_limit * right_perf
        
        # Apply backlash (mechanical play in gearbox)
        left_target_with_backlash = self._apply_backlash(
            self._target_left_speed, self._backlash_state_left, self.backlash_angle
        )
        right_target_with_backlash = self._apply_backlash(
            self._target_right_speed, self._backlash_state_right, self.backlash_angle
        )
        
        # Update motor speeds with acceleration limits
        self._current_left_speed = self._apply_acceleration_limit(
            self._current_left_speed, left_target_with_backlash, left_accel_limit
        )
        self._current_right_speed = self._apply_acceleration_limit(
            self._current_right_speed, right_target_with_backlash, right_accel_limit
        )

    def _apply_backlash(self, target: float, backlash_state: float, backlash: float) -> float:
        """Simulate mechanical backlash in gearbox."""
        direction_change = (target > 0) != (backlash_state > 0) and abs(target) > 0.1
        
        if direction_change:
            # Add backlash delay when changing direction
            return backlash_state + (target - backlash_state) * 0.3
        else:
            return target

    def _simulate_vehicle_dynamics(self, dt: float) -> None:
        """Simulate realistic vehicle dynamics including friction and slip."""
        # Convert motor speeds to wheel velocities
        left_wheel_velocity = self._current_left_speed * self.config.max_velocity
        right_wheel_velocity = self._current_right_speed * self.config.max_velocity
        
        # Calculate wheel slip based on terrain and load
        self._calculate_wheel_slip(left_wheel_velocity, right_wheel_velocity)
        
        # Apply slip to actual velocities
        actual_left_velocity = left_wheel_velocity * (1.0 - self._wheel_slip_left)
        actual_right_velocity = right_wheel_velocity * (1.0 - self._wheel_slip_right)
        
        # Differential drive kinematics with slip
        self.state.linear_velocity = (actual_left_velocity + actual_right_velocity) / 2.0
        self.state.angular_velocity = (actual_right_velocity - actual_left_velocity) / self.config.wheelbase
        
        # Apply terrain effects
        self._apply_terrain_effects()
        
        # Apply environmental forces (wind resistance, etc.)
        self._apply_environmental_forces()

    def _calculate_wheel_slip(self, left_vel: float, right_vel: float) -> None:
        """Calculate wheel slip based on terrain and motor torque."""
        # Slip increases with:
        # - Lower friction coefficient
        # - Higher motor torque
        # - Surface wetness
        # - Surface roughness
        
        base_slip = (1.0 - self.terrain.friction_coefficient) * 0.2
        wetness_slip = self.terrain.wetness * 0.15
        roughness_slip = self.terrain.surface_roughness * 0.1
        
        # Torque-dependent slip
        left_torque_factor = abs(left_vel) / self.config.max_velocity
        right_torque_factor = abs(right_vel) / self.config.max_velocity
        
        self._wheel_slip_left = min(0.8, base_slip + wetness_slip + roughness_slip + 
                                  left_torque_factor * 0.1)
        self._wheel_slip_right = min(0.8, base_slip + wetness_slip + roughness_slip + 
                                   right_torque_factor * 0.1)

    def _apply_terrain_effects(self) -> None:
        """Apply terrain effects to vehicle motion."""
        # Slope effects
        gravity_component = 9.81 * math.sin(self.terrain.slope_angle)
        slope_resistance = gravity_component * self.config.mass / 1000.0  # Convert to velocity effect
        
        # Rolling resistance
        rolling_resistance = self.terrain.rolling_resistance * abs(self.state.linear_velocity) * 0.1
        
        # Apply resistance to linear velocity
        total_resistance = slope_resistance + rolling_resistance
        self.state.linear_velocity *= max(0.0, 1.0 - total_resistance)

    def _apply_environmental_forces(self) -> None:
        """Apply environmental forces like wind resistance."""
        # Wind resistance (simplified)
        wind_effect = (self.environment.wind_speed * 
                      math.cos(self.environment.wind_direction - self.state.theta)) * 0.01
        
        self.state.linear_velocity -= wind_effect

    def _update_position(self, dt: float) -> None:
        """Update position with enhanced integration and noise."""
        # Add small random noise to simulate sensor/encoder noise
        position_noise = random.gauss(0.0, 0.001)  # 1mm standard deviation
        
        # Enhanced integration (Runge-Kutta 2nd order)
        v1 = self.state.linear_velocity
        w1 = self.state.angular_velocity
        
        x1 = self.state.x + v1 * math.cos(self.state.theta) * dt/2
        y1 = self.state.y + v1 * math.sin(self.state.theta) * dt/2
        theta1 = self.state.theta + w1 * dt/2
        
        # Second step
        self.state.x = x1 + v1 * math.cos(theta1) * dt/2 + position_noise
        self.state.y = y1 + v1 * math.sin(theta1) * dt/2 + position_noise
        self.state.theta = theta1 + w1 * dt/2
        
        # Normalize theta
        self.state.theta = math.atan2(math.sin(self.state.theta), math.cos(self.state.theta))

    def _update_motor_states(self, dt: float) -> None:
        """Update motor states based on actual performance."""
        # Calculate motor RPM and torque
        self.left_motor.rpm = abs(self._current_left_speed) * self.motor_max_rpm
        self.right_motor.rpm = abs(self._current_right_speed) * self.motor_max_rpm
        
        # Calculate required torque (simplified)
        self.left_motor.torque = abs(self._current_left_speed) * self.motor_max_torque * 0.5
        self.right_motor.torque = abs(self._current_right_speed) * self.motor_max_torque * 0.5
        
        # Calculate power draw based on torque and efficiency
        self.left_motor.power_draw = (self.left_motor.torque * self.left_motor.rpm * 
                                    2 * math.pi / 60) / self.left_motor.efficiency
        self.right_motor.power_draw = (self.right_motor.torque * self.right_motor.rpm * 
                                     2 * math.pi / 60) / self.right_motor.efficiency
        
        # Update state for monitoring
        self.state.left_motor_speed = self._current_left_speed
        self.state.right_motor_speed = self._current_right_speed

    def _apply_acceleration_limit(self, current: float, target: float, max_change: float) -> float:
        """Apply acceleration limit with enhanced dynamics."""
        delta = target - current
        if abs(delta) <= max_change:
            return target
        else:
            return current + (max_change if delta > 0 else -max_change)

    def get_power_draw(self) -> float:
        """Calculate total power draw including all inefficiencies."""
        return self.left_motor.power_draw + self.right_motor.power_draw + 5.0  # Base power

    # Additional methods for enhanced realism
    def set_terrain(self, terrain: TerrainProperties) -> None:
        """Set terrain properties for simulation."""
        self.terrain = terrain

    def set_environment(self, environment: EnvironmentalConditions) -> None:
        """Set environmental conditions."""
        self.environment = environment

    def get_motor_diagnostics(self) -> Dict:
        """Get detailed motor diagnostics."""
        return {
            "left_motor": {
                "temperature": self.left_motor.temperature,
                "efficiency": self.left_motor.efficiency,
                "wear_factor": self.left_motor.wear_factor,
                "torque": self.left_motor.torque,
                "rpm": self.left_motor.rpm,
                "power_draw": self.left_motor.power_draw,
                "runtime_hours": self.left_motor.total_runtime,
            },
            "right_motor": {
                "temperature": self.right_motor.temperature,
                "efficiency": self.right_motor.efficiency,
                "wear_factor": self.right_motor.wear_factor,
                "torque": self.right_motor.torque,
                "rpm": self.right_motor.rpm,
                "power_draw": self.right_motor.power_draw,
                "runtime_hours": self.right_motor.total_runtime,
            },
            "wheel_slip": {
                "left": self._wheel_slip_left,
                "right": self._wheel_slip_right,
            },
            "terrain": {
                "friction": self.terrain.friction_coefficient,
                "slope": math.degrees(self.terrain.slope_angle),
                "roughness": self.terrain.surface_roughness,
                "wetness": self.terrain.wetness,
            },
        }