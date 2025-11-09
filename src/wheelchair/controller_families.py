"""Controller family definitions for different wheelchair controller types.

This module defines specific controller families used in commercial wheelchairs,
as documented in docs/wheelchair-support.md. Each controller family has different
signal characteristics, protocols, and feature sets.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass

from wheelchair.interfaces import ControllerInput


class ControllerFamily(Enum):
    """Enumeration of supported wheelchair controller families."""

    # Tier 1 - Analog Controllers (Immediate priority)
    RNET = "rnet"  # PG Drives R-Net (DB9 analog proportional)
    SHARK_DX = "shark_dx"  # Dynamic Controls Shark/DX (4-pin DCI)
    VR2_PILOT = "vr2_pilot"  # PG Drives VR2/Pilot+/VSI (4-pin analog)

    # Tier 2 - Digital Bus Controllers (Near-term priority)
    LINX_DX = "linx_dx"  # Dynamic Controls LiNX (DX Bus - digital)
    QLOGIC = "qlogic"  # Q-Logic 3/NE Series (Digital CAN/RS485)

    # Generic fallback
    GENERIC = "generic"  # Generic analog controller


@dataclass
class ControllerSignals:
    """Raw signal data from controller hardware.

    This represents the low-level signals before processing into ControllerInput.
    Different controller families use different signal types and ranges.
    """

    # Analog signals (voltage values, typically 0-5V range)
    axis_x_voltage: float = 2.5  # X-axis voltage (2.5V = center)
    axis_y_voltage: float = 2.5  # Y-axis voltage (2.5V = center)

    # Digital signals (button states)
    enable_line: bool = False  # Enable/deadman switch
    mode_button: bool = False  # Mode selection button
    emergency_stop: bool = False  # Emergency stop button

    # Bus-based digital data (for LiNX, Q-Logic)
    bus_data: Optional[Dict[str, Any]] = None

    # Additional signals for advanced controllers
    speed_pot_voltage: float = 5.0  # Speed potentiometer (5V = max)
    profile_select: int = 0  # Drive profile selector (0-3)


class BaseControllerFamily(ABC):
    """Base class for controller family implementations.

    Each controller family translates raw hardware signals into normalized
    ControllerInput that the emulator can use.
    """

    def __init__(self, family: ControllerFamily):
        """Initialize controller family.

        Args:
            family: The controller family type
        """
        self.family = family
        self._signals = ControllerSignals()

    @abstractmethod
    def process_signals(self, signals: ControllerSignals) -> ControllerInput:
        """Process raw signals into normalized controller input.

        Args:
            signals: Raw hardware signals

        Returns:
            Normalized ControllerInput
        """
        pass

    @abstractmethod
    def get_signal_characteristics(self) -> Dict[str, Any]:
        """Get characteristics of this controller family.

        Returns:
            Dictionary with signal ranges, protocols, features, etc.
        """
        pass

    def set_signals(self, signals: ControllerSignals) -> None:
        """Update current signal values.

        Args:
            signals: New signal values
        """
        self._signals = signals


class RNetController(BaseControllerFamily):
    """PG Drives R-Net controller family (DB9 analog proportional).

    Used in Permobil M3/M5, Quickie Q500/Q300/Q400/Q700 series.
    Tier 1 priority - ~20% market share in premium rehab segment.

    Signal characteristics:
    - DB9 connector with analog X/Y axes
    - 0-5V range, 2.5V center (proportional control)
    - Enable line for deadman switch
    - Mode selection for drive profiles
    """

    def __init__(self):
        """Initialize R-Net controller."""
        super().__init__(ControllerFamily.RNET)
        self.deadzone = 0.15  # 15% deadzone around center
        self.max_voltage = 5.0
        self.center_voltage = 2.5

    def process_signals(self, signals: ControllerSignals) -> ControllerInput:
        """Process R-Net signals into controller input.

        Args:
            signals: Raw R-Net signals

        Returns:
            Normalized ControllerInput
        """
        # Convert voltage to normalized -1.0 to 1.0 range
        linear = self._voltage_to_axis(signals.axis_y_voltage)
        angular = self._voltage_to_axis(signals.axis_x_voltage)

        # Apply deadzone
        linear = self._apply_deadzone(linear)
        angular = self._apply_deadzone(angular)

        return ControllerInput(
            linear=linear,
            angular=angular,
            emergency_stop=signals.emergency_stop,
            deadman_pressed=signals.enable_line,
            mode_switch=signals.mode_button,
        )

    def _voltage_to_axis(self, voltage: float) -> float:
        """Convert voltage to normalized axis value.

        Args:
            voltage: Input voltage (0-5V)

        Returns:
            Normalized axis value (-1.0 to 1.0)
        """
        # Normalize to -1.0 to 1.0 range
        normalized = (voltage - self.center_voltage) / (
            self.max_voltage - self.center_voltage
        )
        return max(-1.0, min(1.0, normalized))

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value.

        Args:
            value: Raw axis value

        Returns:
            Value with deadzone applied
        """
        if abs(value) < self.deadzone:
            return 0.0
        # Scale remaining range
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * scaled

    def get_signal_characteristics(self) -> Dict[str, Any]:
        """Get R-Net signal characteristics."""
        return {
            "family": "PG Drives R-Net",
            "connector": "DB9",
            "protocol": "Analog Proportional",
            "voltage_range": "0-5V",
            "center_voltage": "2.5V",
            "deadzone": f"{self.deadzone * 100}%",
            "tier": 1,
            "common_models": [
                "Permobil M3 Corpus",
                "Permobil M5 Corpus",
                "Quickie Q500 M",
                "Quickie Q300/Q400/Q700",
                "Magic Mobility Extreme X8",
            ],
        }


class SharkDXController(BaseControllerFamily):
    """Dynamic Controls Shark/DX controller family (4-pin DCI).

    Used in Merits Vision, Shoprider 6Runner, budget import chairs.
    Tier 1 priority - ~15% market share in budget/import segment.

    Signal characteristics:
    - 4-pin DCI connector
    - Hall effect or voltage-based joystick
    - Simple analog axes with switch matrix
    - Lower precision than R-Net but reliable
    """

    def __init__(self):
        """Initialize Shark/DX controller."""
        super().__init__(ControllerFamily.SHARK_DX)
        self.deadzone = 0.12  # 12% deadzone
        self.max_voltage = 3.3  # Hall sensors typically 3.3V
        self.center_voltage = 1.65

    def process_signals(self, signals: ControllerSignals) -> ControllerInput:
        """Process Shark/DX signals into controller input.

        Args:
            signals: Raw Shark/DX signals

        Returns:
            Normalized ControllerInput
        """
        # Convert voltage to normalized range
        linear = self._voltage_to_axis(signals.axis_y_voltage)
        angular = self._voltage_to_axis(signals.axis_x_voltage)

        # Apply deadzone
        linear = self._apply_deadzone(linear)
        angular = self._apply_deadzone(angular)

        return ControllerInput(
            linear=linear,
            angular=angular,
            emergency_stop=signals.emergency_stop,
            deadman_pressed=signals.enable_line,
            mode_switch=signals.mode_button,
        )

    def _voltage_to_axis(self, voltage: float) -> float:
        """Convert voltage to normalized axis value."""
        normalized = (voltage - self.center_voltage) / (
            self.max_voltage - self.center_voltage
        )
        return max(-1.0, min(1.0, normalized))

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value."""
        if abs(value) < self.deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * scaled

    def get_signal_characteristics(self) -> Dict[str, Any]:
        """Get Shark/DX signal characteristics."""
        return {
            "family": "Dynamic Controls Shark/DX",
            "connector": "4-pin DCI",
            "protocol": "Analog Hall Effect",
            "voltage_range": "0-3.3V",
            "center_voltage": "1.65V",
            "deadzone": f"{self.deadzone * 100}%",
            "tier": 1,
            "common_models": [
                "Merits Vision Super HD (P327)",
                "Shoprider 6Runner 10",
            ],
        }


class VR2PilotController(BaseControllerFamily):
    """PG Drives VR2/Pilot+/VSI controller family (4-pin analog).

    Used in Pride Jazzy series, Golden Technologies, Hoveround.
    Tier 1 priority - ~30% market share in consumer/mid-range segment.

    Signal characteristics:
    - 4-pin connector with analog axes
    - 0-5V range with center detection
    - Mode switching and speed control
    - Most common controller in US market
    """

    def __init__(self):
        """Initialize VR2/Pilot+ controller."""
        super().__init__(ControllerFamily.VR2_PILOT)
        self.deadzone = 0.10  # 10% deadzone
        self.max_voltage = 5.0
        self.center_voltage = 2.5

    def process_signals(self, signals: ControllerSignals) -> ControllerInput:
        """Process VR2/Pilot+ signals into controller input.

        Args:
            signals: Raw VR2/Pilot+ signals

        Returns:
            Normalized ControllerInput
        """
        # Convert voltage to normalized range
        linear = self._voltage_to_axis(signals.axis_y_voltage)
        angular = self._voltage_to_axis(signals.axis_x_voltage)

        # Apply deadzone
        linear = self._apply_deadzone(linear)
        angular = self._apply_deadzone(angular)

        # Apply speed scaling from speed potentiometer
        speed_scale = signals.speed_pot_voltage / 5.0
        linear *= speed_scale
        angular *= speed_scale

        return ControllerInput(
            linear=linear,
            angular=angular,
            emergency_stop=signals.emergency_stop,
            deadman_pressed=signals.enable_line,
            mode_switch=signals.mode_button,
        )

    def _voltage_to_axis(self, voltage: float) -> float:
        """Convert voltage to normalized axis value."""
        normalized = (voltage - self.center_voltage) / (
            self.max_voltage - self.center_voltage
        )
        return max(-1.0, min(1.0, normalized))

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value."""
        if abs(value) < self.deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * scaled

    def get_signal_characteristics(self) -> Dict[str, Any]:
        """Get VR2/Pilot+ signal characteristics."""
        return {
            "family": "PG Drives VR2/Pilot+/VSI",
            "connector": "4-pin analog",
            "protocol": "Analog Proportional",
            "voltage_range": "0-5V",
            "center_voltage": "2.5V",
            "deadzone": f"{self.deadzone * 100}%",
            "features": ["Speed potentiometer", "Mode switching"],
            "tier": 1,
            "common_models": [
                "Pride Jazzy Carbon",
                "Pride Jazzy Ultra Light",
                "Pride Jazzy Select 6",
                "Pride Jazzy 600 ES",
                "Golden LiteRider Envy GP162",
                "Golden Compass Sport",
                "Hoveround LX-5",
            ],
        }


class LiNXDXController(BaseControllerFamily):
    """Dynamic Controls LiNX DX Bus controller family (digital).

    Used in Invacare TDX SP2, Aviva RX, Golden LiteRider variants, Drive Titan AXS.
    Tier 2 priority - ~15% market share in mid-range rehab segment.

    Signal characteristics:
    - 4-pin micro connector with digital bus
    - CAN-like protocol (proprietary)
    - Supports telemetry and configuration
    - Requires bus protocol decoding
    """

    def __init__(self):
        """Initialize LiNX DX controller."""
        super().__init__(ControllerFamily.LINX_DX)
        self.deadzone = 0.08  # 8% deadzone (digital has less noise)

    def process_signals(self, signals: ControllerSignals) -> ControllerInput:
        """Process LiNX DX bus signals into controller input.

        Args:
            signals: Raw LiNX DX signals (from bus data)

        Returns:
            Normalized ControllerInput
        """
        # Extract data from bus protocol
        if signals.bus_data is None:
            # No bus data, return neutral
            return ControllerInput()

        # Parse bus data (simplified - real implementation would decode CAN frames)
        linear = signals.bus_data.get("linear_axis", 0.0)
        angular = signals.bus_data.get("angular_axis", 0.0)

        # Apply deadzone
        linear = self._apply_deadzone(linear)
        angular = self._apply_deadzone(angular)

        return ControllerInput(
            linear=linear,
            angular=angular,
            emergency_stop=signals.bus_data.get("emergency_stop", False),
            deadman_pressed=signals.bus_data.get("enable", False),
            mode_switch=signals.bus_data.get("mode_button", False),
        )

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value."""
        if abs(value) < self.deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * scaled

    def get_signal_characteristics(self) -> Dict[str, Any]:
        """Get LiNX DX signal characteristics."""
        return {
            "family": "Dynamic Controls LiNX",
            "connector": "4-pin micro DX Bus",
            "protocol": "Digital CAN-like (proprietary)",
            "features": [
                "Telemetry support",
                "Configuration via bus",
                "Error reporting",
                "Battery monitoring",
            ],
            "tier": 2,
            "common_models": [
                "Invacare TDX SP2",
                "Invacare Aviva RX",
                "Golden LiteRider Envy (variants)",
                "Drive Titan AXS",
            ],
        }


class QLogicController(BaseControllerFamily):
    """Q-Logic 3/NE Series controller family (Digital CAN/RS485).

    Used in Quantum Rehab Edge 3, Quantum 4 Front 2.
    Tier 2 priority - ~10% market share in mid/premium rehab segment.

    Signal characteristics:
    - Digital CAN/RS485 hybrid bus
    - Advanced features (specialty controls, seating)
    - Configuration and diagnostics support
    - Requires protocol abstraction layer
    """

    def __init__(self):
        """Initialize Q-Logic controller."""
        super().__init__(ControllerFamily.QLOGIC)
        self.deadzone = 0.08  # 8% deadzone (digital)

    def process_signals(self, signals: ControllerSignals) -> ControllerInput:
        """Process Q-Logic bus signals into controller input.

        Args:
            signals: Raw Q-Logic signals (from bus data)

        Returns:
            Normalized ControllerInput
        """
        # Extract data from bus protocol
        if signals.bus_data is None:
            return ControllerInput()

        # Parse bus data (simplified - real implementation would decode CAN/RS485)
        linear = signals.bus_data.get("linear_axis", 0.0)
        angular = signals.bus_data.get("angular_axis", 0.0)

        # Apply deadzone
        linear = self._apply_deadzone(linear)
        angular = self._apply_deadzone(angular)

        # Q-Logic supports profile-based speed scaling
        profile = signals.bus_data.get("drive_profile", 1)
        profile_scale = min(1.0, profile / 3.0)  # Profiles 0-3, scale to 0-1

        return ControllerInput(
            linear=linear * profile_scale,
            angular=angular * profile_scale,
            emergency_stop=signals.bus_data.get("emergency_stop", False),
            deadman_pressed=signals.bus_data.get("enable", False),
            mode_switch=signals.bus_data.get("mode_button", False),
        )

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value."""
        if abs(value) < self.deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * scaled

    def get_signal_characteristics(self) -> Dict[str, Any]:
        """Get Q-Logic signal characteristics."""
        return {
            "family": "Quantum Q-Logic 3/NE Series",
            "connector": "Digital bus",
            "protocol": "CAN/RS485 hybrid",
            "features": [
                "Drive profiles",
                "Specialty controls",
                "Seating integration",
                "Advanced diagnostics",
                "USB connectivity",
            ],
            "tier": 2,
            "common_models": [
                "Quantum Edge 3",
                "Quantum Edge 3 Stretto",
                "Quantum 4 Front 2",
            ],
        }


class GenericController(BaseControllerFamily):
    """Generic controller for basic analog input.

    Fallback for controllers not matching specific families.
    """

    def __init__(self):
        """Initialize generic controller."""
        super().__init__(ControllerFamily.GENERIC)
        self.deadzone = 0.10

    def process_signals(self, signals: ControllerSignals) -> ControllerInput:
        """Process generic signals into controller input."""
        # Simple linear mapping assuming 0-5V with 2.5V center
        linear = (signals.axis_y_voltage - 2.5) / 2.5
        angular = (signals.axis_x_voltage - 2.5) / 2.5

        # Clamp and apply deadzone
        linear = self._apply_deadzone(max(-1.0, min(1.0, linear)))
        angular = self._apply_deadzone(max(-1.0, min(1.0, angular)))

        return ControllerInput(
            linear=linear,
            angular=angular,
            emergency_stop=signals.emergency_stop,
            deadman_pressed=signals.enable_line,
            mode_switch=signals.mode_button,
        )

    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to axis value."""
        if abs(value) < self.deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self.deadzone) / (1.0 - self.deadzone)
        return sign * scaled

    def get_signal_characteristics(self) -> Dict[str, Any]:
        """Get generic controller characteristics."""
        return {
            "family": "Generic Analog",
            "connector": "Various",
            "protocol": "Generic Analog",
            "voltage_range": "0-5V",
            "deadzone": f"{self.deadzone * 100}%",
            "tier": "Fallback",
        }


def create_controller_family(family: ControllerFamily) -> BaseControllerFamily:
    """Factory function to create a controller family instance.

    Args:
        family: The controller family to create

    Returns:
        Instance of the appropriate controller family class

    Raises:
        ValueError: If controller family is not supported
    """
    family_map = {
        ControllerFamily.RNET: RNetController,
        ControllerFamily.SHARK_DX: SharkDXController,
        ControllerFamily.VR2_PILOT: VR2PilotController,
        ControllerFamily.LINX_DX: LiNXDXController,
        ControllerFamily.QLOGIC: QLogicController,
        ControllerFamily.GENERIC: GenericController,
    }

    if family not in family_map:
        raise ValueError(f"Unsupported controller family: {family}")

    return family_map[family]()
