"""Tests for wheelchair_bot controllers with controller family support."""

import unittest
from wheelchair_bot.controllers import (
    Controller,
    JoystickController,
    GamepadController,
    CONTROLLER_FAMILY_SUPPORT,
)

if CONTROLLER_FAMILY_SUPPORT:
    from wheelchair_bot.controllers import ControllerFamily


class TestControllerFamilyIntegration(unittest.TestCase):
    """Test controller family integration with wheelchair_bot controllers."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not CONTROLLER_FAMILY_SUPPORT:
            self.skipTest("Controller family support not available")
    
    def test_joystick_with_rnet_family(self):
        """Test joystick controller with R-Net family."""
        controller = JoystickController(
            joystick_type="analog",
            controller_family=ControllerFamily.RNET
        )
        controller.connect()
        
        # Verify controller family is set
        self.assertEqual(controller.get_controller_family(), ControllerFamily.RNET)
        
        # Get characteristics
        chars = controller.get_signal_characteristics()
        self.assertIsNotNone(chars)
        self.assertEqual(chars['family'], 'PG Drives R-Net')
        self.assertEqual(chars['deadzone'], '15.0%')
        
        # Test with raw signals
        controller.set_raw_signals(
            axis_x_voltage=2.5,  # Centered
            axis_y_voltage=5.0,  # Full forward
            enable_line=True
        )
        linear, angular = controller.read_input()
        self.assertGreater(linear, 0.5)
        self.assertEqual(angular, 0.0)
    
    def test_joystick_with_vr2_family(self):
        """Test joystick controller with VR2 family and speed pot."""
        controller = JoystickController(
            joystick_type="analog",
            controller_family=ControllerFamily.VR2_PILOT
        )
        controller.connect()
        
        # Test speed potentiometer effect
        controller.set_raw_signals(
            axis_y_voltage=5.0,       # Full forward
            speed_pot_voltage=2.5,    # 50% speed
            enable_line=True
        )
        linear, angular = controller.read_input()
        # Should be scaled by speed pot (~50%)
        self.assertGreater(linear, 0.3)
        self.assertLess(linear, 0.7)
    
    def test_joystick_with_shark_family(self):
        """Test joystick controller with Shark/DX family (3.3V system)."""
        controller = JoystickController(
            joystick_type="analog",
            controller_family=ControllerFamily.SHARK_DX
        )
        controller.connect()
        
        chars = controller.get_signal_characteristics()
        self.assertEqual(chars['voltage_range'], '0-3.3V')
        
        # Test with 3.3V range
        controller.set_raw_signals(
            axis_x_voltage=1.65,  # Centered (3.3V / 2)
            axis_y_voltage=3.3,   # Full forward
            enable_line=True
        )
        linear, angular = controller.read_input()
        self.assertGreater(linear, 0.7)
        self.assertEqual(angular, 0.0)
    
    def test_joystick_legacy_mode(self):
        """Test joystick controller without family (legacy mode)."""
        controller = JoystickController(joystick_type="analog")
        controller.connect()
        
        # Should work without controller family
        self.assertIsNone(controller.get_controller_family())
        
        # Test legacy set_input
        controller.set_input(linear=0.5, angular=-0.3)
        linear, angular = controller.read_input()
        # After 10% deadzone, 0.5 becomes (0.5-0.1)/(1.0-0.1) = 0.444...
        self.assertAlmostEqual(linear, 0.444, places=2)
        self.assertAlmostEqual(angular, -0.222, places=2)
    
    def test_gamepad_with_controller_family(self):
        """Test gamepad controller with controller family."""
        # Note: This test doesn't require pygame to be installed
        controller = GamepadController(
            controller_id=0,
            controller_family=ControllerFamily.VR2_PILOT
        )
        
        # Verify controller family is set
        self.assertEqual(controller.get_controller_family(), ControllerFamily.VR2_PILOT)
        
        chars = controller.get_signal_characteristics()
        self.assertIsNotNone(chars)
        self.assertEqual(chars['family'], 'PG Drives VR2/Pilot+/VSI')
    
    def test_set_input_with_family_voltage_mapping(self):
        """Test that set_input maps to appropriate voltages for family."""
        controller = JoystickController(
            joystick_type="analog",
            controller_family=ControllerFamily.RNET
        )
        controller.connect()
        
        # Set normalized input
        controller.set_input(linear=1.0, angular=0.0)
        
        # Should map to full forward voltage (5.0V for R-Net)
        linear, angular = controller.read_input()
        self.assertGreater(linear, 0.8)  # Should be close to 1.0 after processing
    
    def test_controller_family_deadzone_override(self):
        """Test that controller family deadzone overrides default."""
        # R-Net has 15% deadzone
        rnet_controller = JoystickController(
            joystick_type="analog",
            controller_family=ControllerFamily.RNET
        )
        
        # VR2 has 10% deadzone
        vr2_controller = JoystickController(
            joystick_type="analog",
            controller_family=ControllerFamily.VR2_PILOT
        )
        
        # R-Net should have larger deadzone
        self.assertGreater(rnet_controller._deadzone, vr2_controller._deadzone)
        self.assertAlmostEqual(rnet_controller._deadzone, 0.15, places=2)
        self.assertAlmostEqual(vr2_controller._deadzone, 0.10, places=2)


class TestControllerWithoutFamily(unittest.TestCase):
    """Test that controllers work without family support (backward compatibility)."""
    
    def test_joystick_basic_functionality(self):
        """Test joystick works without controller family."""
        controller = JoystickController(joystick_type="analog")
        controller.connect()
        
        self.assertTrue(controller.is_connected())
        
        controller.set_input(linear=0.7, angular=-0.4)
        linear, angular = controller.read_input()
        
        # Should apply default 10% deadzone
        self.assertGreater(linear, 0.5)
        self.assertLess(angular, -0.3)
    
    def test_controller_set_deadzone(self):
        """Test setting custom deadzone."""
        controller = JoystickController(joystick_type="analog")
        controller.connect()
        
        # Set custom deadzone
        controller.set_deadzone(0.2)
        self.assertEqual(controller._deadzone, 0.2)
        
        # Small input within deadzone should be zero
        controller.set_input(linear=0.15, angular=0.0)
        linear, angular = controller.read_input()
        self.assertEqual(linear, 0.0)


if __name__ == '__main__':
    unittest.main()
