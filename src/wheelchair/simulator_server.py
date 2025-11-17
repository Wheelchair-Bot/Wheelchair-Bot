"""WebSocket server for broadcasting wheelchair emulator state to the simulator GUI."""

import asyncio
import json
import logging
from typing import Set, Optional
import websockets
from wheelchair.interfaces import WheelchairState

logger = logging.getLogger(__name__)


class SimulatorServer:
    """WebSocket server for the wheelchair simulator GUI."""

    def __init__(self, host: str = "localhost", port: int = 8765):
        """
        Initialize the simulator server.

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.clients: Set = set()
        self.server = None
        self._running = False

    async def register(self, websocket):
        """Register a new client connection."""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")

    async def unregister(self, websocket):
        """Unregister a client connection."""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle a client connection."""
        await self.register(websocket)
        try:
            async for message in websocket:
                # Handle incoming messages if needed (e.g., control commands)
                logger.debug(f"Received message: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def broadcast_state(self, state: WheelchairState):
        """
        Broadcast wheelchair state to all connected clients.

        Args:
            state: Current wheelchair state
        """
        if not self.clients:
            return

        state_data = {
            "x": state.x,
            "y": state.y,
            "theta": state.theta,
            "linear_velocity": state.linear_velocity,
            "angular_velocity": state.angular_velocity,
            "left_motor_speed": state.left_motor_speed,
            "right_motor_speed": state.right_motor_speed,
            "battery_voltage": state.battery_voltage,
            "battery_percent": state.battery_percent,
            "emergency_stop": state.emergency_stop,
            "deadman_active": state.deadman_active,
        }

        message = json.dumps(state_data)
        
        # Send to all clients, removing any that have disconnected
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)

        # Remove disconnected clients
        for client in disconnected:
            self.clients.discard(client)

    async def start(self):
        """Start the WebSocket server."""
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        self._running = True
        logger.info(f"Simulator server started on ws://{self.host}:{self.port}")

    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self._running = False
            logger.info("Simulator server stopped")

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running


class SimulatorBroadcaster:
    """Helper class to integrate simulator broadcasting with the emulator loop."""

    def __init__(self, server: SimulatorServer, update_rate: float = 30.0):
        """
        Initialize the broadcaster.

        Args:
            server: SimulatorServer instance
            update_rate: How many times per second to broadcast state
        """
        self.server = server
        self.update_interval = 1.0 / update_rate
        self._last_broadcast = 0.0
        self._sim_time = 0.0

    def update(self, state: WheelchairState, dt: float):
        """
        Update method to be called from simulation loop callback.

        Args:
            state: Current wheelchair state
            dt: Time delta since last update
        """
        self._sim_time += dt

        # Broadcast at the specified rate
        if self._sim_time - self._last_broadcast >= self.update_interval:
            asyncio.create_task(self.server.broadcast_state(state))
            self._last_broadcast = self._sim_time


def create_simulator_callback(server: SimulatorServer, update_rate: float = 30.0):
    """
    Create a callback function for the simulation loop.

    Args:
        server: SimulatorServer instance
        update_rate: How many times per second to broadcast state

    Returns:
        Callback function compatible with SimulationLoop.add_callback
    """
    broadcaster = SimulatorBroadcaster(server, update_rate)

    def callback(state: WheelchairState, dt: float):
        broadcaster.update(state, dt)

    return callback
