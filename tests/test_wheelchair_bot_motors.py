"""Comprehensive tests for wheelchair_bot.motors package."""

import unittest
from wheelchair_bot.motors.base import MotorController
from wheelchair_bot.motors.differential import DifferentialDriveController


class TestMotorControllerBase(unittest.TestCase):
    """Test cases for base MotorController class."""
    
    class MockMotorController(MotorController):
        """Mock motor controller for testing base class."""
        
        def __init__(self):
            super().__init__("MockMotor")
            self._left_speed = 0.0
            self._right_speed = 0.0
            
        def set_motor_speeds(self, left: float, right: float) -> None:
            if self._enabled:
                self._left_speed = left
                self._right_speed = right
                
        def get_motor_speeds(self):
            return (self._left_speed, self._right_speed)
            
        def enable(self) -> None:
            self._enabled = True
            
        def disable(self) -> None:
            self._enabled = False
    
    def setUp(self):
        """Set up test fixtures."""
        self.motor = self.MockMotorController()
    
    def test_initialization(self):
        """Test motor controller initialization."""
        self.assertEqual(self.motor.name, "MockMotor")
        self.assertFalse(self.motor._enabled)
    
    def test_is_enabled_initial_state(self):
        """Test initial enabled state."""
        self.assertFalse(self.motor.is_enabled())
    
    def test_enable(self):
        """Test enabling motor controller."""
        self.motor.enable()
        self.assertTrue(self.motor.is_enabled())
    
    def test_disable(self):
        """Test disabling motor controller."""
        self.motor.enable()
        self.motor.disable()
        self.assertFalse(self.motor.is_enabled())
    
    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        self.motor.enable()
        self.motor.set_motor_speeds(0.5, 0.5)
        
        self.motor.emergency_stop()
        
        left, right = self.motor.get_motor_speeds()
        self.assertEqual(left, 0.0)
        self.assertEqual(right, 0.0)
        self.assertFalse(self.motor.is_enabled())
    
    def test_emergency_stop_when_disabled(self):
        """Test emergency stop when already disabled."""
        # Should not raise an exception
        self.motor.emergency_stop()
        self.assertFalse(self.motor.is_enabled())


class TestDifferentialDriveController(unittest.TestCase):
    """Test cases for DifferentialDriveController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = DifferentialDriveController()
        self.controller.enable()
    
    def tearDown(self):
        """Clean up after tests."""
        self.controller.disable()
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.name, "Differential_Drive")
        self.assertEqual(self.controller._left_speed, 0.0)
        self.assertEqual(self.controller._right_speed, 0.0)
    
    def test_enable(self):
        """Test enabling the controller."""
        controller = DifferentialDriveController()
        controller.enable()
        self.assertTrue(controller.is_enabled())
    
    def test_disable(self):
        """Test disabling the controller."""
        self.controller.disable()
        self.assertFalse(self.controller.is_enabled())
    
    def test_disable_stops_motors(self):
        """Test that disabling stops the motors."""
        self.controller.set_motor_speeds(0.5, 0.5)
        self.controller.disable()
        
        left, right = self.controller.get_motor_speeds()
        self.assertEqual(left, 0.0)
        self.assertEqual(right, 0.0)
    
    def test_set_motor_speeds_direct(self):
        """Test setting motor speeds directly."""
        self.controller.set_motor_speeds(0.5, 0.7)
        
        left, right = self.controller.get_motor_speeds()
        self.assertAlmostEqual(left, 0.5, places=5)
        self.assertAlmostEqual(right, 0.7, places=5)
    
    def test_set_motor_speeds_clamping(self):
        """Test that motor speeds are clamped to valid range."""
        self.controller.set_motor_speeds(1.5, -1.5)
        
        left, right = self.controller.get_motor_speeds()
        self.assertEqual(left, 1.0)
        self.assertEqual(right, -1.0)
    
    def test_set_motor_speeds_when_disabled(self):
        """Test setting motor speeds when disabled."""
        self.controller.disable()
        self.controller.set_motor_speeds(0.5, 0.5)
        
        # Speeds should not change when disabled
        left, right = self.controller.get_motor_speeds()
        self.assertEqual(left, 0.0)
        self.assertEqual(right, 0.0)
    
    def test_set_velocity_forward(self):
        """Test forward movement."""
        self.controller.set_velocity(0.5, 0.0)
        
        left, right = self.controller.get_motor_speeds()
        self.assertAlmostEqual(left, 0.5, places=5)
        self.assertAlmostEqual(right, 0.5, places=5)
    
    def test_set_velocity_backward(self):
        """Test backward movement."""
        self.controller.set_velocity(-0.5, 0.0)
        
        left, right = self.controller.get_motor_speeds()
        self.assertAlmostEqual(left, -0.5, places=5)
        self.assertAlmostEqual(right, -0.5, places=5)
    
    def test_set_velocity_turn_left(self):
        """Test turning left (in place)."""
        self.controller.set_velocity(0.0, 0.5)
        
        left, right = self.controller.get_motor_speeds()
        self.assertAlmostEqual(left, -0.5, places=5)
        self.assertAlmostEqual(right, 0.5, places=5)
    
    def test_set_velocity_turn_right(self):
        """Test turning right (in place)."""
        self.controller.set_velocity(0.0, -0.5)
        
        left, right = self.controller.get_motor_speeds()
        self.assertAlmostEqual(left, 0.5, places=5)
        self.assertAlmostEqual(right, -0.5, places=5)
    
    def test_set_velocity_forward_left_turn(self):
        """Test forward movement with left turn."""
        self.controller.set_velocity(0.5, 0.3)
        
        left, right = self.controller.get_motor_speeds()
        # Left motor should be slower than right
        self.assertLess(left, right)
        self.assertGreater(left, 0.0)
    
    def test_set_velocity_forward_right_turn(self):
        """Test forward movement with right turn."""
        self.controller.set_velocity(0.5, -0.3)
        
        left, right = self.controller.get_motor_speeds()
        # Right motor should be slower than left
        self.assertLess(right, left)
        self.assertGreater(right, 0.0)
    
    def test_set_velocity_normalization(self):
        """Test that velocity values are normalized when exceeding limits."""
        self.controller.set_velocity(0.8, 0.8)
        
        left, right = self.controller.get_motor_speeds()
        # Both values should be within -1.0 to 1.0
        self.assertLessEqual(abs(left), 1.0)
        self.assertLessEqual(abs(right), 1.0)
    
    def test_get_velocity_from_forward(self):
        """Test getting velocity from forward motor speeds."""
        self.controller.set_velocity(0.6, 0.0)
        
        linear, angular = self.controller.get_velocity()
        self.assertAlmostEqual(linear, 0.6, places=5)
        self.assertAlmostEqual(angular, 0.0, places=5)
    
    def test_get_velocity_from_turn(self):
        """Test getting velocity from turning motor speeds."""
        self.controller.set_velocity(0.0, 0.4)
        
        linear, angular = self.controller.get_velocity()
        self.assertAlmostEqual(linear, 0.0, places=5)
        self.assertAlmostEqual(angular, 0.4, places=5)
    
    def test_get_velocity_from_mixed_motion(self):
        """Test getting velocity from mixed motion."""
        self.controller.set_velocity(0.5, 0.3)
        
        linear, angular = self.controller.get_velocity()
        # Should approximately recover original values
        self.assertAlmostEqual(linear, 0.5, places=1)
        self.assertAlmostEqual(angular, 0.3, places=1)
    
    def test_stop_from_motion(self):
        """Test stopping from motion."""
        self.controller.set_velocity(0.5, 0.3)
        self.controller.set_velocity(0.0, 0.0)
        
        left, right = self.controller.get_motor_speeds()
        self.assertEqual(left, 0.0)
        self.assertEqual(right, 0.0)
    
    def test_emergency_stop_functionality(self):
        """Test emergency stop."""
        self.controller.set_velocity(0.8, 0.5)
        self.controller.emergency_stop()
        
        left, right = self.controller.get_motor_speeds()
        self.assertEqual(left, 0.0)
        self.assertEqual(right, 0.0)
        self.assertFalse(self.controller.is_enabled())
    
    def test_multiple_velocity_changes(self):
        """Test multiple velocity changes."""
        velocities = [
            (0.5, 0.0),
            (0.0, 0.5),
            (-0.5, 0.0),
            (0.0, -0.5),
            (0.0, 0.0)
        ]
        
        for linear, angular in velocities:
            self.controller.set_velocity(linear, angular)
            left, right = self.controller.get_motor_speeds()
            
            # Verify speeds are within valid range
            self.assertLessEqual(abs(left), 1.0)
            self.assertLessEqual(abs(right), 1.0)


if __name__ == '__main__':
    unittest.main()
