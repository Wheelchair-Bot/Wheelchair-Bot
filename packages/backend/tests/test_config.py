"""Comprehensive tests for backend package."""

import unittest
from packages.backend.wheelchair_bot.config import Settings, settings


class TestSettings(unittest.TestCase):
    """Test cases for Settings class."""
    
    def test_default_app_name(self):
        """Test default application name."""
        s = Settings()
        self.assertEqual(s.app_name, "Wheelchair Bot API")
    
    def test_default_debug(self):
        """Test default debug setting."""
        s = Settings()
        self.assertFalse(s.debug)
    
    def test_default_host(self):
        """Test default host setting."""
        s = Settings()
        self.assertEqual(s.host, "0.0.0.0")
    
    def test_default_port(self):
        """Test default port setting."""
        s = Settings()
        self.assertEqual(s.port, 8000)
    
    def test_default_max_speed(self):
        """Test default max speed setting."""
        s = Settings()
        self.assertEqual(s.max_speed, 100)
    
    def test_default_min_speed(self):
        """Test default min speed setting."""
        s = Settings()
        self.assertEqual(s.min_speed, 0)
    
    def test_custom_app_name(self):
        """Test custom application name."""
        s = Settings(app_name="Custom Name")
        self.assertEqual(s.app_name, "Custom Name")
    
    def test_custom_debug(self):
        """Test custom debug setting."""
        s = Settings(debug=True)
        self.assertTrue(s.debug)
    
    def test_custom_host(self):
        """Test custom host setting."""
        s = Settings(host="127.0.0.1")
        self.assertEqual(s.host, "127.0.0.1")
    
    def test_custom_port(self):
        """Test custom port setting."""
        s = Settings(port=3000)
        self.assertEqual(s.port, 3000)
    
    def test_custom_max_speed(self):
        """Test custom max speed setting."""
        s = Settings(max_speed=80)
        self.assertEqual(s.max_speed, 80)
    
    def test_custom_min_speed(self):
        """Test custom min speed setting."""
        s = Settings(min_speed=10)
        self.assertEqual(s.min_speed, 10)
    
    def test_settings_singleton(self):
        """Test that settings is a singleton instance."""
        self.assertIsNotNone(settings)
        self.assertIsInstance(settings, Settings)
    
    def test_speed_range_valid(self):
        """Test that speed range is valid."""
        s = Settings()
        self.assertLessEqual(s.min_speed, s.max_speed)
    
    def test_port_positive(self):
        """Test that port is positive."""
        s = Settings()
        self.assertGreater(s.port, 0)
    
    def test_all_settings_accessible(self):
        """Test that all settings are accessible."""
        s = Settings()
        
        # Should not raise AttributeError
        _ = s.app_name
        _ = s.debug
        _ = s.host
        _ = s.port
        _ = s.max_speed
        _ = s.min_speed
    
    def test_settings_immutable_after_creation(self):
        """Test that settings can be modified."""
        s = Settings()
        
        # Should be able to modify
        s.debug = True
        self.assertTrue(s.debug)


class TestBackendIntegration(unittest.TestCase):
    """Integration tests for backend package."""
    
    def test_settings_import(self):
        """Test that settings can be imported."""
        from packages.backend.wheelchair_bot.config import settings as imported_settings
        self.assertIsNotNone(imported_settings)
    
    def test_config_module_exists(self):
        """Test that config module exists."""
        import packages.backend.wheelchair_bot.config as config
        self.assertIsNotNone(config)


if __name__ == '__main__':
    unittest.main()
