"""Command-line interface for wheelchair emulator."""

import argparse
import sys
from pathlib import Path
from wheelchair.config import EmulatorConfig
from wheelchair.factory import create_emulator
from wheelchair.realistic_factory import (
    create_realistic_emulator,
    create_model_emulator,
    create_degraded_emulator,
    WHEELCHAIR_MODELS
)


def print_state(state, dt):
    """Print current wheelchair state."""
    print(
        f"\r[{state.battery_percent:5.1f}%] "
        f"Pos: ({state.x:6.2f}, {state.y:6.2f}) "
        f"θ: {state.theta:5.2f} "
        f"v: {state.linear_velocity:5.2f} m/s "
        f"ω: {state.angular_velocity:5.2f} rad/s "
        f"Motors: L={state.left_motor_speed:5.2f} R={state.right_motor_speed:5.2f}",
        end="",
        flush=True,
    )


def run_emulator(config_path: str = None, duration: float = None, interactive: bool = False,
                realistic: bool = True, scenario: str = "default", model: str = "standard",
                wear_factor: float = 1.0, battery_health: float = 1.0):
    """
    Run the wheelchair emulator.

    Args:
        config_path: Path to configuration file
        duration: Duration to run (None for infinite)
        interactive: Enable interactive control
        realistic: Use realistic physics emulator
        scenario: Simulation scenario for realistic emulator
        model: Wheelchair model to use
        wear_factor: Motor wear factor (0.0-1.0)
        battery_health: Battery health factor (0.0-1.0)
    """
    # Load configuration
    if config_path:
        config_path = Path(config_path)
        if config_path.suffix in [".yaml", ".yml"]:
            config = EmulatorConfig.from_yaml(str(config_path))
        elif config_path.suffix == ".toml":
            config = EmulatorConfig.from_toml(str(config_path))
        else:
            print(f"Unsupported config format: {config_path.suffix}")
            sys.exit(1)
    else:
        config = EmulatorConfig()

    # Create appropriate emulator
    if realistic:
        if wear_factor < 1.0 or battery_health < 1.0:
            print(f"Creating degraded emulator: wear={wear_factor:.1%}, battery={battery_health:.1%}")
            loop = create_degraded_emulator(wear_factor, battery_health)
        elif model != "standard":
            print(f"Creating {model} model emulator")
            loop = create_model_emulator(model)
        else:
            print(f"Creating realistic emulator with {scenario} scenario")
            loop = create_realistic_emulator(config, scenario)
    else:
        print("Creating basic emulator")
        loop = create_emulator(config)

    # Add state printing callback
    loop.add_callback(print_state)

    # Set up interactive control if requested
    if interactive:
        print("Interactive mode not yet implemented. Running with scripted input.")
        # Could add keyboard input here in future
        # For now, set simple forward motion
        loop.controller.set_input(linear=0.5, deadman_pressed=True)

    print(f"Starting wheelchair emulator (update rate: {config.simulation.update_rate} Hz)")
    print("Press Ctrl+C to stop\n")

    # Run simulation
    loop.run(duration=duration)

    print("\n\nSimulation ended.")
    stats = loop.get_stats()
    print(f"Total steps: {stats['step_count']}")
    print(f"Simulation time: {stats['sim_time']:.2f} seconds")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Enhanced Wheelchair Emulator - Realistic physics and sensor simulation"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to configuration file (YAML or TOML)",
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=float,
        help="Duration to run simulation in seconds",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Enable interactive control (keyboard)",
    )
    parser.add_argument(
        "--basic",
        action="store_true",
        help="Use basic emulator instead of realistic physics",
    )
    parser.add_argument(
        "--scenario",
        choices=["default", "urban", "outdoor", "testing", "extreme"],
        default="default",
        help="Simulation scenario for realistic emulator",
    )
    parser.add_argument(
        "--model",
        choices=list(WHEELCHAIR_MODELS.keys()),
        default="standard", 
        help="Wheelchair model to simulate",
    )
    parser.add_argument(
        "--wear",
        type=float,
        default=1.0,
        help="Motor wear factor (0.0=completely worn, 1.0=new)",
    )
    parser.add_argument(
        "--battery-health",
        type=float,
        default=1.0,
        help="Battery health factor (0.0=dead, 1.0=new)",
    )

    args = parser.parse_args()

    try:
        run_emulator(
            config_path=args.config,
            duration=args.duration,
            interactive=args.interactive,
            realistic=not args.basic,
            scenario=args.scenario,
            model=args.model,
            wear_factor=args.wear,
            battery_health=args.battery_health,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
