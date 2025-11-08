"""Tests for emulated power system."""

import pytest
from wheelchair.config import PowerConfig
from wheelchair.emulator.power import EmulatedPowerSystem


class TestEmulatedPowerSystem:
    """Test cases for EmulatedPowerSystem."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return PowerConfig(
            battery_capacity=50.0,
            nominal_voltage=24.0,
            min_voltage=20.0,
            max_voltage=29.4,
            idle_power=10.0,
            motor_efficiency=0.8,
        )

    @pytest.fixture
    def power(self, config):
        """Create power system instance."""
        return EmulatedPowerSystem(config)

    def test_initialization(self, power, config):
        """Test power system initializes to full charge."""
        assert power.get_voltage() == config.max_voltage
        assert power.get_percent() == 100.0

    def test_discharge(self, power):
        """Test battery discharges with power consumption."""
        initial_percent = power.get_percent()

        # Draw power for 1 hour
        power.update(3600.0, 100.0)  # 100W for 1 hour

        # Battery should have discharged
        assert power.get_percent() < initial_percent

    def test_voltage_decreases_with_discharge(self, power, config):
        """Test voltage decreases as battery discharges."""
        initial_voltage = power.get_voltage()

        # Discharge significantly
        for _ in range(10):
            power.update(360.0, 100.0)  # 10 hours total

        final_voltage = power.get_voltage()
        assert final_voltage < initial_voltage
        assert final_voltage >= config.min_voltage

    def test_percent_bounded(self, power):
        """Test battery percent stays in valid range."""
        # Over-discharge
        for _ in range(100):
            power.update(3600.0, 1000.0)

        percent = power.get_percent()
        assert 0.0 <= percent <= 100.0

    def test_voltage_bounded(self, power, config):
        """Test voltage stays in valid range."""
        # Over-discharge
        for _ in range(100):
            power.update(3600.0, 1000.0)

        voltage = power.get_voltage()
        assert config.min_voltage <= voltage <= config.max_voltage

    def test_reset(self, power, config):
        """Test resetting battery to full charge."""
        # Discharge
        power.update(3600.0, 100.0)

        # Reset
        power.reset()

        assert power.get_percent() == 100.0
        assert power.get_voltage() == config.max_voltage

    def test_set_charge_level(self, power):
        """Test manually setting charge level."""
        power.set_charge_level(50.0)
        assert power.get_percent() == 50.0

    def test_set_charge_level_clamping(self, power):
        """Test charge level is clamped to valid range."""
        power.set_charge_level(150.0)
        assert power.get_percent() == 100.0

        power.set_charge_level(-10.0)
        assert power.get_percent() == 0.0

    def test_power_consumption_model(self, power):
        """Test power consumption affects discharge rate."""
        # Low power consumption
        power1 = EmulatedPowerSystem(PowerConfig())
        power1.update(3600.0, 10.0)
        percent1 = power1.get_percent()

        # High power consumption
        power2 = EmulatedPowerSystem(PowerConfig())
        power2.update(3600.0, 100.0)
        percent2 = power2.get_percent()

        # Higher power should discharge more
        assert percent2 < percent1

    def test_voltage_charge_relationship(self, power):
        """Test voltage correlates with charge level."""
        # Set different charge levels and check voltage
        power.set_charge_level(100.0)
        v100 = power.get_voltage()

        power.set_charge_level(50.0)
        v50 = power.get_voltage()

        power.set_charge_level(25.0)
        v25 = power.get_voltage()

        # Voltage should decrease with charge
        assert v100 > v50 > v25
