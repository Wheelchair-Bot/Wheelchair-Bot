"""Comprehensive tests for wheelchair_bot.wheelchairs package."""

import unittest
from wheelchair_bot.wheelchairs.base import Wheelchair
from wheelchair_bot.wheelchairs.models import (
    PermobilM3Corpus,
    QuantumQ6Edge,
    InvacareTPG,
    PrideJazzy,
)


class TestWheelchairBase(unittest.TestCase):
    """Test cases for base Wheelchair class."""
    
    class MockWheelchair(Wheelchair):
        """Mock wheelchair for testing base class."""
        
        def get_motor_config(self):
            return {
                "type": "test",
                "motor_count": 2,
            }
    
    def setUp(self):
        """Set up test fixtures."""
        self.wheelchair = self.MockWheelchair(
            name="Test Wheelchair",
            max_speed=2.0,
            wheel_base=0.5,
            wheel_diameter=0.3,
        )
    
    def test_initialization(self):
        """Test wheelchair initialization."""
        self.assertEqual(self.wheelchair.name, "Test Wheelchair")
        self.assertEqual(self.wheelchair.max_speed, 2.0)
        self.assertEqual(self.wheelchair.wheel_base, 0.5)
        self.assertEqual(self.wheelchair.wheel_diameter, 0.3)
    
    def test_initial_velocity_zero(self):
        """Test that initial velocity is zero."""
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)
    
    def test_set_velocity_valid(self):
        """Test setting valid velocity values."""
        self.wheelchair.set_velocity(0.5, 0.3)
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 0.5)
        self.assertEqual(angular, 0.3)
    
    def test_set_velocity_clamping_positive(self):
        """Test velocity clamping for positive values."""
        self.wheelchair.set_velocity(1.5, 1.5)
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 1.0)
        self.assertEqual(angular, 1.0)
    
    def test_set_velocity_clamping_negative(self):
        """Test velocity clamping for negative values."""
        self.wheelchair.set_velocity(-1.5, -1.5)
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, -1.0)
        self.assertEqual(angular, -1.0)
    
    def test_stop(self):
        """Test stopping the wheelchair."""
        self.wheelchair.set_velocity(0.5, 0.3)
        self.wheelchair.stop()
        
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)
    
    def test_get_info(self):
        """Test getting wheelchair information."""
        info = self.wheelchair.get_info()
        
        self.assertEqual(info["name"], "Test Wheelchair")
        self.assertEqual(info["max_speed"], 2.0)
        self.assertEqual(info["wheel_base"], 0.5)
        self.assertEqual(info["wheel_diameter"], 0.3)


class TestPermobilM3Corpus(unittest.TestCase):
    """Test cases for PermobilM3Corpus class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wheelchair = PermobilM3Corpus()
    
    def test_initialization(self):
        """Test wheelchair initialization."""
        self.assertEqual(self.wheelchair.name, "Permobil M3 Corpus")
        self.assertGreater(self.wheelchair.max_speed, 0.0)
        self.assertGreater(self.wheelchair.wheel_base, 0.0)
        self.assertGreater(self.wheelchair.wheel_diameter, 0.0)
    
    def test_motor_config(self):
        """Test motor configuration."""
        config = self.wheelchair.get_motor_config()
        
        self.assertEqual(config["type"], "mid_wheel_drive")
        self.assertEqual(config["motor_count"], 2)
        self.assertEqual(config["motor_type"], "brushless_dc")
        self.assertIn("max_voltage", config)
        self.assertIn("max_current", config)
    
    def test_velocity_control(self):
        """Test velocity control."""
        self.wheelchair.set_velocity(0.5, 0.0)
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 0.5)
        self.assertEqual(angular, 0.0)


class TestQuantumQ6Edge(unittest.TestCase):
    """Test cases for QuantumQ6Edge class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wheelchair = QuantumQ6Edge()
    
    def test_initialization(self):
        """Test wheelchair initialization."""
        self.assertEqual(self.wheelchair.name, "Quantum Q6 Edge")
        self.assertGreater(self.wheelchair.max_speed, 0.0)
        self.assertGreater(self.wheelchair.wheel_base, 0.0)
        self.assertGreater(self.wheelchair.wheel_diameter, 0.0)
    
    def test_motor_config(self):
        """Test motor configuration."""
        config = self.wheelchair.get_motor_config()
        
        self.assertEqual(config["type"], "mid_wheel_drive")
        self.assertEqual(config["motor_count"], 2)
        self.assertEqual(config["motor_type"], "brushed_dc")
        self.assertEqual(config["max_voltage"], 24)
        self.assertIn("max_current", config)
    
    def test_velocity_control(self):
        """Test velocity control."""
        self.wheelchair.set_velocity(0.8, 0.2)
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 0.8)
        self.assertEqual(angular, 0.2)
    
    def test_stop_functionality(self):
        """Test stop functionality."""
        self.wheelchair.set_velocity(0.5, 0.3)
        self.wheelchair.stop()
        
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)


class TestInvacareTPG(unittest.TestCase):
    """Test cases for InvacareTPG class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wheelchair = InvacareTPG()
    
    def test_initialization(self):
        """Test wheelchair initialization."""
        self.assertEqual(self.wheelchair.name, "Invacare TDX SP2")
        self.assertGreater(self.wheelchair.max_speed, 0.0)
        self.assertGreater(self.wheelchair.wheel_base, 0.0)
        self.assertGreater(self.wheelchair.wheel_diameter, 0.0)
    
    def test_motor_config(self):
        """Test motor configuration."""
        config = self.wheelchair.get_motor_config()
        
        self.assertEqual(config["type"], "rear_wheel_drive")
        self.assertEqual(config["motor_count"], 2)
        self.assertEqual(config["motor_type"], "brushed_dc")
        self.assertEqual(config["max_voltage"], 24)
        self.assertEqual(config["max_current"], 40)
    
    def test_get_info(self):
        """Test getting wheelchair information."""
        info = self.wheelchair.get_info()
        
        self.assertIn("name", info)
        self.assertIn("max_speed", info)
        self.assertIn("wheel_base", info)
        self.assertIn("wheel_diameter", info)


class TestPrideJazzy(unittest.TestCase):
    """Test cases for PrideJazzy class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wheelchair = PrideJazzy()
    
    def test_initialization(self):
        """Test wheelchair initialization."""
        self.assertEqual(self.wheelchair.name, "Pride Jazzy Elite HD")
        self.assertGreater(self.wheelchair.max_speed, 0.0)
        self.assertGreater(self.wheelchair.wheel_base, 0.0)
        self.assertGreater(self.wheelchair.wheel_diameter, 0.0)
    
    def test_motor_config(self):
        """Test motor configuration."""
        config = self.wheelchair.get_motor_config()
        
        self.assertEqual(config["type"], "front_wheel_drive")
        self.assertEqual(config["motor_count"], 2)
        self.assertEqual(config["motor_type"], "brushed_dc")
        self.assertEqual(config["max_voltage"], 24)
        self.assertEqual(config["max_current"], 35)
    
    def test_velocity_control(self):
        """Test velocity control."""
        self.wheelchair.set_velocity(0.4, -0.2)
        linear, angular = self.wheelchair.get_velocity()
        self.assertEqual(linear, 0.4)
        self.assertEqual(angular, -0.2)


class TestAllWheelchairModels(unittest.TestCase):
    """Test cases comparing all wheelchair models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.models = [
            PermobilM3Corpus(),
            QuantumQ6Edge(),
            InvacareTPG(),
            PrideJazzy(),
        ]
    
    def test_all_models_have_unique_names(self):
        """Test that all models have unique names."""
        names = [model.name for model in self.models]
        self.assertEqual(len(names), len(set(names)))
    
    def test_all_models_have_positive_specs(self):
        """Test that all models have positive specifications."""
        for model in self.models:
            self.assertGreater(model.max_speed, 0.0)
            self.assertGreater(model.wheel_base, 0.0)
            self.assertGreater(model.wheel_diameter, 0.0)
    
    def test_all_models_have_motor_config(self):
        """Test that all models have valid motor configuration."""
        for model in self.models:
            config = model.get_motor_config()
            
            self.assertIn("type", config)
            self.assertIn("motor_count", config)
            self.assertIn("motor_type", config)
            self.assertEqual(config["motor_count"], 2)
    
    def test_all_models_can_move(self):
        """Test that all models can control velocity."""
        for model in self.models:
            model.set_velocity(0.5, 0.3)
            linear, angular = model.get_velocity()
            
            self.assertEqual(linear, 0.5)
            self.assertEqual(angular, 0.3)
    
    def test_all_models_can_stop(self):
        """Test that all models can stop."""
        for model in self.models:
            model.set_velocity(0.5, 0.3)
            model.stop()
            
            linear, angular = model.get_velocity()
            self.assertEqual(linear, 0.0)
            self.assertEqual(angular, 0.0)
    
    def test_different_drive_types(self):
        """Test that models have different drive types."""
        drive_types = [model.get_motor_config()["type"] for model in self.models]
        
        # Should have at least 2 different drive types
        self.assertGreaterEqual(len(set(drive_types)), 2)


if __name__ == '__main__':
    unittest.main()
