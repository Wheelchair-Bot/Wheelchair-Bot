"""Comprehensive tests for shared package."""

import unittest
from wheelchair_bot_shared.types import Direction, BotStatus, MoveCommand, CommandResponse
from wheelchair_bot_shared.constants import (
    MIN_SPEED,
    MAX_SPEED,
    DEFAULT_SPEED,
    BATTERY_LOW_THRESHOLD,
    BATTERY_CRITICAL_THRESHOLD,
    API_BASE_URL,
    API_STATUS_ENDPOINT,
    API_MOVE_ENDPOINT,
)
import pytest


class TestDirectionEnum(unittest.TestCase):
    """Test cases for Direction enum."""
    
    def test_forward_value(self):
        """Test FORWARD direction value."""
        self.assertEqual(Direction.FORWARD, "forward")
        self.assertEqual(Direction.FORWARD.value, "forward")
    
    def test_backward_value(self):
        """Test BACKWARD direction value."""
        self.assertEqual(Direction.BACKWARD, "backward")
        self.assertEqual(Direction.BACKWARD.value, "backward")
    
    def test_left_value(self):
        """Test LEFT direction value."""
        self.assertEqual(Direction.LEFT, "left")
        self.assertEqual(Direction.LEFT.value, "left")
    
    def test_right_value(self):
        """Test RIGHT direction value."""
        self.assertEqual(Direction.RIGHT, "right")
        self.assertEqual(Direction.RIGHT.value, "right")
    
    def test_stop_value(self):
        """Test STOP direction value."""
        self.assertEqual(Direction.STOP, "stop")
        self.assertEqual(Direction.STOP.value, "stop")
    
    def test_all_directions(self):
        """Test that all directions are accessible."""
        directions = [
            Direction.FORWARD,
            Direction.BACKWARD,
            Direction.LEFT,
            Direction.RIGHT,
            Direction.STOP,
        ]
        self.assertEqual(len(directions), 5)


class TestBotStatus(unittest.TestCase):
    """Test cases for BotStatus model."""
    
    def test_valid_status_creation(self):
        """Test creating valid BotStatus."""
        status = BotStatus(
            battery_level=75,
            is_moving=True,
            speed=60,
            direction=Direction.FORWARD,
        )
        self.assertEqual(status.battery_level, 75)
        self.assertTrue(status.is_moving)
        self.assertEqual(status.speed, 60)
        self.assertEqual(status.direction, Direction.FORWARD)
    
    def test_minimum_battery_level(self):
        """Test minimum battery level."""
        status = BotStatus(battery_level=0, is_moving=False, speed=0)
        self.assertEqual(status.battery_level, 0)
    
    def test_maximum_battery_level(self):
        """Test maximum battery level."""
        status = BotStatus(battery_level=100, is_moving=False, speed=0)
        self.assertEqual(status.battery_level, 100)
    
    def test_default_is_moving(self):
        """Test default is_moving value."""
        status = BotStatus(battery_level=50, speed=0)
        self.assertFalse(status.is_moving)
    
    def test_default_direction(self):
        """Test default direction value."""
        status = BotStatus(battery_level=50, is_moving=False, speed=0)
        self.assertIsNone(status.direction)
    
    def test_none_direction(self):
        """Test that direction can be None."""
        status = BotStatus(battery_level=50, is_moving=False, speed=0, direction=None)
        self.assertIsNone(status.direction)


class TestMoveCommand(unittest.TestCase):
    """Test cases for MoveCommand model."""
    
    def test_valid_command_creation(self):
        """Test creating valid MoveCommand."""
        cmd = MoveCommand(direction=Direction.FORWARD, speed=75)
        self.assertEqual(cmd.direction, Direction.FORWARD)
        self.assertEqual(cmd.speed, 75)
    
    def test_default_speed(self):
        """Test default speed value."""
        cmd = MoveCommand(direction=Direction.STOP)
        self.assertEqual(cmd.speed, 50)
    
    def test_minimum_speed(self):
        """Test minimum speed value."""
        cmd = MoveCommand(direction=Direction.FORWARD, speed=0)
        self.assertEqual(cmd.speed, 0)
    
    def test_maximum_speed(self):
        """Test maximum speed value."""
        cmd = MoveCommand(direction=Direction.FORWARD, speed=100)
        self.assertEqual(cmd.speed, 100)
    
    def test_all_directions_valid(self):
        """Test that all directions work with MoveCommand."""
        directions = [
            Direction.FORWARD,
            Direction.BACKWARD,
            Direction.LEFT,
            Direction.RIGHT,
            Direction.STOP,
        ]
        
        for direction in directions:
            cmd = MoveCommand(direction=direction, speed=50)
            self.assertEqual(cmd.direction, direction)


class TestCommandResponse(unittest.TestCase):
    """Test cases for CommandResponse model."""
    
    def test_success_response(self):
        """Test creating success response."""
        response = CommandResponse(status="success", message="Operation completed")
        self.assertEqual(response.status, "success")
        self.assertEqual(response.message, "Operation completed")
    
    def test_error_response(self):
        """Test creating error response."""
        response = CommandResponse(status="error", message="Operation failed")
        self.assertEqual(response.status, "error")
        self.assertEqual(response.message, "Operation failed")
    
    def test_default_message(self):
        """Test default message value."""
        response = CommandResponse(status="success")
        self.assertIsNone(response.message)
    
    def test_none_message(self):
        """Test that message can be None."""
        response = CommandResponse(status="success", message=None)
        self.assertIsNone(response.message)


class TestConstants(unittest.TestCase):
    """Test cases for shared constants."""
    
    def test_min_speed(self):
        """Test MIN_SPEED constant."""
        self.assertEqual(MIN_SPEED, 0)
    
    def test_max_speed(self):
        """Test MAX_SPEED constant."""
        self.assertEqual(MAX_SPEED, 100)
    
    def test_default_speed(self):
        """Test DEFAULT_SPEED constant."""
        self.assertEqual(DEFAULT_SPEED, 50)
    
    def test_speed_range_valid(self):
        """Test that speed range is valid."""
        self.assertLessEqual(MIN_SPEED, DEFAULT_SPEED)
        self.assertLessEqual(DEFAULT_SPEED, MAX_SPEED)
    
    def test_battery_low_threshold(self):
        """Test BATTERY_LOW_THRESHOLD constant."""
        self.assertEqual(BATTERY_LOW_THRESHOLD, 20)
    
    def test_battery_critical_threshold(self):
        """Test BATTERY_CRITICAL_THRESHOLD constant."""
        self.assertEqual(BATTERY_CRITICAL_THRESHOLD, 10)
    
    def test_battery_thresholds_valid(self):
        """Test that battery thresholds are valid."""
        self.assertLess(BATTERY_CRITICAL_THRESHOLD, BATTERY_LOW_THRESHOLD)
        self.assertLessEqual(BATTERY_LOW_THRESHOLD, 100)
    
    def test_api_base_url(self):
        """Test API_BASE_URL constant."""
        self.assertEqual(API_BASE_URL, "http://localhost:8000")
        self.assertTrue(API_BASE_URL.startswith("http"))
    
    def test_api_status_endpoint(self):
        """Test API_STATUS_ENDPOINT constant."""
        self.assertEqual(API_STATUS_ENDPOINT, "/api/status")
        self.assertTrue(API_STATUS_ENDPOINT.startswith("/"))
    
    def test_api_move_endpoint(self):
        """Test API_MOVE_ENDPOINT constant."""
        self.assertEqual(API_MOVE_ENDPOINT, "/api/move")
        self.assertTrue(API_MOVE_ENDPOINT.startswith("/"))


if __name__ == '__main__':
    unittest.main()
