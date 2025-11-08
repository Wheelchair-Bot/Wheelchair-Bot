"""Comprehensive tests for wheelchair_bot.system module."""

import unittest
from wheelchair_bot.system import WheelchairControlSystem
from wheelchair_bot.wheelchairs.models import QuantumQ6Edge
from wheelchair_bot.controllers.joystick import JoystickController
from wheelchair_bot.motors.differential import DifferentialDriveController


class TestWheelchairControlSystem(unittest.TestCase):
    """Test cases for WheelchairControlSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wheelchair = QuantumQ6Edge()
        self.controller = JoystickController()
        self.motor_controller = DifferentialDriveController()
        
        self.system = WheelchairControlSystem(
            wheelchair=self.wheelchair,
            controller=self.controller,
            motor_controller=self.motor_controller,
        )
    
    def tearDown(self):
        """Clean up after tests."""
        if self.system._running:
            self.system.stop()
    
    def test_initialization(self):
        """Test system initialization."""
        self.assertIsNotNone(self.system.wheelchair)
        self.assertIsNotNone(self.system.controller)
        self.assertIsNotNone(self.system.motor_controller)
        self.assertIsNotNone(self.system.speed_limiter)
        self.assertIsNotNone(self.system.accel_limiter)
        self.assertIsNotNone(self.system.deadman_switch)
    
    def test_initial_state(self):
        """Test initial system state."""
        self.assertFalse(self.system._running)
        self.assertFalse(self.system._emergency_stop)
    
    def test_start_system(self):
        """Test starting the system."""
        result = self.system.start()
        self.assertTrue(result)
        self.assertTrue(self.system._running)
        self.assertTrue(self.system.controller.is_connected())
        self.assertTrue(self.system.motor_controller.is_enabled())
    
    def test_stop_system(self):
        """Test stopping the system."""
        self.system.start()
        self.system.stop()
        
        self.assertFalse(self.system._running)
        self.assertFalse(self.system.controller.is_connected())
        self.assertFalse(self.system.motor_controller.is_enabled())
    
    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        self.system.start()
        self.system.emergency_stop_trigger()
        
        self.assertTrue(self.system._emergency_stop)
        
        linear, angular = self.system.wheelchair.get_velocity()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)
        
        self.assertFalse(self.system.motor_controller.is_enabled())
    
    def test_update_when_stopped(self):
        """Test update when system is stopped."""
        # Should not raise exception
        self.system.update()
    
    def test_update_when_emergency_stopped(self):
        """Test update when emergency stopped."""
        self.system.start()
        self.system.emergency_stop_trigger()
        
        # Should not process any commands
        self.system.update()
    
    def test_update_with_deadman_inactive(self):
        """Test update with inactive deadman switch."""
        self.system.start()
        # Don't confirm deadman switch
        
        self.system.update()
        
        # Wheelchair should be stopped
        linear, angular = self.system.wheelchair.get_velocity()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)
    
    def test_update_with_active_deadman(self):
        """Test update with active deadman switch."""
        self.system.start()
        self.system.deadman_switch.confirm()
        self.system.controller.set_input(0.5, 0.0)
        
        self.system.update()
        
        # Should have some velocity
        linear, angular = self.system.wheelchair.get_velocity()
        self.assertGreater(abs(linear), 0.0)
    
    def test_get_status_stopped(self):
        """Test getting status when stopped."""
        status = self.system.get_status()
        
        self.assertFalse(status["running"])
        self.assertFalse(status["emergency_stop"])
        self.assertIn("wheelchair", status)
        self.assertIn("velocity", status)
        self.assertIn("motor_speeds", status)
    
    def test_get_status_running(self):
        """Test getting status when running."""
        self.system.start()
        status = self.system.get_status()
        
        self.assertTrue(status["running"])
        self.assertFalse(status["emergency_stop"])
        self.assertTrue(status["controller_connected"])
        self.assertTrue(status["motors_enabled"])
    
    def test_get_status_emergency_stopped(self):
        """Test getting status when emergency stopped."""
        self.system.start()
        self.system.emergency_stop_trigger()
        status = self.system.get_status()
        
        self.assertTrue(status["emergency_stop"])
    
    def test_speed_limiter_integration(self):
        """Test that speed limiter is applied."""
        self.system.start()
        self.system.deadman_switch.confirm()
        
        # Set very high input
        self.system.controller.set_input(1.0, 1.0)
        self.system.update()
        
        linear, angular = self.system.wheelchair.get_velocity()
        
        # Should be limited by speed limiter (max 0.8)
        self.assertLessEqual(abs(linear), 0.8)
        self.assertLessEqual(abs(angular), 0.8)
    
    def test_acceleration_limiter_integration(self):
        """Test that acceleration limiter is applied."""
        self.system.start()
        self.system.deadman_switch.confirm()
        
        # Request immediate full speed
        self.system.controller.set_input(1.0, 1.0)
        self.system.update()
        
        linear, angular = self.system.wheelchair.get_velocity()
        
        # Should be limited by acceleration limiter (won't reach full speed immediately)
        self.assertLess(linear, 0.8)
        self.assertLess(angular, 0.8)
    
    def test_multiple_start_stop_cycles(self):
        """Test multiple start/stop cycles."""
        for _ in range(3):
            self.assertTrue(self.system.start())
            self.assertTrue(self.system._running)
            
            self.system.stop()
            self.assertFalse(self.system._running)
    
    def test_status_wheelchair_info(self):
        """Test that status includes wheelchair info."""
        status = self.system.get_status()
        
        wheelchair_info = status["wheelchair"]
        self.assertEqual(wheelchair_info["name"], "Quantum Q6 Edge")
        self.assertIn("max_speed", wheelchair_info)
        self.assertIn("wheel_base", wheelchair_info)
        self.assertIn("wheel_diameter", wheelchair_info)
    
    def test_status_velocity_info(self):
        """Test that status includes velocity info."""
        self.system.start()
        self.system.deadman_switch.confirm()
        self.system.controller.set_input(0.5, 0.3)
        self.system.update()
        
        status = self.system.get_status()
        
        self.assertIn("linear", status["velocity"])
        self.assertIn("angular", status["velocity"])
    
    def test_status_motor_speeds(self):
        """Test that status includes motor speeds."""
        self.system.start()
        self.system.deadman_switch.confirm()
        self.system.controller.set_input(0.5, 0.0)
        self.system.update()
        
        status = self.system.get_status()
        
        self.assertIn("left", status["motor_speeds"])
        self.assertIn("right", status["motor_speeds"])
    
    def test_deadman_status(self):
        """Test deadman switch status."""
        status = self.system.get_status()
        self.assertIn("deadman_active", status)
        self.assertFalse(status["deadman_active"])
        
        self.system.deadman_switch.confirm()
        status = self.system.get_status()
        self.assertTrue(status["deadman_active"])
    
    def test_controller_input_processing(self):
        """Test that controller input is processed correctly."""
        self.system.start()
        self.system.deadman_switch.confirm()
        
        # Set specific input
        self.system.controller.set_deadzone(0.0)
        self.system.controller.set_input(0.6, 0.0)
        self.system.update()
        
        linear, angular = self.system.wheelchair.get_velocity()
        
        # Should have forward velocity
        self.assertGreater(linear, 0.0)
        self.assertAlmostEqual(angular, 0.0, places=1)


if __name__ == '__main__':
    unittest.main()
