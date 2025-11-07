"""
Example: Showcase all wheelchair models
"""

from wheelchair_bot.wheelchairs.models import (
    PermobilM3Corpus,
    QuantumQ6Edge,
    InvacareTPG,
    PrideJazzy,
)


def main():
    """Display information about all supported wheelchair models."""
    
    wheelchairs = [
        PermobilM3Corpus(),
        QuantumQ6Edge(),
        InvacareTPG(),
        PrideJazzy(),
    ]
    
    print("=" * 70)
    print("SUPPORTED WHEELCHAIR MODELS")
    print("=" * 70)
    
    for wheelchair in wheelchairs:
        info = wheelchair.get_info()
        motor_config = wheelchair.get_motor_config()
        
        print(f"\n{info['name']}")
        print("-" * 70)
        print(f"  Max Speed:      {info['max_speed']:.2f} m/s ({info['max_speed'] * 2.237:.1f} mph)")
        print(f"  Wheel Base:     {info['wheel_base']:.2f} m")
        print(f"  Wheel Diameter: {info['wheel_diameter']:.2f} m")
        print(f"\n  Motor Configuration:")
        print(f"    Drive Type:   {motor_config['type']}")
        print(f"    Motor Type:   {motor_config['motor_type']}")
        print(f"    Motor Count:  {motor_config['motor_count']}")
        print(f"    Max Voltage:  {motor_config['max_voltage']}V")
        print(f"    Max Current:  {motor_config['max_current']}A")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
