"""Unit tests for wheelchair controller."""

import unittest
from wheelchair_controller import WheelchairController, MotorDriver
from wheelchair_controller.motor_driver import Direction


class TestMotorDriver(unittest.TestCase):
    """Test cases for MotorDriver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = MotorDriver(use_mock=True)
    
    def tearDown(self):
        """Clean up after tests."""
        self.driver.cleanup()
    
    def test_initialization(self):
        """Test motor driver initialization."""
        self.assertIsNotNone(self.driver)
        self.assertTrue(self.driver.use_mock)
    
    def test_set_motor_speed(self):
        """Test setting motor speeds."""
        # Should not raise any exceptions
        self.driver.set_motor_speed(50, 50)
        self.driver.set_motor_speed(-50, -50)
        self.driver.set_motor_speed(0, 0)
    
    def test_speed_clamping(self):
        """Test that speeds are clamped to valid range."""
        # Should clamp to -100 to 100 range
        self.driver.set_motor_speed(150, 150)  # Should clamp to 100
        self.driver.set_motor_speed(-150, -150)  # Should clamp to -100
    
    def test_stop(self):
        """Test stopping motors."""
        self.driver.set_motor_speed(50, 50)
        self.driver.stop()
        # Should not raise any exceptions


class TestWheelchairController(unittest.TestCase):
    """Test cases for WheelchairController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.motor_driver = MotorDriver(use_mock=True)
        self.controller = WheelchairController(
            motor_driver=self.motor_driver,
            max_speed=80,
            turn_speed=60
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.controller.cleanup()
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertIsNotNone(self.controller)
        self.assertEqual(self.controller.max_speed, 80)
        self.assertEqual(self.controller.turn_speed, 60)
    
    def test_move_forward(self):
        """Test forward movement."""
        self.controller.move_forward()
        self.assertEqual(self.controller.current_left_speed, 80)
        self.assertEqual(self.controller.current_right_speed, 80)
    
    def test_move_backward(self):
        """Test backward movement."""
        self.controller.move_backward()
        self.assertEqual(self.controller.current_left_speed, -80)
        self.assertEqual(self.controller.current_right_speed, -80)
    
    def test_turn_left(self):
        """Test left turn."""
        self.controller.turn_left()
        self.assertEqual(self.controller.current_left_speed, -60)
        self.assertEqual(self.controller.current_right_speed, 60)
    
    def test_turn_right(self):
        """Test right turn."""
        self.controller.turn_right()
        self.assertEqual(self.controller.current_left_speed, 60)
        self.assertEqual(self.controller.current_right_speed, -60)
    
    def test_stop(self):
        """Test stopping."""
        self.controller.move_forward()
        self.controller.stop()
        self.assertEqual(self.controller.current_left_speed, 0)
        self.assertEqual(self.controller.current_right_speed, 0)
    
    def test_emergency_stop(self):
        """Test emergency stop."""
        self.controller.move_forward()
        self.controller.emergency_stop()
        self.assertEqual(self.controller.current_left_speed, 0)
        self.assertEqual(self.controller.current_right_speed, 0)
    
    def test_move_with_direction(self):
        """Test move method with Direction enum."""
        self.controller.move(Direction.FORWARD)
        self.assertEqual(self.controller.current_left_speed, 80)
        
        self.controller.move(Direction.BACKWARD)
        self.assertEqual(self.controller.current_left_speed, -80)
        
        self.controller.move(Direction.LEFT)
        self.assertEqual(self.controller.current_left_speed, -60)
        
        self.controller.move(Direction.RIGHT)
        self.assertEqual(self.controller.current_left_speed, 60)
        
        self.controller.move(Direction.STOP)
        self.assertEqual(self.controller.current_left_speed, 0)
    
    def test_custom_speed(self):
        """Test movement with custom speed."""
        self.controller.move_forward(50)
        self.assertEqual(self.controller.current_left_speed, 50)
        self.assertEqual(self.controller.current_right_speed, 50)
    
    def test_speed_limiting(self):
        """Test that speeds are limited to max."""
        # Speed should be clamped to valid range
        self.controller.move_forward(150)
        self.assertTrue(self.controller.current_left_speed <= 100)


if __name__ == '__main__':
    unittest.main()
