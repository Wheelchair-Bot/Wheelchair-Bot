#!/usr/bin/env python3
"""
Demo script showing controller family emulation.

This example demonstrates how to use different wheelchair controller families
in the emulator to test with realistic signal characteristics.
"""

from wheelchair.emulator.controller import EmulatedController
from wheelchair.controller_families import ControllerFamily


def demo_rnet_controller():
    """Demonstrate PG Drives R-Net controller (Permobil, Quickie)."""
    print("\n=== R-Net Controller Demo (Permobil M3/M5, Quickie Q500) ===")
    controller = EmulatedController(controller_family=ControllerFamily.RNET)

    # Display characteristics
    chars = controller.get_signal_characteristics()
    print(f"Family: {chars['family']}")
    print(f"Connector: {chars['connector']}")
    print(f"Voltage Range: {chars['voltage_range']}")
    print(f"Deadzone: {chars['deadzone']}")

    # Test neutral position (2.5V center)
    controller.set_raw_signals(axis_x_voltage=2.5, axis_y_voltage=2.5)
    input_data = controller.read_input()
    print(f"Neutral: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}")

    # Test forward movement (5V = full forward)
    controller.set_raw_signals(
        axis_x_voltage=2.5, axis_y_voltage=5.0, enable_line=True
    )
    input_data = controller.read_input()
    print(
        f"Full Forward: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )

    # Test small movement in deadzone (15% deadzone should filter this)
    controller.set_raw_signals(axis_x_voltage=2.5, axis_y_voltage=2.7)
    input_data = controller.read_input()
    print(
        f"Small Movement (in deadzone): linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )


def demo_vr2_controller():
    """Demonstrate PG Drives VR2/Pilot+ controller (Pride Jazzy series)."""
    print("\n=== VR2/Pilot+ Controller Demo (Pride Jazzy, Golden) ===")
    controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)

    chars = controller.get_signal_characteristics()
    print(f"Family: {chars['family']}")
    print(f"Features: {', '.join(chars['features'])}")

    # Test forward at 100% speed setting
    controller.set_raw_signals(
        axis_y_voltage=5.0, speed_pot_voltage=5.0, enable_line=True
    )
    input_data = controller.read_input()
    print(
        f"Forward at 100% speed: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )

    # Test forward at 50% speed setting (speed potentiometer)
    controller.set_raw_signals(
        axis_y_voltage=5.0, speed_pot_voltage=2.5, enable_line=True
    )
    input_data = controller.read_input()
    print(
        f"Forward at 50% speed: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )

    # Test forward at 25% speed setting
    controller.set_raw_signals(
        axis_y_voltage=5.0, speed_pot_voltage=1.25, enable_line=True
    )
    input_data = controller.read_input()
    print(
        f"Forward at 25% speed: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )


def demo_shark_controller():
    """Demonstrate Dynamic Controls Shark/DX controller (budget chairs)."""
    print("\n=== Shark/DX Controller Demo (Merits, Shoprider) ===")
    controller = EmulatedController(controller_family=ControllerFamily.SHARK_DX)

    chars = controller.get_signal_characteristics()
    print(f"Family: {chars['family']}")
    print(f"Voltage Range: {chars['voltage_range']}")

    # Shark uses 3.3V system with 1.65V center (Hall effect sensors)
    controller.set_raw_signals(axis_x_voltage=1.65, axis_y_voltage=1.65)
    input_data = controller.read_input()
    print(f"Neutral: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}")

    # Full forward (3.3V)
    controller.set_raw_signals(
        axis_x_voltage=1.65, axis_y_voltage=3.3, enable_line=True
    )
    input_data = controller.read_input()
    print(
        f"Full Forward: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )

    # Right turn
    controller.set_raw_signals(
        axis_x_voltage=3.3, axis_y_voltage=1.65, enable_line=True
    )
    input_data = controller.read_input()
    print(
        f"Right Turn: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )


def demo_linx_controller():
    """Demonstrate Dynamic Controls LiNX DX Bus controller (digital)."""
    print("\n=== LiNX DX Bus Controller Demo (Invacare TDX SP2) ===")
    controller = EmulatedController(controller_family=ControllerFamily.LINX_DX)

    chars = controller.get_signal_characteristics()
    print(f"Family: {chars['family']}")
    print(f"Protocol: {chars['protocol']}")
    print(f"Features: {', '.join(chars['features'])}")

    # Digital controllers use bus data instead of voltage
    controller.set_raw_signals(
        bus_data={
            "linear_axis": 0.0,
            "angular_axis": 0.0,
            "enable": False,
            "emergency_stop": False,
        }
    )
    input_data = controller.read_input()
    print(f"Neutral: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}")

    # Forward movement via bus
    controller.set_raw_signals(
        bus_data={
            "linear_axis": 0.9,
            "angular_axis": 0.0,
            "enable": True,
            "emergency_stop": False,
        }
    )
    input_data = controller.read_input()
    print(
        f"Forward: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )

    # Combined movement (forward + right turn)
    controller.set_raw_signals(
        bus_data={
            "linear_axis": 0.7,
            "angular_axis": 0.5,
            "enable": True,
            "emergency_stop": False,
        }
    )
    input_data = controller.read_input()
    print(
        f"Forward + Right: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
    )


def demo_qlogic_controller():
    """Demonstrate Q-Logic 3 controller with drive profiles."""
    print("\n=== Q-Logic 3 Controller Demo (Quantum Edge 3) ===")
    controller = EmulatedController(controller_family=ControllerFamily.QLOGIC)

    chars = controller.get_signal_characteristics()
    print(f"Family: {chars['family']}")
    print(f"Features: {', '.join(chars['features'])}")

    # Test different drive profiles (0=slowest, 3=fastest)
    for profile in range(4):
        controller.set_raw_signals(
            bus_data={
                "linear_axis": 1.0,
                "angular_axis": 0.0,
                "drive_profile": profile,
                "enable": True,
            }
        )
        input_data = controller.read_input()
        print(
            f"Profile {profile}: linear={input_data.linear:.2f}, angular={input_data.angular:.2f}"
        )


def compare_deadzones():
    """Compare deadzone behavior across controller families."""
    print("\n=== Deadzone Comparison ===")

    families = [
        (ControllerFamily.RNET, "R-Net", 2.5, 2.8),  # 12% deflection
        (ControllerFamily.VR2_PILOT, "VR2/Pilot+", 2.5, 2.8),
        (ControllerFamily.SHARK_DX, "Shark/DX", 1.65, 1.85),
    ]

    for family, name, center, test_voltage in families:
        controller = EmulatedController(controller_family=family)
        controller.set_raw_signals(axis_y_voltage=test_voltage, enable_line=True)
        input_data = controller.read_input()
        chars = controller.get_signal_characteristics()

        print(
            f"{name:15} (Deadzone: {chars['deadzone']:5}): linear={input_data.linear:.3f}"
        )


def main():
    """Run all controller family demos."""
    print("=" * 70)
    print("Wheelchair Controller Family Emulation Demo")
    print("=" * 70)

    demo_rnet_controller()
    demo_vr2_controller()
    demo_shark_controller()
    demo_linx_controller()
    demo_qlogic_controller()
    compare_deadzones()

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
