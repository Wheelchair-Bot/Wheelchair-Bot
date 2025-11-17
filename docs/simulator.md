# Three.js Wheelchair Simulator GUI

A real-time 3D visualization for the wheelchair emulator using Three.js.

## Overview

This simulator provides a web-based 3D visualization of the wheelchair emulator's state, allowing you to see the wheelchair's position, orientation, and movement in real-time.

## Features

- **3D Visualization**: Realistic wheelchair model with animated wheels
- **Real-time Updates**: WebSocket connection for live state updates
- **Path Tracing**: Visual trail showing the wheelchair's path
- **Interactive Camera**: Orbit controls to view from any angle
- **Detailed Telemetry**: Position, velocity, motor speeds, and battery status
- **Customizable View**: Adjustable camera distance and height
- **Responsive Design**: Works on desktop and mobile browsers

## Quick Start

### 1. Start the Emulator with Simulator Server

```bash
cd /home/runner/work/Wheelchair-Bot/Wheelchair-Bot
PYTHONPATH=src python3 examples/simulator_demo.py
```

This will:
- Start the wheelchair emulator
- Launch a WebSocket server on `ws://localhost:8765`
- Automatically open `simulator.html` in your browser

### 2. Manual Browser Setup

If the browser doesn't open automatically:

1. Open `simulator.html` in your web browser
2. The WebSocket URL should be pre-filled as `ws://localhost:8765`
3. Click "Connect to Emulator"
4. Watch the wheelchair move in 3D!

## Usage

### Connecting to the Emulator

1. Ensure the emulator is running with the simulator server
2. Open `simulator.html` in a modern web browser
3. Enter the WebSocket URL (default: `ws://localhost:8765`)
4. Click "Connect to Emulator"

The status indicator will turn green when connected.

### Camera Controls

- **Orbit**: Left mouse button drag
- **Zoom**: Mouse wheel
- **Pan**: Right mouse button drag (or two-finger drag on trackpad)

### View Options

Use the sidebar controls to customize the view:

- **Camera Distance**: Adjust how far the camera is from the wheelchair
- **Camera Height**: Change the viewing elevation
- **Show Path Trace**: Toggle the yellow trail that shows where the wheelchair has been

### Reset Position

Click the "Reset Position" button to:
- Return the wheelchair to origin (0, 0)
- Clear the path trace
- Reset the camera view

## Architecture

### Components

1. **simulator.html**: Web interface with sidebar controls and 3D canvas
2. **simulator.js**: Three.js rendering and WebSocket client
3. **src/wheelchair/simulator_server.py**: WebSocket server for broadcasting state
4. **examples/simulator_demo.py**: Demo script integrating emulator with server

### Data Flow

```
Wheelchair Emulator
    ↓
SimulationLoop callbacks
    ↓
SimulatorServer.broadcast_state()
    ↓ WebSocket (JSON)
WheelchairSimulator (JavaScript)
    ↓
Three.js rendering
```

### State Message Format

The WebSocket server broadcasts JSON messages with the wheelchair state:

```json
{
  "x": 1.23,
  "y": 4.56,
  "theta": 0.785,
  "linear_velocity": 0.5,
  "angular_velocity": 0.1,
  "left_motor_speed": 0.6,
  "right_motor_speed": 0.4,
  "battery_voltage": 24.0,
  "battery_percent": 95.0,
  "emergency_stop": false,
  "deadman_active": true
}
```

## Integration with Existing Emulator

### Adding Simulator to Your Own Script

```python
import asyncio
from wheelchair.config import EmulatorConfig
from wheelchair.factory import create_emulator
from wheelchair.simulator_server import SimulatorServer, create_simulator_callback

async def main():
    # Create emulator
    config = EmulatorConfig()
    loop = create_emulator(config)
    
    # Create and start simulator server
    server = SimulatorServer(host="localhost", port=8765)
    await server.start()
    
    # Add broadcasting callback
    callback = create_simulator_callback(server, update_rate=30.0)
    loop.add_callback(callback)
    
    # Run your simulation
    try:
        loop.run(duration=60.0)
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Update Rate

The `update_rate` parameter controls how many times per second the state is broadcast:

```python
# Broadcast 60 times per second (smoother but more bandwidth)
callback = create_simulator_callback(server, update_rate=60.0)

# Broadcast 10 times per second (less smooth but lower bandwidth)
callback = create_simulator_callback(server, update_rate=10.0)
```

## Browser Compatibility

The simulator requires a modern browser with support for:
- WebGL (for Three.js rendering)
- ES6 Modules
- WebSocket API

Tested browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Troubleshooting

### "Failed to connect to emulator"

- Make sure the emulator is running with the simulator server
- Check that the WebSocket URL is correct
- Verify the port (default: 8765) is not blocked by firewall

### Simulator is choppy/laggy

- Reduce the broadcast update rate in the server
- Close other browser tabs
- Try a different browser
- Check your GPU drivers

### Path trace is too long/cluttered

- Uncheck "Show Path Trace" to disable it
- Click "Reset Position" to clear the trace
- The trace automatically limits to 1000 points

### Browser shows "Loading 3D Simulator..." indefinitely

- Check browser console for errors (F12)
- Ensure you have a stable internet connection (for CDN resources)
- Try refreshing the page

## Customization

### Changing the Wheelchair Model

Edit `simulator.js` and modify the `createWheelchair()` method:

```javascript
createWheelchair() {
    // Modify dimensions, colors, and geometry here
    const bodyGeometry = new THREE.BoxGeometry(1.0, 0.5, 1.2); // Larger body
    const bodyMaterial = new THREE.MeshStandardMaterial({
        color: 0xff0000,  // Red color
        // ...
    });
    // ...
}
```

### Adding Sensors/Obstacles

Extend the state message to include sensor data and modify the visualization:

```python
# In simulator_server.py, add to state_data:
state_data = {
    # ... existing fields ...
    "proximity_front": sensor_data.proximity_front,
    "proximity_left": sensor_data.proximity_left,
    # ...
}
```

```javascript
// In simulator.js, visualize obstacles:
updateState(data) {
    // ... existing code ...
    if (data.proximity_front && data.proximity_front < 2.0) {
        this.showObstacle(data.proximity_front);
    }
}
```

## Performance

- Default broadcast rate: 30 Hz (30 updates/second)
- Path trace limit: 1000 points
- Render loop: 60 FPS (requestAnimationFrame)
- Typical CPU usage: 5-10% (depends on system)
- Network bandwidth: ~5-10 KB/s (JSON state updates)

## Development

### File Structure

```
Wheelchair-Bot/
├── simulator.html              # Main HTML interface
├── simulator.js                # Three.js client code
├── src/wheelchair/
│   └── simulator_server.py    # WebSocket server
└── examples/
    └── simulator_demo.py      # Demo integration script
```

### Adding New Features

1. Extend state data in `simulator_server.py`
2. Update UI elements in `simulator.html`
3. Implement visualization in `simulator.js`

## License

Same as the main Wheelchair-Bot project (MIT License).

## Credits

- Three.js: https://threejs.org/
- WebSocket API: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
