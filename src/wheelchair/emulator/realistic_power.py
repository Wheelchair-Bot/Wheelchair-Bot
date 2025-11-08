"""Enhanced realistic power system with comprehensive battery modeling."""

import math
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from wheelchair.interfaces import PowerSystem, WheelchairState
from wheelchair.config import PowerConfig


@dataclass
class BatteryCell:
    """Individual battery cell model."""
    
    voltage: float = 4.0          # Cell voltage
    capacity: float = 3.0         # Capacity in Ah
    internal_resistance: float = 0.1  # Internal resistance in Ohms
    temperature: float = 25.0     # Cell temperature in Celsius
    cycle_count: int = 0          # Number of charge/discharge cycles
    health: float = 1.0          # Battery health (1.0 = new, 0.0 = dead)
    charge_level: float = 1.0     # State of charge (0.0 - 1.0)


@dataclass
class PowerConsumer:
    """Power consuming component."""
    
    name: str
    base_power: float             # Base power consumption in watts
    load_dependent: bool = False  # Whether power scales with load
    efficiency: float = 1.0       # Component efficiency
    enabled: bool = True          # Whether component is active


class RealisticPowerSystem(PowerSystem):
    """
    Enhanced power system with realistic battery modeling.
    
    Features:
    - Individual battery cell simulation
    - Temperature effects on capacity and performance
    - Battery aging and degradation
    - Realistic discharge curves
    - Power distribution to multiple consumers
    - Regenerative braking simulation
    - Battery management system (BMS) simulation
    - Thermal management
    """

    def __init__(self, config: PowerConfig, state: WheelchairState = None):
        """Initialize realistic power system."""
        self.config = config
        self.state = state
        
        # Battery pack configuration (6S2P = 6 series, 2 parallel)
        self.series_cells = 6
        self.parallel_cells = 2
        self.cells = []
        
        # Initialize battery cells
        for s in range(self.series_cells):
            series_group = []
            for p in range(self.parallel_cells):
                cell = BatteryCell()
                # Add some cell-to-cell variation
                cell.capacity *= (0.98 + 0.04 * (s * self.parallel_cells + p) / 
                                (self.series_cells * self.parallel_cells))
                cell.internal_resistance *= (0.9 + 0.2 * (s * self.parallel_cells + p) / 
                                           (self.series_cells * self.parallel_cells))
                series_group.append(cell)
            self.cells.append(series_group)
        
        # Power consumers
        self.consumers = {
            "motors": PowerConsumer("Motor Controllers", 0.0, True, 0.85),
            "computer": PowerConsumer("Main Computer", 15.0, False, 0.95),
            "sensors": PowerConsumer("Sensor Suite", 8.0, False, 0.9),
            "wireless": PowerConsumer("Wireless Systems", 3.0, False, 0.8),
            "lights": PowerConsumer("LED Lighting", 5.0, False, 0.9),
            "cooling": PowerConsumer("Cooling Fans", 2.0, True, 0.7),
            "bms": PowerConsumer("Battery Management", 1.0, False, 0.95),
        }
        
        # System state
        self._total_energy_consumed = 0.0  # Wh
        self._peak_power_draw = 0.0        # W
        self._regenerative_energy = 0.0    # Wh recovered
        self._charge_cycles = 0.0          # Fractional charge cycles
        self._last_charge_level = 1.0      # For cycle counting
        
        # Thermal state
        self._ambient_temperature = 25.0
        self._battery_temperature = 25.0
        self._thermal_mass = 5.0           # kg equivalent thermal mass
        
        # BMS parameters
        self._cell_balancing_active = False
        self._over_temperature_protection = False
        self._under_voltage_protection = False
        
        # Historical data for analysis
        self._voltage_history = []
        self._current_history = []
        self._temperature_history = []

    def get_voltage(self) -> float:
        """Get battery pack voltage."""
        total_voltage = 0.0
        
        for series_group in self.cells:
            # Parallel cells: average voltage (accounting for current sharing)
            group_voltage = sum(cell.voltage for cell in series_group) / len(series_group)
            total_voltage += group_voltage
        
        return total_voltage

    def get_current_draw(self) -> float:
        """Get total current draw from battery."""
        total_power = self.get_total_power_draw()
        voltage = self.get_voltage()
        
        if voltage > 0:
            return total_power / voltage
        return 0.0

    def get_charge_level(self) -> float:
        """Get state of charge (0.0 - 1.0)."""
        # Use the weakest cell to determine pack charge level
        min_charge = float('inf')
        
        for series_group in self.cells:
            for cell in series_group:
                min_charge = min(min_charge, cell.charge_level)
        
        return min_charge
    
    def get_percent(self) -> float:
        """Get battery percentage (0-100)."""
        return self.get_charge_level() * 100.0

    def get_remaining_time(self) -> Optional[float]:
        """Estimate remaining runtime in hours."""
        current_draw = self.get_current_draw()
        
        if current_draw <= 0:
            return None  # No discharge or charging
        
        # Calculate usable capacity (accounting for voltage cutoff)
        usable_capacity = self._calculate_usable_capacity()
        current_capacity = self.get_charge_level() * usable_capacity
        
        if current_capacity <= 0:
            return 0.0
        
        return current_capacity / current_draw

    def is_low_battery(self) -> bool:
        """Check if battery is low."""
        return self.get_charge_level() < 0.2 or self.get_voltage() < self.config.min_voltage

    def is_critical_battery(self) -> bool:
        """Check if battery is critically low."""
        return self.get_charge_level() < 0.05 or self.get_voltage() < (self.config.min_voltage * 0.95)

    def update(self, dt: float, motor_power: float = 0.0) -> None:
        """Update power system simulation."""
        # Update motor power consumption
        self.consumers["motors"].base_power = motor_power
        
        # Update cooling power based on motor load and temperature
        cooling_needed = max(0.0, (self._battery_temperature - 35.0) / 20.0)
        motor_load_factor = motor_power / 500.0  # Normalize to 500W max
        self.consumers["cooling"].base_power = 2.0 + cooling_needed * 8.0 + motor_load_factor * 3.0
        
        # Calculate total power draw
        total_power = self.get_total_power_draw()
        
        # Update battery cells
        self._update_battery_cells(dt, total_power)
        
        # Update thermal dynamics
        self._update_thermal_dynamics(dt, total_power)
        
        # Update BMS functions
        self._update_bms(dt)
        
        # Update statistics
        self._update_statistics(dt, total_power)
        
        # Update historical data
        self._update_history()

    def get_total_power_draw(self) -> float:
        """Calculate total power consumption from all consumers."""
        total_power = 0.0
        
        for consumer in self.consumers.values():
            if consumer.enabled:
                power = consumer.base_power
                
                # Add load-dependent power if applicable
                if consumer.load_dependent and self.state:
                    load_factor = abs(self.state.linear_velocity) / 2.0  # Normalize to 2 m/s max
                    power += power * load_factor
                
                # Apply efficiency
                total_power += power / consumer.efficiency
        
        return total_power

    def _update_battery_cells(self, dt: float, total_power: float) -> None:
        """Update individual battery cell states."""
        pack_current = self.get_current_draw()
        
        # Current per series string (parallel cells share current)
        series_current = pack_current / self.parallel_cells
        
        for series_idx, series_group in enumerate(self.cells):
            for parallel_idx, cell in enumerate(series_group):
                # Cell current (may vary slightly due to resistance differences)
                cell_current_factor = (cell.internal_resistance / 
                                     sum(c.internal_resistance for c in series_group))
                cell_current = series_current * cell_current_factor
                
                # Voltage drop due to internal resistance
                voltage_drop = cell_current * cell.internal_resistance
                
                # Update cell voltage (simplified model)
                # Real batteries have complex voltage curves
                base_voltage = self._calculate_cell_voltage(cell)
                cell.voltage = max(2.5, base_voltage - voltage_drop)  # Minimum 2.5V per cell
                
                # Update charge level
                capacity_ah = cell.capacity * cell.health
                if capacity_ah > 0:
                    charge_delta = -(cell_current * dt / 3600.0) / capacity_ah
                    cell.charge_level = max(0.0, min(1.0, cell.charge_level + charge_delta))
                
                # Update cell temperature (simplified)
                heat_generation = cell_current**2 * cell.internal_resistance  # I²R losses
                cell.temperature += heat_generation * dt * 0.1  # Thermal response
                
                # Cell aging
                self._update_cell_aging(cell, dt, cell_current)

    def _calculate_cell_voltage(self, cell: BatteryCell) -> float:
        """Calculate cell voltage based on state of charge and temperature."""
        # Simplified lithium-ion voltage curve
        soc = cell.charge_level
        
        # Base voltage curve (typical Li-ion)
        if soc > 0.9:
            voltage = 4.0 + (soc - 0.9) * 2.0  # Steep rise at top
        elif soc > 0.1:
            voltage = 3.3 + (soc - 0.1) * 0.875  # Linear middle section
        else:
            voltage = 3.0 + soc * 3.0  # Steep drop at bottom
        
        # Temperature effects
        temp_coeff = -0.003  # V/°C (typical for Li-ion)
        temp_effect = (cell.temperature - 25.0) * temp_coeff
        
        return voltage + temp_effect

    def _update_cell_aging(self, cell: BatteryCell, dt: float, current: float) -> None:
        """Update cell aging and degradation."""
        # Calendar aging (time-based degradation)
        calendar_aging_rate = 0.00001 / 3600.0  # Per second
        
        # Cycle aging (usage-based degradation)
        current_stress = abs(current) / cell.capacity  # C-rate
        temperature_stress = max(0.0, (cell.temperature - 25.0) / 50.0)
        depth_stress = abs(cell.charge_level - 0.5) * 2.0  # Stress increases away from 50% SOC
        
        cycle_aging_rate = (calendar_aging_rate * 
                          (1.0 + current_stress * 10.0) *
                          (1.0 + temperature_stress * 5.0) *
                          (1.0 + depth_stress * 2.0))
        
        # Apply aging
        aging_factor = cycle_aging_rate * dt
        cell.health = max(0.1, cell.health - aging_factor)  # Minimum 10% health
        
        # Update cycle count (simplified)
        if current > 0:  # Discharging
            cell.cycle_count += abs(current) * dt / (3600.0 * cell.capacity * 2.0)

    def _update_thermal_dynamics(self, dt: float, power: float) -> None:
        """Update battery thermal dynamics."""
        # Heat generation from power losses
        efficiency = 0.95  # Battery efficiency
        heat_generation = power * (1.0 - efficiency)
        
        # Heat dissipation to ambient
        heat_transfer_coeff = 10.0  # W/K
        heat_dissipation = heat_transfer_coeff * (self._battery_temperature - self._ambient_temperature)
        
        # Update temperature
        net_heat = heat_generation - heat_dissipation
        temp_rise = net_heat * dt / (self._thermal_mass * 1000.0)  # Specific heat ~1000 J/kg/K
        self._battery_temperature += temp_rise
        
        # Limit temperature range
        self._battery_temperature = max(self._ambient_temperature, 
                                      min(70.0, self._battery_temperature))

    def _update_bms(self, dt: float) -> None:
        """Update Battery Management System functions."""
        # Check for over-temperature
        max_temp = max(max(cell.temperature for cell in series_group) 
                      for series_group in self.cells)
        self._over_temperature_protection = max_temp > 60.0
        
        # Check for under-voltage
        min_voltage = min(min(cell.voltage for cell in series_group) 
                         for series_group in self.cells)
        self._under_voltage_protection = min_voltage < 2.8
        
        # Cell balancing (simplified)
        max_soc = max(max(cell.charge_level for cell in series_group) 
                     for series_group in self.cells)
        min_soc = min(min(cell.charge_level for cell in series_group) 
                     for series_group in self.cells)
        
        self._cell_balancing_active = (max_soc - min_soc) > 0.05  # 5% imbalance threshold
        
        if self._cell_balancing_active:
            # Simulate cell balancing by slowly equalizing charge levels
            for series_group in self.cells:
                avg_soc = sum(cell.charge_level for cell in series_group) / len(series_group)
                for cell in series_group:
                    balance_rate = 0.001 * dt  # Very slow balancing
                    if cell.charge_level > avg_soc:
                        cell.charge_level -= balance_rate
                    elif cell.charge_level < avg_soc:
                        cell.charge_level += balance_rate

    def _calculate_usable_capacity(self) -> float:
        """Calculate usable battery capacity accounting for cell variations."""
        # Usable capacity limited by weakest cell
        min_capacity = float('inf')
        
        for series_group in self.cells:
            # Parallel cells add capacity
            group_capacity = sum(cell.capacity * cell.health for cell in series_group)
            min_capacity = min(min_capacity, group_capacity)
        
        return min_capacity

    def _update_statistics(self, dt: float, power: float) -> None:
        """Update power system statistics."""
        # Energy consumption
        energy_delta = power * dt / 3600.0  # Convert to Wh
        self._total_energy_consumed += energy_delta
        
        # Peak power tracking
        self._peak_power_draw = max(self._peak_power_draw, power)
        
        # Charge cycle counting (simplified)
        current_charge = self.get_charge_level()
        if current_charge < self._last_charge_level:  # Discharging
            cycle_delta = (self._last_charge_level - current_charge) / 2.0  # Full cycle = 100% -> 0% -> 100%
            self._charge_cycles += cycle_delta
        self._last_charge_level = current_charge

    def _update_history(self) -> None:
        """Update historical data for analysis."""
        # Keep last 1000 data points
        max_history = 1000
        
        self._voltage_history.append(self.get_voltage())
        if len(self._voltage_history) > max_history:
            self._voltage_history.pop(0)
        
        self._current_history.append(self.get_current_draw())
        if len(self._current_history) > max_history:
            self._current_history.pop(0)
        
        self._temperature_history.append(self._battery_temperature)
        if len(self._temperature_history) > max_history:
            self._temperature_history.pop(0)

    # Enhanced control and monitoring methods
    def simulate_regenerative_braking(self, energy: float) -> None:
        """Simulate energy recovery from regenerative braking."""
        if self.get_charge_level() < 0.95:  # Don't overcharge
            # Convert energy back to charge (simplified)
            total_capacity = sum(sum(cell.capacity for cell in series_group) 
                               for series_group in self.cells)
            
            charge_increase = energy / (self.get_voltage() * total_capacity)
            
            # Distribute charge to all cells
            for series_group in self.cells:
                for cell in series_group:
                    cell.charge_level = min(1.0, cell.charge_level + charge_increase)
            
            self._regenerative_energy += energy

    def get_power_diagnostics(self) -> Dict:
        """Get comprehensive power system diagnostics."""
        cell_voltages = []
        cell_temperatures = []
        cell_healths = []
        
        for series_group in self.cells:
            for cell in series_group:
                cell_voltages.append(cell.voltage)
                cell_temperatures.append(cell.temperature)
                cell_healths.append(cell.health)
        
        return {
            "battery": {
                "pack_voltage": self.get_voltage(),
                "pack_current": self.get_current_draw(),
                "charge_level": self.get_charge_level(),
                "remaining_time": self.get_remaining_time(),
                "temperature": self._battery_temperature,
                "is_low": self.is_low_battery(),
                "is_critical": self.is_critical_battery(),
            },
            "cells": {
                "voltages": cell_voltages,
                "temperatures": cell_temperatures,
                "health": cell_healths,
                "min_voltage": min(cell_voltages),
                "max_voltage": max(cell_voltages),
                "voltage_spread": max(cell_voltages) - min(cell_voltages),
            },
            "bms": {
                "balancing_active": self._cell_balancing_active,
                "over_temp_protection": self._over_temperature_protection,
                "under_voltage_protection": self._under_voltage_protection,
            },
            "consumers": {
                name: {
                    "power": consumer.base_power,
                    "enabled": consumer.enabled,
                    "efficiency": consumer.efficiency,
                }
                for name, consumer in self.consumers.items()
            },
            "statistics": {
                "total_energy_consumed": self._total_energy_consumed,
                "peak_power_draw": self._peak_power_draw,
                "regenerative_energy": self._regenerative_energy,
                "charge_cycles": self._charge_cycles,
            },
            "thermal": {
                "battery_temp": self._battery_temperature,
                "ambient_temp": self._ambient_temperature,
                "thermal_mass": self._thermal_mass,
            }
        }

    def set_consumer_state(self, name: str, enabled: bool) -> None:
        """Enable or disable a power consumer."""
        if name in self.consumers:
            self.consumers[name].enabled = enabled

    def set_ambient_temperature(self, temperature: float) -> None:
        """Set ambient temperature for thermal simulation."""
        self._ambient_temperature = temperature