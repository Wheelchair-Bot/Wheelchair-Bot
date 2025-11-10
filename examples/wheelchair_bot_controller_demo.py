#!/usr/bin/env python3
"""
Demo showing wheelchair_bot controllers with controller family support.

This example demonstrates how to use the wheelchair_bot controller classes
with realistic controller family emulation.
"""

from wheelchair_bot.controllers import (
    JoystickController,
    GamepadController,
    CONTROLLER_FAMILY_SUPPORT,
)

if CONTROLLER_FAMILY_SUPPORT:
    from wheelchair_bot.controllers import ControllerFamily


def demo_joystick_with_families():
    """Demonstrate joystick controller with different families."""
    if not CONTROLLER_FAMILY_SUPPORT:
        print("Controller family support not available. Install wheelchair package.")
        return
    
    print("\n" + "=" * 70)
    print("Wheelchair-Bot Controllers with Controller Family Support")
    print("=" * 70)
    
    families = [
        (ControllerFamily.RNET, "PG Drives R-Net (Permobil, Quickie)"),
        (ControllerFamily.VR2_PILOT, "VR2/Pilot+ (Pride Jazzy, Golden)"),
        (ControllerFamily.SHARK_DX, "Shark/DX (Merits, Shoprider)"),
        (ControllerFamily.LINX_DX, "LiNX DX (Invacare TDX)"),
        (ControllerFamily.QLOGIC, "Q-Logic 3 (Quantum Edge)"),
    ]
    
    for family, description in families:
        print(f"\n--- {description} ---")
        
        controller = JoystickController(
            joystick_type="analog",
            controller_family=family
        )
        controller.connect()
        
        # Display characteristics
        chars = controller.get_signal_characteristics()
        print(f"  Family: {chars['family']}")
        print(f"  Connector: {chars.get('connector', 'N/A')}")
        print(f"  Protocol: {chars.get('protocol', 'N/A')}")
        print(f"  Deadzone: {chars.get('deadzone', 'N/A')}")
        
        # Test forward movement
        if family in [ControllerFamily.LINX_DX, ControllerFamily.QLOGIC]:
            # Digital controllers use bus data
            print("  (Digital controller - would use bus data in real implementation)")
        else:
            # Analog controllers
            if family == ControllerFamily.SHARK_DX:
                # 3.3V system
                controller.set_raw_signals(
                    axis_x_voltage=1.65,  # Centered
                    axis_y_voltage=3.3,   # Full forward
                    enable_line=True
                )
            else:
                # 5V system
                controller.set_raw_signals(
                    axis_x_voltage=2.5,  # Centered
                    axis_y_voltage=5.0,  # Full forward
                    enable_line=True
                )
            
            linear, angular = controller.read_input()
            print(f"  Full forward: linear={linear:.3f}, angular={angular:.3f}")
        
        controller.disconnect()


def demo_vr2_speed_control():
    """Demonstrate VR2 speed potentiometer feature."""
    if not CONTROLLER_FAMILY_SUPPORT:
        return
    
    print("\n" + "=" * 70)
    print("VR2/Pilot+ Speed Potentiometer Demo")
    print("=" * 70)
    
    controller = JoystickController(
        joystick_type="analog",
        controller_family=ControllerFamily.VR2_PILOT
    )
    controller.connect()
    
    # Test different speed settings
    speed_settings = [
        (5.0, "100%"),
        (3.75, "75%"),
        (2.5, "50%"),
        (1.25, "25%"),
    ]
    
    for speed_voltage, speed_label in speed_settings:
        controller.set_raw_signals(
            axis_y_voltage=5.0,           # Full joystick forward
            speed_pot_voltage=speed_voltage,
            enable_line=True
        )
        linear, angular = controller.read_input()
        print(f"  Speed setting {speed_label}: output={linear:.3f}")
    
    controller.disconnect()


def demo_legacy_mode():
    """Demonstrate backward compatibility without controller family."""
    print("\n" + "=" * 70)
    print("Legacy Mode (Without Controller Family)")
    print("=" * 70)
    
    controller = JoystickController(joystick_type="analog")
    controller.connect()
    
    print(f"  Controller family: {controller.get_controller_family()}")
    print(f"  Default deadzone: {controller._deadzone * 100}%")
    
    # Use legacy set_input method
    controller.set_input(linear=0.8, angular=-0.4)
    linear, angular = controller.read_input()
    print(f"  Input (0.8, -0.4) -> Output ({linear:.3f}, {angular:.3f})")
    
    controller.disconnect()


def demo_comparison():
    """Compare deadzone behavior across families."""
    if not CONTROLLER_FAMILY_SUPPORT:
        return
    
    print("\n" + "=" * 70)
    print("Deadzone Comparison Across Controller Families")
    print("=" * 70)
    
    families = [
        (ControllerFamily.RNET, "R-Net (15%)"),
        (ControllerFamily.VR2_PILOT, "VR2/Pilot+ (10%)"),
        (ControllerFamily.SHARK_DX, "Shark/DX (12%)"),
    ]
    
    print("\n  Small deflection test (12% of full scale):")
    for family, name in families:
        controller = JoystickController(
            joystick_type="analog",
            controller_family=family
        )
        controller.connect()
        
        # Set 12% deflection
        if family == ControllerFamily.SHARK_DX:
            # 3.3V system, 12% = 0.396V above center
            controller.set_raw_signals(axis_y_voltage=1.65 + 0.396, enable_line=True)
        else:
            # 5V system, 12% = 0.6V above center
            controller.set_raw_signals(axis_y_voltage=2.5 + 0.6, enable_line=True)
        
        linear, angular = controller.read_input()
        status = "BLOCKED" if linear == 0.0 else "PASSED"
        print(f"    {name:20} -> {status} (output={linear:.3f})")
        
        controller.disconnect()


def main():
    """Run all demonstrations."""
    demo_joystick_with_families()
    demo_vr2_speed_control()
    demo_comparison()
    demo_legacy_mode()
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
