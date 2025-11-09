"""Tests for controller family implementations."""

import pytest
from wheelchair.controller_families import (
    ControllerFamily,
    ControllerSignals,
    RNetController,
    SharkDXController,
    VR2PilotController,
    LiNXDXController,
    QLogicController,
    GenericController,
    create_controller_family,
)
from wheelchair.interfaces import ControllerInput


class TestControllerFamilyFactory:
    """Test controller family factory function."""

    def test_create_rnet(self):
        """Test creating R-Net controller."""
        controller = create_controller_family(ControllerFamily.RNET)
        assert isinstance(controller, RNetController)
        assert controller.family == ControllerFamily.RNET

    def test_create_shark_dx(self):
        """Test creating Shark/DX controller."""
        controller = create_controller_family(ControllerFamily.SHARK_DX)
        assert isinstance(controller, SharkDXController)
        assert controller.family == ControllerFamily.SHARK_DX

    def test_create_vr2_pilot(self):
        """Test creating VR2/Pilot+ controller."""
        controller = create_controller_family(ControllerFamily.VR2_PILOT)
        assert isinstance(controller, VR2PilotController)
        assert controller.family == ControllerFamily.VR2_PILOT

    def test_create_linx_dx(self):
        """Test creating LiNX DX controller."""
        controller = create_controller_family(ControllerFamily.LINX_DX)
        assert isinstance(controller, LiNXDXController)
        assert controller.family == ControllerFamily.LINX_DX

    def test_create_qlogic(self):
        """Test creating Q-Logic controller."""
        controller = create_controller_family(ControllerFamily.QLOGIC)
        assert isinstance(controller, QLogicController)
        assert controller.family == ControllerFamily.QLOGIC

    def test_create_generic(self):
        """Test creating generic controller."""
        controller = create_controller_family(ControllerFamily.GENERIC)
        assert isinstance(controller, GenericController)
        assert controller.family == ControllerFamily.GENERIC


class TestRNetController:
    """Test PG Drives R-Net controller family."""

    @pytest.fixture
    def controller(self):
        """Create R-Net controller instance."""
        return RNetController()

    def test_initialization(self, controller):
        """Test R-Net controller initializes correctly."""
        assert controller.family == ControllerFamily.RNET
        assert controller.center_voltage == 2.5
        assert controller.max_voltage == 5.0
        assert controller.deadzone == 0.15

    def test_neutral_position(self, controller):
        """Test neutral joystick position."""
        signals = ControllerSignals(axis_x_voltage=2.5, axis_y_voltage=2.5)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_forward_movement(self, controller):
        """Test forward joystick movement."""
        signals = ControllerSignals(axis_x_voltage=2.5, axis_y_voltage=5.0)
        input_data = controller.process_signals(signals)
        assert input_data.linear > 0.5
        assert input_data.angular == 0.0

    def test_backward_movement(self, controller):
        """Test backward joystick movement."""
        signals = ControllerSignals(axis_x_voltage=2.5, axis_y_voltage=0.0)
        input_data = controller.process_signals(signals)
        assert input_data.linear < -0.5
        assert input_data.angular == 0.0

    def test_left_turn(self, controller):
        """Test left turn."""
        signals = ControllerSignals(axis_x_voltage=0.0, axis_y_voltage=2.5)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular < -0.5

    def test_right_turn(self, controller):
        """Test right turn."""
        signals = ControllerSignals(axis_x_voltage=5.0, axis_y_voltage=2.5)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular > 0.5

    def test_deadzone_application(self, controller):
        """Test that small movements within deadzone are ignored."""
        # Small movement within 15% deadzone
        signals = ControllerSignals(axis_x_voltage=2.6, axis_y_voltage=2.6)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_emergency_stop(self, controller):
        """Test emergency stop signal."""
        signals = ControllerSignals(emergency_stop=True)
        input_data = controller.process_signals(signals)
        assert input_data.emergency_stop is True

    def test_deadman_switch(self, controller):
        """Test deadman switch (enable line)."""
        signals = ControllerSignals(enable_line=True)
        input_data = controller.process_signals(signals)
        assert input_data.deadman_pressed is True

    def test_mode_button(self, controller):
        """Test mode button."""
        signals = ControllerSignals(mode_button=True)
        input_data = controller.process_signals(signals)
        assert input_data.mode_switch is True

    def test_signal_characteristics(self, controller):
        """Test getting signal characteristics."""
        chars = controller.get_signal_characteristics()
        assert chars["family"] == "PG Drives R-Net"
        assert chars["connector"] == "DB9"
        assert chars["tier"] == 1
        assert "Permobil" in str(chars["common_models"])


class TestSharkDXController:
    """Test Dynamic Controls Shark/DX controller family."""

    @pytest.fixture
    def controller(self):
        """Create Shark/DX controller instance."""
        return SharkDXController()

    def test_initialization(self, controller):
        """Test Shark/DX controller initializes correctly."""
        assert controller.family == ControllerFamily.SHARK_DX
        assert controller.center_voltage == 1.65
        assert controller.max_voltage == 3.3
        assert controller.deadzone == 0.12

    def test_neutral_position(self, controller):
        """Test neutral joystick position."""
        signals = ControllerSignals(axis_x_voltage=1.65, axis_y_voltage=1.65)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_full_forward(self, controller):
        """Test full forward movement."""
        signals = ControllerSignals(axis_x_voltage=1.65, axis_y_voltage=3.3)
        input_data = controller.process_signals(signals)
        assert input_data.linear > 0.5

    def test_full_backward(self, controller):
        """Test full backward movement."""
        signals = ControllerSignals(axis_x_voltage=1.65, axis_y_voltage=0.0)
        input_data = controller.process_signals(signals)
        assert input_data.linear < -0.5

    def test_deadzone_application(self, controller):
        """Test 12% deadzone."""
        # Small movement within deadzone
        signals = ControllerSignals(axis_x_voltage=1.7, axis_y_voltage=1.7)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_signal_characteristics(self, controller):
        """Test getting signal characteristics."""
        chars = controller.get_signal_characteristics()
        assert chars["family"] == "Dynamic Controls Shark/DX"
        assert chars["connector"] == "4-pin DCI"
        assert chars["voltage_range"] == "0-3.3V"


class TestVR2PilotController:
    """Test PG Drives VR2/Pilot+/VSI controller family."""

    @pytest.fixture
    def controller(self):
        """Create VR2/Pilot+ controller instance."""
        return VR2PilotController()

    def test_initialization(self, controller):
        """Test VR2/Pilot+ controller initializes correctly."""
        assert controller.family == ControllerFamily.VR2_PILOT
        assert controller.center_voltage == 2.5
        assert controller.max_voltage == 5.0
        assert controller.deadzone == 0.10

    def test_neutral_position(self, controller):
        """Test neutral joystick position."""
        signals = ControllerSignals(axis_x_voltage=2.5, axis_y_voltage=2.5)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_speed_potentiometer(self, controller):
        """Test speed potentiometer affects output."""
        # Full forward at 50% speed setting
        signals = ControllerSignals(
            axis_x_voltage=2.5, axis_y_voltage=5.0, speed_pot_voltage=2.5
        )
        input_data = controller.process_signals(signals)
        # Should be scaled by 50%
        assert 0.4 < input_data.linear < 0.6

    def test_full_speed_setting(self, controller):
        """Test full speed setting."""
        signals = ControllerSignals(
            axis_x_voltage=2.5, axis_y_voltage=5.0, speed_pot_voltage=5.0
        )
        input_data = controller.process_signals(signals)
        assert input_data.linear > 0.8

    def test_low_speed_setting(self, controller):
        """Test low speed setting."""
        signals = ControllerSignals(
            axis_x_voltage=2.5, axis_y_voltage=5.0, speed_pot_voltage=1.0
        )
        input_data = controller.process_signals(signals)
        assert input_data.linear < 0.3

    def test_deadzone_smaller_than_rnet(self, controller):
        """Test VR2 has smaller deadzone (10%) than R-Net (15%)."""
        assert controller.deadzone < 0.15

    def test_signal_characteristics(self, controller):
        """Test getting signal characteristics."""
        chars = controller.get_signal_characteristics()
        assert chars["family"] == "PG Drives VR2/Pilot+/VSI"
        assert "Speed potentiometer" in chars["features"]
        assert "Pride Jazzy" in str(chars["common_models"])


class TestLiNXDXController:
    """Test Dynamic Controls LiNX DX Bus controller family."""

    @pytest.fixture
    def controller(self):
        """Create LiNX DX controller instance."""
        return LiNXDXController()

    def test_initialization(self, controller):
        """Test LiNX DX controller initializes correctly."""
        assert controller.family == ControllerFamily.LINX_DX
        assert controller.deadzone == 0.08

    def test_no_bus_data(self, controller):
        """Test handling when no bus data is present."""
        signals = ControllerSignals(bus_data=None)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_bus_data_processing(self, controller):
        """Test processing digital bus data."""
        signals = ControllerSignals(
            bus_data={
                "linear_axis": 0.8,
                "angular_axis": -0.5,
                "emergency_stop": False,
                "enable": True,
                "mode_button": False,
            }
        )
        input_data = controller.process_signals(signals)
        assert input_data.linear > 0.6
        assert input_data.angular < -0.3
        assert input_data.deadman_pressed is True

    def test_emergency_stop_via_bus(self, controller):
        """Test emergency stop via bus data."""
        signals = ControllerSignals(
            bus_data={"linear_axis": 0.5, "angular_axis": 0.0, "emergency_stop": True}
        )
        input_data = controller.process_signals(signals)
        assert input_data.emergency_stop is True

    def test_deadzone_application(self, controller):
        """Test digital controller has smaller deadzone (8%)."""
        signals = ControllerSignals(bus_data={"linear_axis": 0.05, "angular_axis": 0.0})
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0  # Within deadzone

    def test_signal_characteristics(self, controller):
        """Test getting signal characteristics."""
        chars = controller.get_signal_characteristics()
        assert chars["family"] == "Dynamic Controls LiNX"
        assert chars["protocol"] == "Digital CAN-like (proprietary)"
        assert "Telemetry support" in chars["features"]
        assert "Invacare" in str(chars["common_models"])


class TestQLogicController:
    """Test Q-Logic 3/NE Series controller family."""

    @pytest.fixture
    def controller(self):
        """Create Q-Logic controller instance."""
        return QLogicController()

    def test_initialization(self, controller):
        """Test Q-Logic controller initializes correctly."""
        assert controller.family == ControllerFamily.QLOGIC
        assert controller.deadzone == 0.08

    def test_no_bus_data(self, controller):
        """Test handling when no bus data is present."""
        signals = ControllerSignals(bus_data=None)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_drive_profile_scaling(self, controller):
        """Test drive profile affects speed scaling."""
        # Profile 0 (slowest)
        signals = ControllerSignals(
            bus_data={"linear_axis": 1.0, "angular_axis": 0.0, "drive_profile": 0}
        )
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0  # Profile 0 scales to 0

        # Profile 1
        signals.bus_data["drive_profile"] = 1
        input_data = controller.process_signals(signals)
        assert 0.2 < input_data.linear < 0.5

        # Profile 3 (fastest)
        signals.bus_data["drive_profile"] = 3
        input_data = controller.process_signals(signals)
        assert input_data.linear > 0.9

    def test_bus_data_processing(self, controller):
        """Test processing Q-Logic bus data."""
        signals = ControllerSignals(
            bus_data={
                "linear_axis": 0.7,
                "angular_axis": 0.3,
                "drive_profile": 2,
                "enable": True,
            }
        )
        input_data = controller.process_signals(signals)
        # Profile 2 scales to 2/3
        assert 0.3 < input_data.linear < 0.6
        assert input_data.deadman_pressed is True

    def test_signal_characteristics(self, controller):
        """Test getting signal characteristics."""
        chars = controller.get_signal_characteristics()
        assert chars["family"] == "Quantum Q-Logic 3/NE Series"
        assert chars["protocol"] == "CAN/RS485 hybrid"
        assert "Drive profiles" in chars["features"]
        assert "Quantum Edge" in str(chars["common_models"])


class TestGenericController:
    """Test generic controller fallback."""

    @pytest.fixture
    def controller(self):
        """Create generic controller instance."""
        return GenericController()

    def test_initialization(self, controller):
        """Test generic controller initializes correctly."""
        assert controller.family == ControllerFamily.GENERIC
        assert controller.deadzone == 0.10

    def test_neutral_position(self, controller):
        """Test neutral joystick position."""
        signals = ControllerSignals(axis_x_voltage=2.5, axis_y_voltage=2.5)
        input_data = controller.process_signals(signals)
        assert input_data.linear == 0.0
        assert input_data.angular == 0.0

    def test_forward_movement(self, controller):
        """Test forward movement."""
        signals = ControllerSignals(axis_x_voltage=2.5, axis_y_voltage=5.0)
        input_data = controller.process_signals(signals)
        assert input_data.linear > 0.5

    def test_signal_characteristics(self, controller):
        """Test getting signal characteristics."""
        chars = controller.get_signal_characteristics()
        assert chars["family"] == "Generic Analog"
        assert chars["tier"] == "Fallback"


class TestControllerSignals:
    """Test ControllerSignals dataclass."""

    def test_default_values(self):
        """Test default signal values."""
        signals = ControllerSignals()
        assert signals.axis_x_voltage == 2.5
        assert signals.axis_y_voltage == 2.5
        assert signals.enable_line is False
        assert signals.emergency_stop is False
        assert signals.speed_pot_voltage == 5.0

    def test_custom_values(self):
        """Test setting custom signal values."""
        signals = ControllerSignals(
            axis_x_voltage=3.0,
            axis_y_voltage=4.0,
            enable_line=True,
            emergency_stop=True,
            speed_pot_voltage=2.5,
        )
        assert signals.axis_x_voltage == 3.0
        assert signals.axis_y_voltage == 4.0
        assert signals.enable_line is True
        assert signals.emergency_stop is True
        assert signals.speed_pot_voltage == 2.5

    def test_bus_data(self):
        """Test bus data for digital controllers."""
        bus_data = {"linear_axis": 0.5, "angular_axis": -0.3, "enable": True}
        signals = ControllerSignals(bus_data=bus_data)
        assert signals.bus_data == bus_data


class TestControllerFamilyIntegration:
    """Integration tests for controller families."""

    def test_all_families_have_characteristics(self):
        """Test all controller families return characteristics."""
        for family in ControllerFamily:
            controller = create_controller_family(family)
            chars = controller.get_signal_characteristics()
            assert chars is not None
            assert "family" in chars
            assert "tier" in chars or chars.get("tier") == "Fallback"

    def test_all_families_process_neutral(self):
        """Test all families handle neutral position correctly."""
        for family in ControllerFamily:
            controller = create_controller_family(family)

            # For analog controllers
            if family in [
                ControllerFamily.RNET,
                ControllerFamily.SHARK_DX,
                ControllerFamily.VR2_PILOT,
                ControllerFamily.GENERIC,
            ]:
                # Use appropriate center voltage
                if family == ControllerFamily.SHARK_DX:
                    signals = ControllerSignals(axis_x_voltage=1.65, axis_y_voltage=1.65)
                else:
                    signals = ControllerSignals(axis_x_voltage=2.5, axis_y_voltage=2.5)
            else:
                # For digital controllers
                signals = ControllerSignals(
                    bus_data={"linear_axis": 0.0, "angular_axis": 0.0}
                )

            input_data = controller.process_signals(signals)
            assert input_data.linear == 0.0
            assert input_data.angular == 0.0

    def test_tier_1_controllers_are_analog(self):
        """Test Tier 1 controllers use analog signals."""
        tier_1 = [
            ControllerFamily.RNET,
            ControllerFamily.SHARK_DX,
            ControllerFamily.VR2_PILOT,
        ]
        for family in tier_1:
            controller = create_controller_family(family)
            chars = controller.get_signal_characteristics()
            assert chars["tier"] == 1
            assert "Analog" in chars["protocol"] or "analog" in chars["protocol"].lower()

    def test_tier_2_controllers_are_digital(self):
        """Test Tier 2 controllers use digital bus protocols."""
        tier_2 = [ControllerFamily.LINX_DX, ControllerFamily.QLOGIC]
        for family in tier_2:
            controller = create_controller_family(family)
            chars = controller.get_signal_characteristics()
            assert chars["tier"] == 2
            assert "Digital" in chars["protocol"] or "CAN" in chars["protocol"]
