"""Tests for emulated controller with controller family support."""

import pytest
from wheelchair.interfaces import ControllerInput
from wheelchair.emulator.controller import EmulatedController
from wheelchair.controller_families import ControllerFamily


class TestEmulatedControllerWithFamilies:
    """Test EmulatedController with controller family support."""

    def test_default_initialization(self):
        """Test controller initializes without a family (legacy mode)."""
        controller = EmulatedController()
        assert controller.is_connected()
        assert controller.get_controller_family() is None
        input_data = controller.read_input()
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_initialization_with_rnet(self):
        """Test controller initializes with R-Net family."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)
        assert controller.is_connected()
        assert controller.get_controller_family() == ControllerFamily.RNET

    def test_initialization_with_vr2(self):
        """Test controller initializes with VR2 family."""
        controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)
        assert controller.get_controller_family() == ControllerFamily.VR2_PILOT

    def test_set_controller_family(self):
        """Test setting controller family after initialization."""
        controller = EmulatedController()
        assert controller.get_controller_family() is None

        controller.set_controller_family(ControllerFamily.SHARK_DX)
        assert controller.get_controller_family() == ControllerFamily.SHARK_DX

    def test_legacy_set_input_still_works(self):
        """Test that legacy set_input method still works without family."""
        controller = EmulatedController()
        controller.set_input(linear=0.5, angular=-0.3)
        input_data = controller.read_input()
        assert input_data.linear == 0.5
        assert input_data.angular == -0.3

    def test_raw_signals_with_rnet(self):
        """Test setting raw signals for R-Net controller."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)

        # Set forward movement (Y-axis high voltage)
        controller.set_raw_signals(axis_x_voltage=2.5, axis_y_voltage=5.0)
        input_data = controller.read_input()
        assert input_data.linear > 0.5
        assert input_data.angular == 0.0

    def test_raw_signals_with_shark_dx(self):
        """Test setting raw signals for Shark/DX controller."""
        controller = EmulatedController(controller_family=ControllerFamily.SHARK_DX)

        # Shark uses 3.3V, center at 1.65V
        controller.set_raw_signals(axis_x_voltage=3.3, axis_y_voltage=1.65)
        input_data = controller.read_input()
        assert input_data.linear == 0.0
        assert input_data.angular > 0.5

    def test_raw_signals_with_vr2_speed_pot(self):
        """Test VR2 speed potentiometer affects output."""
        controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)

        # Full forward at 50% speed setting
        controller.set_raw_signals(
            axis_x_voltage=2.5, axis_y_voltage=5.0, speed_pot_voltage=2.5
        )
        input_data = controller.read_input()
        # Should be scaled by ~50%
        assert 0.3 < input_data.linear < 0.7

    def test_raw_signals_with_linx_bus_data(self):
        """Test LiNX controller with digital bus data."""
        controller = EmulatedController(controller_family=ControllerFamily.LINX_DX)

        bus_data = {
            "linear_axis": 0.8,
            "angular_axis": -0.5,
            "enable": True,
            "emergency_stop": False,
        }
        controller.set_raw_signals(bus_data=bus_data)
        input_data = controller.read_input()
        assert input_data.linear > 0.6
        assert input_data.angular < -0.3
        assert input_data.deadman_pressed is True

    def test_raw_signals_with_qlogic_profiles(self):
        """Test Q-Logic drive profiles."""
        controller = EmulatedController(controller_family=ControllerFamily.QLOGIC)

        # Profile 1 (slow)
        bus_data = {"linear_axis": 1.0, "angular_axis": 0.0, "drive_profile": 1}
        controller.set_raw_signals(bus_data=bus_data)
        input_data = controller.read_input()
        slow_speed = input_data.linear

        # Profile 3 (fast)
        bus_data["drive_profile"] = 3
        controller.set_raw_signals(bus_data=bus_data)
        input_data = controller.read_input()
        fast_speed = input_data.linear

        assert fast_speed > slow_speed

    def test_get_signal_characteristics(self):
        """Test getting controller family characteristics."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)
        chars = controller.get_signal_characteristics()
        assert chars is not None
        assert chars["family"] == "PG Drives R-Net"
        assert chars["connector"] == "DB9"

    def test_get_signal_characteristics_no_family(self):
        """Test getting characteristics when no family is set."""
        controller = EmulatedController()
        chars = controller.get_signal_characteristics()
        assert chars is None

    def test_emergency_stop_with_family(self):
        """Test emergency stop signal with controller family."""
        controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)
        controller.set_raw_signals(emergency_stop=True)
        input_data = controller.read_input()
        assert input_data.emergency_stop is True

    def test_deadman_switch_with_family(self):
        """Test deadman switch with controller family."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)
        controller.set_raw_signals(enable_line=True)
        input_data = controller.read_input()
        assert input_data.deadman_pressed is True

    def test_mode_button_with_family(self):
        """Test mode button with controller family."""
        controller = EmulatedController(controller_family=ControllerFamily.SHARK_DX)
        controller.set_raw_signals(mode_button=True)
        input_data = controller.read_input()
        assert input_data.mode_switch is True

    def test_script_overrides_family_signals(self):
        """Test that script playback works even with family set."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)

        # Set some raw signals
        controller.set_raw_signals(axis_y_voltage=5.0)

        # Load script - should override signals
        script = [
            ControllerInput(linear=0.3, angular=0.0),
            ControllerInput(linear=0.0, angular=0.5),
        ]
        controller.load_script(script)

        # Script should take precedence
        assert controller.read_input().linear == 0.3
        assert controller.read_input().angular == 0.5

    def test_legacy_set_input_clears_family_signals(self):
        """Test that legacy set_input works with family controllers."""
        controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)

        # Set raw signals first
        controller.set_raw_signals(axis_y_voltage=5.0)

        # Use legacy set_input - should work
        controller.set_input(linear=0.7, angular=-0.2)
        input_data = controller.read_input()
        # The exact value depends on family processing
        assert abs(input_data.linear - 0.7) < 0.1 or input_data.linear > 0.6

    def test_neutral_signals_all_families(self):
        """Test neutral signals produce zero output for all families."""
        families = [
            ControllerFamily.RNET,
            ControllerFamily.SHARK_DX,
            ControllerFamily.VR2_PILOT,
            ControllerFamily.LINX_DX,
            ControllerFamily.QLOGIC,
            ControllerFamily.GENERIC,
        ]

        for family in families:
            controller = EmulatedController(controller_family=family)

            # Set neutral signals based on controller type
            if family in [
                ControllerFamily.RNET,
                ControllerFamily.VR2_PILOT,
                ControllerFamily.GENERIC,
            ]:
                # 5V systems, center at 2.5V
                controller.set_raw_signals(axis_x_voltage=2.5, axis_y_voltage=2.5)
            elif family == ControllerFamily.SHARK_DX:
                # 3.3V system, center at 1.65V
                controller.set_raw_signals(axis_x_voltage=1.65, axis_y_voltage=1.65)
            else:
                # Digital controllers
                controller.set_raw_signals(
                    bus_data={"linear_axis": 0.0, "angular_axis": 0.0}
                )

            input_data = controller.read_input()
            assert (
                input_data.linear == 0.0
            ), f"{family.value} failed neutral linear test"
            assert (
                input_data.angular == 0.0
            ), f"{family.value} failed neutral angular test"

    def test_disconnect_with_family(self):
        """Test disconnect works with controller family."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)
        controller.disconnect()
        assert not controller.is_connected()

    def test_reconnect_with_family(self):
        """Test reconnect works with controller family."""
        controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)
        controller.disconnect()
        controller.connect()
        assert controller.is_connected()

    def test_switching_families(self):
        """Test switching between controller families."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)
        assert controller.get_controller_family() == ControllerFamily.RNET

        # Switch to VR2
        controller.set_controller_family(ControllerFamily.VR2_PILOT)
        assert controller.get_controller_family() == ControllerFamily.VR2_PILOT

        # Switch to LiNX
        controller.set_controller_family(ControllerFamily.LINX_DX)
        assert controller.get_controller_family() == ControllerFamily.LINX_DX

    def test_raw_signals_clear_script(self):
        """Test that setting raw signals clears any active script."""
        controller = EmulatedController(controller_family=ControllerFamily.RNET)

        script = [ControllerInput(linear=0.5, angular=0.0)]
        controller.load_script(script)

        # Set raw signals - should clear script
        controller.set_raw_signals(axis_y_voltage=3.0)

        # Next read should use signals, not script
        input_data = controller.read_input()
        # Won't be exactly 0.5 due to family processing
        assert input_data.linear != 0.5


class TestControllerFamilyRealism:
    """Test realistic behavior of different controller families."""

    def test_rnet_deadzone_is_larger(self):
        """Test R-Net has larger deadzone than VR2."""
        rnet = EmulatedController(controller_family=ControllerFamily.RNET)
        vr2 = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)

        # Small deflection that should be in R-Net deadzone but not VR2
        small_voltage = 2.6  # 0.1V from center (4% of full scale)

        rnet.set_raw_signals(axis_y_voltage=small_voltage)
        vr2.set_raw_signals(axis_y_voltage=small_voltage)

        rnet_input = rnet.read_input()
        vr2_input = vr2.read_input()

        # R-Net has 15% deadzone, so this should be zero
        assert rnet_input.linear == 0.0
        # VR2 has 10% deadzone, so this should also be zero
        # Let's test with larger deflection
        larger_voltage = 2.8  # 0.3V from center (12% of full scale)

        rnet.set_raw_signals(axis_y_voltage=larger_voltage)
        vr2.set_raw_signals(axis_y_voltage=larger_voltage)

        rnet_input = rnet.read_input()
        vr2_input = vr2.read_input()

        # R-Net (15% deadzone) should still be zero
        assert rnet_input.linear == 0.0
        # VR2 (10% deadzone) should have some output
        assert vr2_input.linear > 0.0

    def test_shark_dx_uses_different_voltage(self):
        """Test Shark/DX uses 3.3V system vs 5V for others."""
        shark = EmulatedController(controller_family=ControllerFamily.SHARK_DX)
        rnet = EmulatedController(controller_family=ControllerFamily.RNET)

        # Full forward for Shark (3.3V)
        shark.set_raw_signals(axis_y_voltage=3.3)
        shark_input = shark.read_input()

        # Full forward for R-Net (5V)
        rnet.set_raw_signals(axis_y_voltage=5.0)
        rnet_input = rnet.read_input()

        # Both should produce high linear output
        assert shark_input.linear > 0.7
        assert rnet_input.linear > 0.7

    def test_digital_controllers_have_smaller_deadzone(self):
        """Test digital controllers have smaller deadzones than analog."""
        linx = EmulatedController(controller_family=ControllerFamily.LINX_DX)
        qlogic = EmulatedController(controller_family=ControllerFamily.QLOGIC)
        rnet = EmulatedController(controller_family=ControllerFamily.RNET)

        # Small input (10% of full scale)
        small_input = 0.10

        # Digital controllers
        linx.set_raw_signals(bus_data={"linear_axis": small_input, "angular_axis": 0.0})
        qlogic.set_raw_signals(
            bus_data={"linear_axis": small_input, "angular_axis": 0.0, "drive_profile": 3}
        )

        # Analog controller
        rnet.set_raw_signals(axis_y_voltage=2.5 + (2.5 * small_input))

        linx_input = linx.read_input()
        qlogic_input = qlogic.read_input()
        rnet_input = rnet.read_input()

        # Digital (8% deadzone) should have output
        assert linx_input.linear > 0.0
        assert qlogic_input.linear > 0.0

        # R-Net (15% deadzone) should be zero
        assert rnet_input.linear == 0.0

    def test_vr2_speed_pot_affects_all_movement(self):
        """Test VR2 speed potentiometer affects both linear and angular."""
        controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)

        # Forward and right turn at 50% speed
        controller.set_raw_signals(
            axis_x_voltage=5.0, axis_y_voltage=5.0, speed_pot_voltage=2.5
        )
        input_data = controller.read_input()

        # Both should be scaled down by speed pot
        assert 0.3 < input_data.linear < 0.7
        assert 0.3 < input_data.angular < 0.7
