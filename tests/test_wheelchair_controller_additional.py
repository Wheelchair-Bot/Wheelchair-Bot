"""Additional comprehensive tests for wheelchair_controller package."""

import unittest
from wheelchair_controller import WheelchairController, MotorDriver
from wheelchair_controller.motor_driver import Direction


class TestMotorDriverAdditional(unittest.TestCase):
    """Additional test cases for MotorDriver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.driver = MotorDriver(use_mock=True)
    
    def tearDown(self):
        """Clean up after tests."""
        self.driver.cleanup()
    
    def test_forward_movement(self):
        """Test forward movement command."""
        self.driver.set_motor_speed(50, 50)
        # Should not raise any exceptions
    
    def test_backward_movement(self):
        """Test backward movement command."""
        self.driver.set_motor_speed(-50, -50)
        # Should not raise any exceptions
    
    def test_left_turn(self):
        """Test left turn command."""
        self.driver.set_motor_speed(-50, 50)
        # Should not raise any exceptions
    
    def test_right_turn(self):
        """Test right turn command."""
        self.driver.set_motor_speed(50, -50)
        # Should not raise any exceptions
    
    def test_multiple_direction_changes(self):
        """Test multiple direction changes."""
        directions = [
            (Direction.FORWARD, 50),
            (Direction.BACKWARD, 40),
            (Direction.LEFT, 30),
            (Direction.RIGHT, 60),
            (Direction.STOP, 0),
        ]
        
        for direction, speed in directions:
            if direction == Direction.FORWARD:
                self.driver.set_motor_speed(speed, speed)
            elif direction == Direction.BACKWARD:
                self.driver.set_motor_speed(-speed, -speed)
            elif direction == Direction.LEFT:
                self.driver.set_motor_speed(-speed, speed)
            elif direction == Direction.RIGHT:
                self.driver.set_motor_speed(speed, -speed)
            elif direction == Direction.STOP:
                self.driver.stop()
    
    def test_zero_speed(self):
        """Test setting zero speed."""
        self.driver.set_motor_speed(0, 0)
        # Should not raise any exceptions


class TestWheelchairControllerAdditional(unittest.TestCase):
    """Additional test cases for WheelchairController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.motor_driver = MotorDriver(use_mock=True)
        self.controller = WheelchairController(
            motor_driver=self.motor_driver,
            max_speed=100,
            turn_speed=80
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.controller.cleanup()
    
    def test_max_speed_configuration(self):
        """Test max speed configuration."""
        self.assertEqual(self.controller.max_speed, 100)
    
    def test_turn_speed_configuration(self):
        """Test turn speed configuration."""
        self.assertEqual(self.controller.turn_speed, 80)
    
    def test_smooth_acceleration(self):
        """Test smooth acceleration from stop to full speed."""
        speeds = [20, 40, 60, 80]
        
        for speed in speeds:
            self.controller.move_forward(speed)
            self.assertEqual(self.controller.current_left_speed, speed)
            self.assertEqual(self.controller.current_right_speed, speed)
    
    def test_smooth_deceleration(self):
        """Test smooth deceleration from full speed to stop."""
        speeds = [80, 60, 40, 20, 0]
        
        for speed in speeds:
            if speed > 0:
                self.controller.move_forward(speed)
                self.assertGreaterEqual(self.controller.current_left_speed, 0)
            else:
                self.controller.stop()
                self.assertEqual(self.controller.current_left_speed, 0)
    
    def test_differential_steering_right(self):
        """Test differential steering while moving forward right."""
        self.controller.move_forward(80)
        # Then turn right slightly - right motor should slow down
        self.controller.turn_right()
        
        # After turn, verify we can go back to forward
        self.controller.move_forward(80)
        self.assertEqual(self.controller.current_left_speed, 80)
    
    def test_differential_steering_left(self):
        """Test differential steering while moving forward left."""
        self.controller.move_forward(80)
        # Then turn left slightly - left motor should slow down
        self.controller.turn_left()
        
        # After turn, verify we can go back to forward
        self.controller.move_forward(80)
        self.assertEqual(self.controller.current_left_speed, 80)
    
    def test_reverse_turn_right(self):
        """Test turning right while moving backward."""
        self.controller.move_backward(50)
        self.assertEqual(self.controller.current_left_speed, -50)
        self.assertEqual(self.controller.current_right_speed, -50)
    
    def test_reverse_turn_left(self):
        """Test turning left while moving backward."""
        self.controller.move_backward(50)
        self.assertEqual(self.controller.current_left_speed, -50)
        self.assertEqual(self.controller.current_right_speed, -50)
    
    def test_emergency_stop_from_full_speed(self):
        """Test emergency stop from full speed."""
        self.controller.move_forward(100)
        self.controller.emergency_stop()
        
        self.assertEqual(self.controller.current_left_speed, 0)
        self.assertEqual(self.controller.current_right_speed, 0)
    
    def test_emergency_stop_from_turn(self):
        """Test emergency stop while turning."""
        self.controller.turn_left()
        self.controller.emergency_stop()
        
        self.assertEqual(self.controller.current_left_speed, 0)
        self.assertEqual(self.controller.current_right_speed, 0)


if __name__ == '__main__':
    unittest.main()
