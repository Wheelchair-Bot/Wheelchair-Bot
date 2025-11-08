"""Comprehensive tests for wheelchair_bot.controllers package."""

import unittest
from wheelchair_bot.controllers.base import Controller
from wheelchair_bot.controllers.joystick import JoystickController
from wheelchair_bot.controllers.gamepad import GamepadController


class TestControllerBase(unittest.TestCase):
    """Test cases for base Controller class."""
    
    class MockController(Controller):
        """Mock controller for testing base class."""
        
        def __init__(self):
            super().__init__("MockController")
            self._connected = False
            
        def connect(self) -> bool:
            self._connected = True
            return True
            
        def disconnect(self) -> None:
            self._connected = False
            
        def read_input(self):
            return (0.5, 0.3)
            
        def is_connected(self) -> bool:
            return self._connected
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = self.MockController()
    
    def test_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.name, "MockController")
        self.assertEqual(self.controller._deadzone, 0.1)
    
    def test_set_deadzone_valid(self):
        """Test setting valid deadzone values."""
        self.controller.set_deadzone(0.2)
        self.assertEqual(self.controller._deadzone, 0.2)
        
        self.controller.set_deadzone(0.0)
        self.assertEqual(self.controller._deadzone, 0.0)
        
        self.controller.set_deadzone(1.0)
        self.assertEqual(self.controller._deadzone, 1.0)
    
    def test_set_deadzone_clamping(self):
        """Test deadzone value clamping."""
        self.controller.set_deadzone(-0.5)
        self.assertEqual(self.controller._deadzone, 0.0)
        
        self.controller.set_deadzone(1.5)
        self.assertEqual(self.controller._deadzone, 1.0)
    
    def test_apply_deadzone_below_threshold(self):
        """Test deadzone application for values below threshold."""
        self.controller.set_deadzone(0.2)
        
        self.assertEqual(self.controller.apply_deadzone(0.1), 0.0)
        self.assertEqual(self.controller.apply_deadzone(-0.1), 0.0)
        self.assertEqual(self.controller.apply_deadzone(0.0), 0.0)
    
    def test_apply_deadzone_above_threshold(self):
        """Test deadzone application for values above threshold."""
        self.controller.set_deadzone(0.2)
        
        # Values above deadzone should be scaled
        result = self.controller.apply_deadzone(0.6)
        self.assertGreater(result, 0.0)
        self.assertLess(result, 0.6)
        
        result = self.controller.apply_deadzone(-0.6)
        self.assertLess(result, 0.0)
        self.assertGreater(result, -0.6)
    
    def test_apply_deadzone_scaling(self):
        """Test proper scaling of values beyond deadzone."""
        self.controller.set_deadzone(0.2)
        
        # At maximum input, output should be close to 1.0
        result = self.controller.apply_deadzone(1.0)
        self.assertAlmostEqual(result, 1.0, places=5)
        
        result = self.controller.apply_deadzone(-1.0)
        self.assertAlmostEqual(result, -1.0, places=5)
    
    def test_connect_disconnect(self):
        """Test controller connection and disconnection."""
        self.assertFalse(self.controller.is_connected())
        
        self.assertTrue(self.controller.connect())
        self.assertTrue(self.controller.is_connected())
        
        self.controller.disconnect()
        self.assertFalse(self.controller.is_connected())


class TestJoystickController(unittest.TestCase):
    """Test cases for JoystickController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = JoystickController()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.controller.is_connected():
            self.controller.disconnect()
    
    def test_initialization_default(self):
        """Test default initialization."""
        self.assertEqual(self.controller.joystick_type, "analog")
        self.assertEqual(self.controller.name, "Joystick_analog")
        self.assertFalse(self.controller.is_connected())
    
    def test_initialization_custom_type(self):
        """Test initialization with custom joystick type."""
        controller = JoystickController(joystick_type="digital")
        self.assertEqual(controller.joystick_type, "digital")
        self.assertEqual(controller.name, "Joystick_digital")
    
    def test_connect(self):
        """Test joystick connection."""
        result = self.controller.connect()
        self.assertTrue(result)
        self.assertTrue(self.controller.is_connected())
    
    def test_disconnect(self):
        """Test joystick disconnection."""
        self.controller.connect()
        self.controller.disconnect()
        self.assertFalse(self.controller.is_connected())
    
    def test_disconnect_resets_values(self):
        """Test that disconnect resets input values."""
        self.controller.connect()
        self.controller.set_input(0.5, 0.3)
        self.controller.disconnect()
        
        # Values should be reset
        self.assertEqual(self.controller._linear, 0.0)
        self.assertEqual(self.controller._angular, 0.0)
    
    def test_read_input_disconnected(self):
        """Test reading input when disconnected."""
        linear, angular = self.controller.read_input()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)
    
    def test_set_input_clamping(self):
        """Test that set_input clamps values to valid range."""
        self.controller.set_input(1.5, -1.5)
        self.assertEqual(self.controller._linear, 1.0)
        self.assertEqual(self.controller._angular, -1.0)
        
        self.controller.set_input(-2.0, 2.0)
        self.assertEqual(self.controller._linear, -1.0)
        self.assertEqual(self.controller._angular, 1.0)
    
    def test_read_input_with_values(self):
        """Test reading input with set values."""
        self.controller.connect()
        self.controller.set_deadzone(0.0)  # Disable deadzone for precise testing
        self.controller.set_input(0.7, 0.3)
        
        linear, angular = self.controller.read_input()
        self.assertAlmostEqual(linear, 0.7, places=5)
        self.assertAlmostEqual(angular, 0.3, places=5)
    
    def test_read_input_with_deadzone(self):
        """Test reading input with deadzone applied."""
        self.controller.connect()
        self.controller.set_deadzone(0.2)
        self.controller.set_input(0.15, 0.15)
        
        linear, angular = self.controller.read_input()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)
    
    def test_read_raw_values(self):
        """Test reading raw joystick values."""
        self.controller.set_input(0.5, 0.3)
        angular, linear = self.controller.read_raw_values()
        self.assertEqual(linear, 0.5)
        self.assertEqual(angular, 0.3)
    
    def test_multiple_connect_disconnect_cycles(self):
        """Test multiple connect/disconnect cycles."""
        for _ in range(3):
            self.controller.connect()
            self.assertTrue(self.controller.is_connected())
            self.controller.disconnect()
            self.assertFalse(self.controller.is_connected())


class TestGamepadController(unittest.TestCase):
    """Test cases for GamepadController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.controller = GamepadController()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.controller.is_connected():
            self.controller.disconnect()
    
    def test_initialization_default(self):
        """Test default initialization."""
        self.assertEqual(self.controller.controller_id, 0)
        self.assertEqual(self.controller.name, "Gamepad_0")
        self.assertIsNone(self.controller._joystick)
    
    def test_initialization_custom_id(self):
        """Test initialization with custom controller ID."""
        controller = GamepadController(controller_id=1)
        self.assertEqual(controller.controller_id, 1)
        self.assertEqual(controller.name, "Gamepad_1")
    
    def test_is_connected_initial_state(self):
        """Test initial connection state."""
        self.assertFalse(self.controller.is_connected())
    
    def test_disconnect_without_connection(self):
        """Test disconnect when not connected."""
        # Should not raise an exception
        self.controller.disconnect()
        self.assertFalse(self.controller.is_connected())
    
    def test_read_input_disconnected(self):
        """Test reading input when disconnected."""
        linear, angular = self.controller.read_input()
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)
    
    def test_get_button_state_disconnected(self):
        """Test getting button state when disconnected."""
        result = self.controller.get_button_state(0)
        self.assertFalse(result)
    
    def test_controller_name_consistency(self):
        """Test that controller name is consistent with ID."""
        for i in range(3):
            controller = GamepadController(controller_id=i)
            self.assertEqual(controller.name, f"Gamepad_{i}")


if __name__ == '__main__':
    unittest.main()
