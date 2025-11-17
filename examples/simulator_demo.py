#!/usr/bin/env python3
"""
Wheelchair Emulator with 3D Simulator GUI Demo

This script runs the wheelchair emulator and broadcasts its state to a WebSocket
server for visualization in the Three.js based simulator GUI.

Usage:
    python examples/simulator_demo.py

Then open simulator.html in a web browser to view the 3D visualization.
"""

import asyncio
import time
import argparse
import logging
import webbrowser
from pathlib import Path

from wheelchair.config import EmulatorConfig
from wheelchair.realistic_factory import create_realistic_emulator
from wheelchair.simulator_server import SimulatorServer, create_simulator_callback
from wheelchair.interfaces import ControllerInput


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulatorDemo:
    """Demo of wheelchair emulator with 3D simulator GUI."""

    def __init__(self, scenario: str = "default", auto_open_browser: bool = True, server: SimulatorServer = None):
        """
        Initialize the demo.

        Args:
            scenario: Simulation scenario to use
            auto_open_browser: Whether to automatically open the browser
            server: Optional SimulatorServer instance. If not provided, creates a default one.
        """
        self.scenario = scenario
        self.auto_open_browser = auto_open_browser
        
        # Create emulator
        config = EmulatorConfig()
        self.loop = create_realistic_emulator(config, scenario)
        
        # Use provided server or create default one
        self.server = server if server is not None else SimulatorServer(host="localhost", port=8765)
        
        # Add broadcasting callback
        callback = create_simulator_callback(self.server, update_rate=30.0)
        self.loop.add_callback(callback)

    async def run_demo(self, duration: float = None):
        """
        Run the demonstration.

        Args:
            duration: How long to run (None for infinite)
        """
        # Start WebSocket server
        await self.server.start()
        
        # Open browser if requested
        if self.auto_open_browser:
            simulator_path = Path(__file__).parent.parent / "simulator.html"
            if simulator_path.exists():
                logger.info(f"Opening simulator GUI: {simulator_path}")
                webbrowser.open(f"file://{simulator_path.absolute()}")
            else:
                logger.warning(f"Simulator HTML not found at {simulator_path}")
                logger.info("Please manually open simulator.html in your browser")

        logger.info("Simulator server running on ws://localhost:8765")
        logger.info("Running emulator demo with movement pattern...")

        # Run simulation with a demo movement pattern
        start_time = time.time()
        
        try:
            # Create an async task for the simulation loop
            async def run_simulation():
                phase_time = 0.0
                dt = 1.0 / self.loop.config.simulation.update_rate

                while duration is None or (time.time() - start_time) < duration:
                    # Demo movement pattern
                    cycle_time = 20.0  # 20 second cycle
                    t = phase_time % cycle_time

                    if t < 5.0:
                        # Forward movement
                        self.loop.controller.set_input(linear=0.6, deadman_pressed=True)
                    elif t < 10.0:
                        # Turn right while moving
                        self.loop.controller.set_input(
                            linear=0.4, angular=0.5, deadman_pressed=True
                        )
                    elif t < 15.0:
                        # Backward movement
                        self.loop.controller.set_input(linear=-0.4, deadman_pressed=True)
                    else:
                        # Turn left while moving
                        self.loop.controller.set_input(
                            linear=0.4, angular=-0.5, deadman_pressed=True
                        )

                    # Step simulation
                    self.loop.step()
                    
                    # Small delay to maintain real-time simulation
                    await asyncio.sleep(dt)
                    
                    phase_time += dt

            # Run simulation
            await run_simulation()

        except KeyboardInterrupt:
            logger.info("\nDemo stopped by user")
        finally:
            await self.server.stop()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Wheelchair Emulator with 3D Simulator GUI Demo"
    )
    parser.add_argument(
        "--scenario",
        default="default",
        choices=["default", "urban", "outdoor", "testing", "extreme"],
        help="Simulation scenario",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Demo duration in seconds (default: run indefinitely)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="WebSocket server host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="WebSocket server port (default: 8765)",
    )

    args = parser.parse_args()

    # Create the SimulatorServer with the correct host and port
    server = SimulatorServer(host=args.host, port=args.port)

    demo = SimulatorDemo(
        scenario=args.scenario,
        auto_open_browser=not args.no_browser,
        server=server
    )
    print("\n" + "=" * 60)
    print("🦽 Wheelchair Emulator with 3D Simulator GUI")
    print("=" * 60)
    print(f"Scenario: {args.scenario}")
    print(f"WebSocket Server: ws://{args.host}:{args.port}")
    print("\nInstructions:")
    print("1. The simulator will open in your browser automatically")
    print("2. If not, open simulator.html manually")
    print("3. Click 'Connect to Emulator' in the GUI")
    print("4. Watch the wheelchair move in 3D!")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 60 + "\n")

    await demo.run_demo(duration=args.duration)


if __name__ == "__main__":
    asyncio.run(main())
