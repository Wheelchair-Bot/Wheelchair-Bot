#!/usr/bin/env python3
"""
Enhanced Wheelchair Emulator Demo - Realistic Physics and Sensors

This script demonstrates the enhanced wheelchair emulator with realistic
physics simulation, comprehensive sensor modeling, and environmental effects.
"""

import time
import math
import json
from typing import Dict, Any
import argparse

from wheelchair.config import EmulatorConfig
from wheelchair.realistic_factory import (
    create_realistic_emulator,
    create_degraded_emulator, 
    create_fault_injection_emulator,
    create_model_emulator,
    WHEELCHAIR_MODELS
)
from wheelchair.interfaces import ControllerInput


class EmulatorDemo:
    """Enhanced emulator demonstration class."""
    
    def __init__(self, scenario: str = "default", model: str = "standard"):
        """Initialize the demo."""
        print(f"\n🦽 Enhanced Wheelchair Emulator Demo")
        print(f"{'='*50}")
        print(f"Scenario: {scenario}")
        print(f"Model: {model}")
        print()
        
        # Create emulator based on model
        if model in WHEELCHAIR_MODELS:
            self.loop = create_model_emulator(model)
        else:
            config = EmulatorConfig()
            self.loop = create_realistic_emulator(config, scenario)
        
        self.running = False
        self.demo_phase = 0
        
    def run_comprehensive_demo(self, duration: float = 60.0):
        """Run a comprehensive demonstration of all features."""
        print("🚀 Starting Comprehensive Demo...")
        print(f"Duration: {duration} seconds")
        print()
        
        # Demo phases
        phases = [
            ("Initialization & Diagnostics", self._demo_diagnostics, 5.0),
            ("Basic Movement", self._demo_basic_movement, 10.0),
            ("Terrain Effects", self._demo_terrain_effects, 15.0),
            ("Sensor Simulation", self._demo_sensors, 10.0),
            ("Power Management", self._demo_power_management, 10.0),
            ("Environmental Effects", self._demo_environmental, 10.0),
        ]
        
        start_time = time.time()
        
        for phase_name, phase_func, phase_duration in phases:
            if time.time() - start_time > duration:
                break
                
            print(f"\n📋 Phase: {phase_name}")
            print(f"   Duration: {phase_duration}s")
            
            phase_start = time.time()
            
            # Add callback for this phase
            self.loop.add_callback(lambda state, dt: phase_func(state, dt, time.time() - phase_start))
            
            # Run phase
            self.loop.run(duration=phase_duration)
            
            # Display phase results
            self._display_phase_results()
            
            time.sleep(1)  # Brief pause between phases
    
    def _demo_diagnostics(self, state, dt, phase_time):
        """Demonstrate system diagnostics."""
        if phase_time < 1.0:  # Only run diagnostics once
            print("\n🔧 System Diagnostics:")
            
            # Motor diagnostics
            if hasattr(self.loop.drive, 'get_motor_diagnostics'):
                motor_diag = self.loop.drive.get_motor_diagnostics()
                print(f"  Left Motor:  Temp: {motor_diag['left_motor']['temperature']:.1f}°C, "
                      f"Efficiency: {motor_diag['left_motor']['efficiency']:.2f}")
                print(f"  Right Motor: Temp: {motor_diag['right_motor']['temperature']:.1f}°C, "
                      f"Efficiency: {motor_diag['right_motor']['efficiency']:.2f}")
                print(f"  Wheel Slip:  Left: {motor_diag['wheel_slip']['left']:.3f}, "
                      f"Right: {motor_diag['wheel_slip']['right']:.3f}")
            
            # Power diagnostics
            if hasattr(self.loop.power, 'get_power_diagnostics'):
                power_diag = self.loop.power.get_power_diagnostics()
                print(f"  Battery:     {power_diag['battery']['charge_level']:.1%} charge, "
                      f"{power_diag['battery']['pack_voltage']:.1f}V")
                print(f"  Power Draw:  {power_diag['battery']['pack_current']:.1f}A")
            
            # Sensor diagnostics
            if hasattr(self.loop.sensors, 'get_sensor_diagnostics'):
                sensor_diag = self.loop.sensors.get_sensor_diagnostics()
                print(f"  GPS:         {sensor_diag['gps']['satellites']} satellites, "
                      f"accuracy ±{sensor_diag['gps']['accuracy']:.1f}m")
                print(f"  IMU Bias:    X:{sensor_diag['imu']['bias_x']:.4f} "
                      f"Y:{sensor_diag['imu']['bias_y']:.4f} "
                      f"Z:{sensor_diag['imu']['bias_z']:.4f}")
    
    def _demo_basic_movement(self, state, dt, phase_time):
        """Demonstrate basic movement patterns."""
        # Create movement pattern
        cycle_time = 8.0  # 8 second cycle
        t = phase_time % cycle_time
        
        if t < 2.0:
            # Forward movement
            self.loop.controller.set_input(linear=0.5, deadman_pressed=True)
            if t < 0.1:
                print("  ⬆️  Moving Forward")
        elif t < 4.0:
            # Turn right
            self.loop.controller.set_input(linear=0.3, angular=0.5, deadman_pressed=True)
            if t < 2.1:
                print("  ↗️  Turning Right")
        elif t < 6.0:
            # Backward movement
            self.loop.controller.set_input(linear=-0.3, deadman_pressed=True)
            if t < 4.1:
                print("  ⬇️  Moving Backward")
        else:
            # Turn left
            self.loop.controller.set_input(linear=0.3, angular=-0.5, deadman_pressed=True)
            if t < 6.1:
                print("  ↖️  Turning Left")
    
    def _demo_terrain_effects(self, state, dt, phase_time):
        """Demonstrate terrain effects on movement."""
        if not hasattr(self.loop.drive, 'set_terrain'):
            return
        
        cycle_time = 12.0
        t = phase_time % cycle_time
        
        from wheelchair.emulator.realistic_drive import TerrainProperties
        
        if t < 3.0:
            # Smooth surface
            terrain = TerrainProperties(friction_coefficient=0.9, surface_roughness=0.0)
            self.loop.drive.set_terrain(terrain)
            if t < 0.1:
                print("  🛣️  Smooth Surface (high friction)")
        elif t < 6.0:
            # Slippery surface
            terrain = TerrainProperties(friction_coefficient=0.5, surface_roughness=0.1, wetness=0.7)
            self.loop.drive.set_terrain(terrain)
            if t < 3.1:
                print("  🧊  Slippery Surface (wet, low friction)")
        elif t < 9.0:
            # Rough terrain
            terrain = TerrainProperties(friction_coefficient=0.7, surface_roughness=0.4, rolling_resistance=0.04)
            self.loop.drive.set_terrain(terrain)
            if t < 6.1:
                print("  🪨  Rough Terrain (high resistance)")
        else:
            # Uphill slope
            terrain = TerrainProperties(friction_coefficient=0.8, slope_angle=0.1)  # 5.7 degree slope
            self.loop.drive.set_terrain(terrain)
            if t < 9.1:
                print("  ⛰️  Uphill Slope (10% grade)")
        
        # Maintain movement during terrain changes
        self.loop.controller.set_input(linear=0.4, deadman_pressed=True)
    
    def _demo_sensors(self, state, dt, phase_time):
        """Demonstrate sensor simulation capabilities."""
        # Move in a pattern to generate sensor data
        t = phase_time % 8.0
        
        if t < 2.0:
            self.loop.controller.set_input(linear=0.6, deadman_pressed=True)
        elif t < 4.0:
            self.loop.controller.set_input(angular=0.8, deadman_pressed=True)  # Spin to test gyro
        elif t < 6.0:
            self.loop.controller.set_input(linear=-0.4, deadman_pressed=True)
        else:
            self.loop.controller.set_input(linear=0.0, angular=0.0, deadman_pressed=True)
        
        # Display sensor readings periodically
        if phase_time % 2.0 < dt:  # Every 2 seconds
            sensor_data = self.loop.sensors.read_sensors()
            print(f"  📡 IMU: ax={sensor_data.accel_x:.2f} ay={sensor_data.accel_y:.2f} "
                  f"gz={sensor_data.gyro_z:.3f} rad/s")
            
            if hasattr(sensor_data, 'gps'):
                print(f"  🛰️  GPS: {sensor_data.gps.latitude:.6f}°, "
                      f"{sensor_data.gps.longitude:.6f}° (±{sensor_data.gps.accuracy:.1f}m)")
            
            # Show proximity sensors
            sensors = [sensor_data.proximity_front, sensor_data.proximity_rear, 
                      sensor_data.proximity_left, sensor_data.proximity_right]
            sensor_names = ["Front", "Rear", "Left", "Right"]
            
            obstacles = [f"{name}: {dist:.1f}m" for name, dist in zip(sensor_names, sensors) if dist is not None]
            if obstacles:
                print(f"  🚧 Obstacles: {', '.join(obstacles)}")
    
    def _demo_power_management(self, state, dt, phase_time):
        """Demonstrate power system simulation."""
        # Create varying power demands
        t = phase_time % 6.0
        
        if t < 2.0:
            # High power demand
            self.loop.controller.set_input(linear=0.8, deadman_pressed=True)
            if t < 0.1:
                print("  ⚡ High Power Demand")
        elif t < 4.0:
            # Medium power demand
            self.loop.controller.set_input(linear=0.4, deadman_pressed=True)
            if t < 2.1:
                print("  🔋 Medium Power Demand")
        else:
            # Low power (idle)
            self.loop.controller.set_input(linear=0.0, deadman_pressed=True)
            if t < 4.1:
                print("  💤 Idle (Low Power)")
        
        # Display power statistics
        if phase_time % 3.0 < dt:
            if hasattr(self.loop.power, 'get_power_diagnostics'):
                power_diag = self.loop.power.get_power_diagnostics()
                battery = power_diag['battery']
                
                print(f"  🔋 Battery: {battery['charge_level']:.1%} charge, "
                      f"{battery['pack_voltage']:.1f}V, {battery['pack_current']:.1f}A")
                
                if battery['remaining_time'] is not None:
                    print(f"  ⏱️  Estimated runtime: {battery['remaining_time']:.1f} hours")
                
                # Show individual cell voltages
                cells = power_diag['cells']
                print(f"  🔬 Cell voltage range: {cells['min_voltage']:.2f}V - {cells['max_voltage']:.2f}V "
                      f"(spread: {cells['voltage_spread']:.3f}V)")
    
    def _demo_environmental(self, state, dt, phase_time):
        """Demonstrate environmental effects."""
        if not hasattr(self.loop.drive, 'set_environment'):
            return
        
        from wheelchair.emulator.realistic_drive import EnvironmentalConditions
        
        cycle_time = 10.0
        t = phase_time % cycle_time
        
        if t < 2.5:
            # Normal conditions
            env = EnvironmentalConditions(temperature=20.0, wind_speed=0.0)
            self.loop.drive.set_environment(env)
            if t < 0.1:
                print("  🌤️  Normal Weather")
        elif t < 5.0:
            # Hot and windy
            env = EnvironmentalConditions(temperature=35.0, wind_speed=5.0, wind_direction=0.0)
            self.loop.drive.set_environment(env)
            if t < 2.6:
                print("  🌡️  Hot & Windy (35°C, 5m/s headwind)")
        elif t < 7.5:
            # Cold and humid
            env = EnvironmentalConditions(temperature=5.0, humidity=0.9)
            self.loop.drive.set_environment(env)
            if t < 5.1:
                print("  🥶  Cold & Humid (5°C, 90% humidity)")
        else:
            # Rainy
            env = EnvironmentalConditions(temperature=15.0, precipitation=0.5)
            self.loop.drive.set_environment(env)
            if t < 7.6:
                print("  🌧️  Rainy Weather")
        
        # Maintain movement
        self.loop.controller.set_input(linear=0.3, deadman_pressed=True)
    
    def _display_phase_results(self):
        """Display results after each phase."""
        state = self.loop.state
        print(f"\n📊 Phase Results:")
        print(f"  Position: ({state.x:.2f}, {state.y:.2f}) meters")
        print(f"  Heading:  {math.degrees(state.theta):.1f}°")
        print(f"  Velocity: {state.linear_velocity:.2f} m/s")
        
        # Additional diagnostics if available
        if hasattr(self.loop.power, 'get_power_diagnostics'):
            power_diag = self.loop.power.get_power_diagnostics()
            energy_consumed = power_diag['statistics']['total_energy_consumed']
            print(f"  Energy:   {energy_consumed:.1f} Wh consumed")
    
    def run_fault_injection_demo(self):
        """Demonstrate fault injection capabilities."""
        print("\n⚠️  Fault Injection Demo")
        print("="*30)
        
        # Create emulator with injected faults
        faults = {
            "left_motor_fault": True,
            "gps_error": 5.0,
            "battery_cell_failure": 2
        }
        
        print("Injecting faults:")
        for fault, value in faults.items():
            print(f"  - {fault}: {value}")
        
        fault_emulator = create_fault_injection_emulator(faults)
        
        # Run brief test
        fault_emulator.controller.set_input(linear=0.5, deadman_pressed=True)
        fault_emulator.run(duration=5.0)
        
        # Show degraded performance
        if hasattr(fault_emulator.drive, 'get_motor_diagnostics'):
            motor_diag = fault_emulator.drive.get_motor_diagnostics()
            print("\n🔧 Motor Status After Fault Injection:")
            print(f"  Left Motor Efficiency:  {motor_diag['left_motor']['efficiency']:.2f}")
            print(f"  Right Motor Efficiency: {motor_diag['right_motor']['efficiency']:.2f}")
        
        if hasattr(fault_emulator.sensors, 'read_sensors'):
            sensor_data = fault_emulator.sensors.read_sensors()
            if hasattr(sensor_data, 'gps'):
                print(f"  GPS Accuracy: ±{sensor_data.gps.accuracy:.1f}m (degraded)")
    
    def run_aging_demo(self):
        """Demonstrate component aging simulation."""
        print("\n👴 Component Aging Demo")
        print("="*25)
        
        # Create aged emulator
        aged_emulator = create_degraded_emulator(wear_factor=0.6, battery_health=0.7)
        
        print("Simulating aged wheelchair:")
        print("  - Motor wear: 40% degradation")
        print("  - Battery health: 70% of original capacity")
        
        # Compare performance
        aged_emulator.controller.set_input(linear=1.0, deadman_pressed=True)
        aged_emulator.run(duration=3.0)
        
        state = aged_emulator.state
        print(f"\n📉 Aged Performance:")
        print(f"  Maximum achieved velocity: {state.linear_velocity:.2f} m/s")
        
        if hasattr(aged_emulator.power, 'get_power_diagnostics'):
            power_diag = aged_emulator.power.get_power_diagnostics()
            print(f"  Battery capacity: {power_diag['battery']['charge_level']:.1%} of degraded capacity")


def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(description="Enhanced Wheelchair Emulator Demo")
    parser.add_argument("--scenario", default="default", 
                       choices=["default", "urban", "outdoor", "testing", "extreme"],
                       help="Simulation scenario")
    parser.add_argument("--model", default="standard",
                       choices=list(WHEELCHAIR_MODELS.keys()),
                       help="Wheelchair model")
    parser.add_argument("--duration", type=float, default=60.0,
                       help="Demo duration in seconds")
    parser.add_argument("--demo-type", default="comprehensive",
                       choices=["comprehensive", "fault-injection", "aging", "all"],
                       help="Type of demonstration")
    
    args = parser.parse_args()
    
    try:
        demo = EmulatorDemo(args.scenario, args.model)
        
        if args.demo_type in ["comprehensive", "all"]:
            demo.run_comprehensive_demo(args.duration)
        
        if args.demo_type in ["fault-injection", "all"]:
            demo.run_fault_injection_demo()
        
        if args.demo_type in ["aging", "all"]:
            demo.run_aging_demo()
        
        print("\n✅ Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  🔬 Realistic physics simulation with friction, slip, and inertia")
        print("  🌡️ Environmental effects (temperature, humidity, wind, precipitation)")
        print("  🔋 Comprehensive battery modeling with cell-level simulation")
        print("  📡 Enhanced sensor suite (IMU, GPS, LiDAR, cameras, encoders)")
        print("  ⚙️ Motor thermal dynamics and efficiency modeling")
        print("  🔧 Component wear and aging simulation")
        print("  ⚠️ Fault injection for testing robustness")
        print("  📊 Comprehensive diagnostics and monitoring")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        raise


if __name__ == "__main__":
    main()