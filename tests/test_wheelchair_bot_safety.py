"""Comprehensive tests for wheelchair_bot.safety package."""

import unittest
import time
from wheelchair_bot.safety.limiter import SpeedLimiter, AccelerationLimiter
from wheelchair_bot.safety.deadman import DeadmanSwitch


class TestSpeedLimiter(unittest.TestCase):
    """Test cases for SpeedLimiter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.limiter = SpeedLimiter()
    
    def test_initialization_default(self):
        """Test default initialization."""
        self.assertEqual(self.limiter.max_linear, 1.0)
        self.assertEqual(self.limiter.max_angular, 1.0)
    
    def test_initialization_custom(self):
        """Test initialization with custom limits."""
        limiter = SpeedLimiter(max_linear=0.5, max_angular=0.7)
        self.assertEqual(limiter.max_linear, 0.5)
        self.assertEqual(limiter.max_angular, 0.7)
    
    def test_initialization_clamping(self):
        """Test that initialization clamps values to valid range."""
        limiter = SpeedLimiter(max_linear=1.5, max_angular=-0.5)
        self.assertEqual(limiter.max_linear, 1.0)
        self.assertEqual(limiter.max_angular, 0.0)
    
    def test_limit_within_bounds(self):
        """Test limiting values within bounds."""
        linear, angular = self.limiter.limit(0.5, 0.3)
        self.assertEqual(linear, 0.5)
        self.assertEqual(angular, 0.3)
    
    def test_limit_linear_exceeds_positive(self):
        """Test limiting when linear exceeds positive bound."""
        self.limiter.max_linear = 0.5
        linear, angular = self.limiter.limit(0.8, 0.3)
        self.assertEqual(linear, 0.5)
        self.assertEqual(angular, 0.3)
    
    def test_limit_linear_exceeds_negative(self):
        """Test limiting when linear exceeds negative bound."""
        self.limiter.max_linear = 0.5
        linear, angular = self.limiter.limit(-0.8, 0.3)
        self.assertEqual(linear, -0.5)
        self.assertEqual(angular, 0.3)
    
    def test_limit_angular_exceeds_positive(self):
        """Test limiting when angular exceeds positive bound."""
        self.limiter.max_angular = 0.4
        linear, angular = self.limiter.limit(0.3, 0.7)
        self.assertEqual(linear, 0.3)
        self.assertEqual(angular, 0.4)
    
    def test_limit_angular_exceeds_negative(self):
        """Test limiting when angular exceeds negative bound."""
        self.limiter.max_angular = 0.4
        linear, angular = self.limiter.limit(0.3, -0.7)
        self.assertEqual(linear, 0.3)
        self.assertEqual(angular, -0.4)
    
    def test_limit_both_exceed(self):
        """Test limiting when both values exceed bounds."""
        self.limiter.max_linear = 0.5
        self.limiter.max_angular = 0.4
        linear, angular = self.limiter.limit(0.8, 0.9)
        self.assertEqual(linear, 0.5)
        self.assertEqual(angular, 0.4)
    
    def test_set_max_linear(self):
        """Test setting maximum linear speed."""
        self.limiter.set_max_linear(0.6)
        self.assertEqual(self.limiter.max_linear, 0.6)
    
    def test_set_max_linear_clamping(self):
        """Test that set_max_linear clamps values."""
        self.limiter.set_max_linear(1.5)
        self.assertEqual(self.limiter.max_linear, 1.0)
        
        self.limiter.set_max_linear(-0.5)
        self.assertEqual(self.limiter.max_linear, 0.0)
    
    def test_set_max_angular(self):
        """Test setting maximum angular speed."""
        self.limiter.set_max_angular(0.7)
        self.assertEqual(self.limiter.max_angular, 0.7)
    
    def test_set_max_angular_clamping(self):
        """Test that set_max_angular clamps values."""
        self.limiter.set_max_angular(1.5)
        self.assertEqual(self.limiter.max_angular, 1.0)
        
        self.limiter.set_max_angular(-0.5)
        self.assertEqual(self.limiter.max_angular, 0.0)
    
    def test_zero_limits(self):
        """Test with zero limits."""
        limiter = SpeedLimiter(max_linear=0.0, max_angular=0.0)
        linear, angular = limiter.limit(0.5, 0.5)
        self.assertEqual(linear, 0.0)
        self.assertEqual(angular, 0.0)


class TestAccelerationLimiter(unittest.TestCase):
    """Test cases for AccelerationLimiter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.limiter = AccelerationLimiter(max_linear_accel=1.0, max_angular_accel=1.0)
        self.limiter.reset()
    
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.limiter.max_linear_accel, 1.0)
        self.assertEqual(self.limiter.max_angular_accel, 1.0)
    
    def test_reset(self):
        """Test reset functionality."""
        self.limiter._last_linear = 0.5
        self.limiter._last_angular = 0.3
        
        self.limiter.reset()
        
        self.assertEqual(self.limiter._last_linear, 0.0)
        self.assertEqual(self.limiter._last_angular, 0.0)
    
    def test_limit_gradual_acceleration(self):
        """Test that acceleration is limited gradually."""
        self.limiter.reset()
        time.sleep(0.1)
        
        # Request full speed
        linear, angular = self.limiter.limit(1.0, 1.0)
        
        # Should be limited by acceleration
        self.assertLess(linear, 1.0)
        self.assertLess(angular, 1.0)
        self.assertGreater(linear, 0.0)
        self.assertGreater(angular, 0.0)
    
    def test_limit_small_changes(self):
        """Test that small changes pass through."""
        self.limiter.reset()
        time.sleep(0.1)
        
        linear, angular = self.limiter.limit(0.05, 0.05)
        
        # Small changes should be allowed
        self.assertAlmostEqual(linear, 0.05, places=2)
        self.assertAlmostEqual(angular, 0.05, places=2)
    
    def test_limit_deceleration(self):
        """Test deceleration limiting."""
        # Set initial high speed
        self.limiter._last_linear = 1.0
        self.limiter._last_angular = 1.0
        self.limiter._last_time = time.time()
        
        time.sleep(0.1)
        
        # Request stop
        linear, angular = self.limiter.limit(0.0, 0.0)
        
        # Should decelerate gradually
        self.assertGreater(linear, 0.0)
        self.assertGreater(angular, 0.0)
        self.assertLess(linear, 1.0)
        self.assertLess(angular, 1.0)
    
    def test_limit_multiple_updates(self):
        """Test multiple consecutive updates."""
        self.limiter.reset()
        
        for _ in range(5):
            time.sleep(0.05)
            linear, angular = self.limiter.limit(1.0, 1.0)
            
            # Each iteration should get closer to target
            self.assertLessEqual(abs(linear), 1.0)
            self.assertLessEqual(abs(angular), 1.0)
    
    def test_limit_handles_zero_dt(self):
        """Test that limiter handles zero time delta."""
        self.limiter.reset()
        # Don't sleep, force dt to be ~0
        
        linear, angular = self.limiter.limit(0.5, 0.5)
        
        # Should handle zero dt gracefully
        self.assertIsNotNone(linear)
        self.assertIsNotNone(angular)


class TestDeadmanSwitch(unittest.TestCase):
    """Test cases for DeadmanSwitch class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.switch = DeadmanSwitch(timeout=0.1)
    
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.switch.timeout, 0.1)
        self.assertFalse(self.switch._active)
    
    def test_initial_state_inactive(self):
        """Test that switch is initially inactive."""
        self.assertFalse(self.switch.is_active())
    
    def test_confirm_activates(self):
        """Test that confirm activates the switch."""
        self.switch.confirm()
        self.assertTrue(self.switch.is_active())
    
    def test_timeout_deactivates(self):
        """Test that timeout deactivates the switch."""
        self.switch.confirm()
        self.assertTrue(self.switch.is_active())
        
        time.sleep(0.15)
        
        self.assertFalse(self.switch.is_active())
    
    def test_confirm_resets_timer(self):
        """Test that confirm resets the timer."""
        self.switch.confirm()
        time.sleep(0.08)
        
        self.switch.confirm()  # Reset timer
        time.sleep(0.08)
        
        # Should still be active since we reset the timer
        self.assertTrue(self.switch.is_active())
    
    def test_reset(self):
        """Test reset functionality."""
        self.switch.confirm()
        self.assertTrue(self.switch.is_active())
        
        self.switch.reset()
        
        self.assertFalse(self.switch.is_active())
    
    def test_set_timeout(self):
        """Test setting timeout."""
        self.switch.set_timeout(0.5)
        self.assertEqual(self.switch.timeout, 0.5)
    
    def test_set_timeout_minimum(self):
        """Test that timeout has a minimum value."""
        self.switch.set_timeout(0.05)
        self.assertGreaterEqual(self.switch.timeout, 0.1)
    
    def test_multiple_confirm_cycles(self):
        """Test multiple confirm cycles."""
        for _ in range(3):
            self.switch.confirm()
            self.assertTrue(self.switch.is_active())
            
            time.sleep(0.15)
            self.assertFalse(self.switch.is_active())
    
    def test_is_active_when_never_confirmed(self):
        """Test is_active when never confirmed."""
        # Create new switch
        switch = DeadmanSwitch(timeout=0.1)
        self.assertFalse(switch.is_active())
    
    def test_confirm_extends_active_time(self):
        """Test that multiple confirms extend active time."""
        self.switch.confirm()
        time.sleep(0.05)
        self.assertTrue(self.switch.is_active())
        
        self.switch.confirm()
        time.sleep(0.05)
        self.assertTrue(self.switch.is_active())
        
        self.switch.confirm()
        time.sleep(0.05)
        self.assertTrue(self.switch.is_active())


if __name__ == '__main__':
    unittest.main()
