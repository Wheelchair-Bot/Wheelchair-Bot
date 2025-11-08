# Wheelchair-Bot - Universal Tele-Robotics Kit

A lightweight, universal tele-robotics kit that turns almost any powered wheelchair into a remotely driven robot using commodity parts, an Android phone and/or a Raspberry Pi, and a camera—all accessed through a secure web interface.

## Overview

Wheelchair-Bot is designed as a modular, service-based system that requires minimal hardware and avoids heavy frameworks like ROS. It provides a complete solution for remote wheelchair control with real-time video streaming, responsive controls, and comprehensive safety features.

## Features

- **Universal Compatibility**: Works with most powered wheelchairs using commodity hardware
- **Lightweight Stack**: No ROS dependency - uses FastAPI, WebSockets, and WebRTC
- **Multiple Platform Support**: Run on Raspberry Pi, Android devices, or standard computers
- **Real-Time Video/Audio**: WebRTC-based streaming with low latency
- **Secure Web Access**: Control from any modern web browser
- **Safety-First Design**: Built-in E-stop, deadman switch, and speed limiting
- **Network Resilient**: Supports both LTE and Wi-Fi connectivity
- **Modular Architecture**: Easy to customize and extend

## System Architecture

The system consists of five core services that work together:

### Services

1. **teleopd** - Teleoperations daemon (Python FastAPI)
   - WebSocket server for real-time control commands
   - REST API for configuration and status
   - Handles motor control interface
   - Service endpoint: `http://localhost:8000`

2. **webrtc** - Video and audio streaming
   - WebRTC peer connection management
   - Real-time video from camera to web client
   - Bidirectional audio support
   - Low-latency streaming

3. **streamer** - Camera capture service
   - Uses libcamera (Raspberry Pi) or GStreamer (general)
   - Configurable resolution and framerate
   - H.264 encoding for efficient streaming
   - Supports USB and CSI cameras

4. **safety-agent** - Safety monitoring service
   - Emergency stop (E-stop) monitoring
   - Deadman switch enforcement
   - Speed and acceleration limiting
   - Watchdog for all critical services

5. **net-agent** - Network management service
   - LTE and Wi-Fi connectivity management
   - Dynamic DNS for remote access
   - VPN/secure tunnel setup
   - Connection quality monitoring

### Control Interface

- **Web Client** - Browser-based control interface
  - Virtual joystick for precise control
  - Real-time video display
  - Status monitoring
  - Works on desktop and mobile
  - No app installation required

## Hardware Requirements

### Minimum Requirements
- **Computing Platform** (choose one or more):
  - Raspberry Pi 4 (2GB+ RAM recommended)
  - Raspberry Pi 3B+
  - Android phone/tablet (for camera and compute)
  - Any Linux-capable computer
  
- **Camera**:
  - Raspberry Pi Camera Module v2/v3 (CSI interface)
  - USB webcam (UVC compatible)
  - Android device camera

- **Wheelchair Interface**:
  - Motor driver board (L298N, L293D, or similar)
  - OR direct interface to wheelchair's control system
  - Power supply appropriate for your motors

- **Network** (choose one):
  - Wi-Fi dongle or built-in Wi-Fi
  - 4G/LTE USB modem or built-in cellular
  - Ethernet connection

### Optional Components
- GPS module for location tracking
- IMU for motion sensing
- Motor encoders for odometry
- Battery monitoring system
- External speakers for audio feedback

## Installation

### Quick Start

For the fastest setup, see [QUICKSTART.md](QUICKSTART.md).

### Detailed Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot
```

#### 2. Install Dependencies

**On Raspberry Pi:**
```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y python3-pip libcamera-apps gstreamer1.0-tools

# Install Python dependencies
pip3 install -r requirements.txt
```

**On other Linux systems:**
```bash
# Install GStreamer
sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins-good

# Install Python dependencies
pip3 install -r requirements.txt
```

**For development:**
```bash
# Install with development tools
pip3 install -e ".[dev]"
```

#### 3. Configure Services

Edit configuration files in the `config/` directory:

- `teleopd.json` - Teleoperations service settings
- `safety.json` - Safety parameters and limits
- `network.json` - Network and security settings
- `camera.json` - Camera and streaming configuration

#### 4. GPIO Pin Configuration (Raspberry Pi)

Default GPIO pin assignments (BCM mode):

| Function | GPIO Pin |
|----------|----------|
| Left Motor Forward | 17 |
| Left Motor Backward | 18 |
| Left Motor Enable (PWM) | 12 |
| Right Motor Forward | 22 |
| Right Motor Backward | 23 |
| Right Motor Enable (PWM) | 13 |
| E-Stop Input | 27 |

Customize pin assignments in `config/default_config.json`.

## Usage

### Starting the System

#### Option 1: Start All Services (Production)

```bash
# Start all services using the main launcher
python3 main.py
```

This starts:
- teleopd (control server)
- webrtc (video/audio streaming)
- streamer (camera capture)
- safety-agent (safety monitoring)
- net-agent (network management)

#### Option 2: Start Individual Services (Development)

```bash
# Terminal 1: Start teleopd
python3 -m wheelchair_bot.services.teleopd

# Terminal 2: Start video streamer
python3 -m wheelchair_bot.services.streamer

# Terminal 3: Start safety agent
python3 -m wheelchair_bot.services.safety_agent

# Terminal 4: Start network agent (if needed)
python3 -m wheelchair_bot.services.net_agent
```

#### Option 3: Mock Mode (Testing without Hardware)

```bash
# Run with mock GPIO and camera
python3 main.py --mock
```

### Web Interface

Once the services are running:

1. Open a web browser on any device
2. Navigate to: `http://<raspberry-pi-ip>:8080` or `http://localhost:8080` (local)
3. The control interface will load automatically
4. Click "Connect" to establish WebRTC connection
5. Use the virtual joystick or keyboard to control the wheelchair

### Keyboard Controls

When using the web interface:

- **W** or **↑** - Move Forward
- **S** or **↓** - Move Backward
- **A** or **←** - Turn Left
- **D** or **→** - Turn Right
- **Space** or **Esc** - Stop (E-Stop)
- **+/-** - Adjust Speed

### Command Line Options

```bash
python3 main.py [OPTIONS]

Options:
  --mock              Use mock GPIO and camera (for testing)
  --config FILE       Configuration file (default: config/default_config.json)
  --max-speed SPEED   Maximum speed percentage (0-100, default: 80)
  --port PORT         Web server port (default: 8080)
  --camera DEVICE     Camera device (default: auto-detect)
  --no-video          Disable video streaming
  --verbose, -v       Enable verbose logging
  --help, -h          Show help message
```

## Project Structure

```
Wheelchair-Bot/
├── wheelchair_bot/              # Main package
│   ├── services/                # Service implementations
│   │   ├── teleopd.py          # Teleoperations daemon
│   │   ├── streamer.py         # Camera streaming service
│   │   ├── safety_agent.py     # Safety monitoring
│   │   └── net_agent.py        # Network management
│   ├── controllers/             # Input controllers
│   │   ├── joystick.py         # Virtual joystick
│   │   └── gamepad.py          # Physical gamepad
│   ├── motors/                  # Motor control
│   │   ├── differential.py     # Differential drive
│   │   └── base.py             # Motor interface
│   ├── safety/                  # Safety features
│   │   ├── deadman.py          # Deadman switch
│   │   └── limiter.py          # Speed/acceleration limits
│   └── wheelchairs/             # Wheelchair models
│       └── models.py            # Wheelchair configurations
├── packages/
│   ├── backend/                 # FastAPI backend (teleopd)
│   ├── frontend/                # React web UI (optional)
│   └── shared/                  # Shared utilities
├── config/                      # Configuration files
│   ├── default_config.json     # Main configuration
│   ├── teleopd.json            # Teleopd settings
│   ├── safety.json             # Safety parameters
│   └── network.json            # Network settings
├── web/                         # Web client (HTML/JS/CSS)
│   ├── index.html              # Main UI
│   ├── webrtc.js               # WebRTC handling
│   ├── controller.js           # Control logic
│   └── styles.css              # Styling
├── docs/                        # Documentation
│   ├── architecture.md         # System architecture
│   ├── api.md                  # API reference
│   └── getting-started.md      # Setup guide
├── tests/                       # Test suite
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

### Service Configuration

Each service can be configured via JSON files in the `config/` directory:

#### teleopd.json
```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "websocket_port": 8080,
  "max_clients": 5,
  "command_timeout": 1.0
}
```

#### safety.json
```json
{
  "max_speed": 0.8,
  "max_angular_speed": 0.8,
  "deadman_timeout": 0.5,
  "estop_enabled": true,
  "speed_limit_enabled": true
}
```

#### camera.json
```json
{
  "device": "/dev/video0",
  "width": 1280,
  "height": 720,
  "framerate": 30,
  "codec": "h264",
  "backend": "libcamera"
}
```

#### network.json
```json
{
  "interfaces": ["wlan0", "eth0", "usb0"],
  "ddns_enabled": true,
  "ddns_hostname": "mychair.local",
  "vpn_enabled": false
}
```

### GPIO Configuration

Edit `config/default_config.json` to customize:
- GPIO pin assignments
- Motor parameters
- Safety thresholds
- PWM frequencies

## Safety Features

The system includes multiple layers of safety:

### Hardware Safety
- **E-Stop Button**: Physical emergency stop (GPIO input)
- **Deadman Switch**: Requires continuous operator input
- **Watchdog Timer**: Automatic shutdown if service fails

### Software Safety
- **Speed Limiting**: Configurable maximum speeds
- **Acceleration Limiting**: Prevents sudden movements
- **Command Timeout**: Stops if no commands received
- **Input Validation**: All commands validated before execution

### Network Safety
- **Secure WebSocket**: WSS encryption for commands
- **Authentication**: Optional password/token protection
- **Rate Limiting**: Prevents command flooding
- **Connection Monitoring**: Detects and handles disconnections

### Safety Override
```bash
# Activate emergency stop from command line
python3 -m wheelchair_bot.safety.estop --trigger

# Reset after E-stop
python3 -m wheelchair_bot.safety.estop --reset
```

## Development

### Running Tests

Run the complete test suite:

```bash
# All tests
python3 -m pytest tests/ -v

# Unit tests only
python3 -m unittest discover -s tests -v

# Integration tests
python3 -m pytest tests/test_integration.py -v

# With coverage
python3 -m pytest --cov=wheelchair_bot tests/
```

### Mock Mode for Development

Test without hardware:

```bash
# Mock GPIO, camera, and network
python3 main.py --mock --verbose

# Mock specific components
python3 main.py --mock-gpio --mock-camera

# Run individual service in mock mode
python3 -m wheelchair_bot.services.teleopd --mock
```

### Code Quality

```bash
# Format code
black wheelchair_bot/ tests/

# Lint code
ruff check wheelchair_bot/ tests/

# Type checking
mypy wheelchair_bot/
```

### Building Documentation

```bash
# Generate API documentation
python3 -m pdoc wheelchair_bot --output-dir docs/api

# Build documentation site (if using mkdocs)
mkdocs build
```

### Adding New Features

The modular design makes it easy to extend:

1. **New Control Interface**: Add to `wheelchair_bot/controllers/`
2. **New Motor Type**: Implement in `wheelchair_bot/motors/`
3. **New Safety Feature**: Add to `wheelchair_bot/safety/`
4. **New Service**: Create in `wheelchair_bot/services/`

See [docs/contributing.md](docs/contributing.md) for detailed guidelines.

## Deployment

### Running as a System Service

Create a systemd service for automatic startup:

```bash
# Create service file
sudo nano /etc/systemd/system/wheelchair-bot.service
```

Service file content:
```ini
[Unit]
Description=Wheelchair Bot Tele-Robotics System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Wheelchair-Bot
ExecStart=/usr/bin/python3 /home/pi/Wheelchair-Bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable wheelchair-bot
sudo systemctl start wheelchair-bot
sudo systemctl status wheelchair-bot
```

### Remote Access Setup

#### Option 1: Local Network
Access via local IP: `http://192.168.1.X:8080`

#### Option 2: Dynamic DNS
Configure in `config/network.json` for external access:
```json
{
  "ddns_enabled": true,
  "ddns_provider": "duckdns",
  "ddns_hostname": "mychair.duckdns.org",
  "ddns_token": "your-token-here"
}
```

#### Option 3: VPN/Tailscale
For secure remote access without port forwarding:
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Access via Tailscale network
```

### Android Setup (Alternative Platform)

Use Termux on Android as the computing platform:

```bash
# Install Termux from F-Droid
# Inside Termux:
pkg install python clang libusb
pip install -r requirements.txt
python main.py --platform android
```

### Security Best Practices

1. **Change default passwords** in configuration files
2. **Enable HTTPS** for production use
3. **Use strong authentication** tokens
4. **Enable firewall** rules:
   ```bash
   sudo ufw allow 8080/tcp  # Web interface
   sudo ufw allow 8000/tcp  # API
   sudo ufw enable
   ```
5. **Regular updates**: Keep system and dependencies updated
6. **Monitor logs**: Check `/var/log/wheelchair-bot/` regularly

## Troubleshooting

### Common Issues

#### Connection Problems

**Cannot connect to web interface**
- Verify services are running: `systemctl status wheelchair-bot`
- Check firewall settings: `sudo ufw status`
- Confirm correct IP address and port
- Test local access first: `http://localhost:8080`

**WebRTC not connecting**
- Check STUN/TURN server configuration
- Verify network allows UDP traffic
- Test with browser console open (F12) for errors
- Ensure camera permissions are granted

#### Hardware Issues

**GPIO Permission Errors**
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Or run with sudo
sudo python3 main.py
```

**Motors not responding**
1. Check GPIO connections and wiring
2. Verify power supply to motors (separate from Pi)
3. Test with multimeter for voltage
4. Run diagnostic: `python3 -m wheelchair_bot.diagnostics.motors`
5. Check verbose logs: `python3 main.py --verbose`

**Camera not detected**
```bash
# List camera devices
v4l2-ctl --list-devices

# Test camera
libcamera-hello  # Raspberry Pi
gst-launch-1.0 v4l2src ! autovideosink  # USB camera

# Check permissions
sudo usermod -a -G video $USER
```

#### Software Issues

**Service won't start**
```bash
# Check logs
journalctl -u wheelchair-bot -n 50

# Run manually to see errors
python3 main.py --verbose

# Verify dependencies
pip3 install -r requirements.txt --upgrade
```

**High latency / lag**
- Reduce video resolution in `config/camera.json`
- Use wired Ethernet instead of Wi-Fi
- Close bandwidth-heavy applications
- Check CPU usage: `htop`

### Getting Help

1. Check the [documentation](docs/)
2. Review [existing issues](https://github.com/mrhegemon/Wheelchair-Bot/issues)
3. Run diagnostics: `python3 -m wheelchair_bot.diagnostics`
4. Enable debug logging: `--verbose` flag
5. Open a new issue with:
   - System information (`uname -a`, `python3 --version`)
   - Error logs
   - Configuration (redact sensitive info)
   - Steps to reproduce

## Performance Tuning

### Optimize Video Streaming

```json
// config/camera.json - Low latency preset
{
  "width": 640,
  "height": 480,
  "framerate": 24,
  "codec": "h264",
  "bitrate": 500000
}
```

### Reduce CPU Usage

```bash
# Use hardware encoding (Raspberry Pi)
echo "h264_v4l2m2m" | sudo tee -a /etc/modules

# Limit background processes
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

### Network Optimization

```bash
# Increase network buffer sizes
sudo sysctl -w net.core.rmem_max=26214400
sudo sysctl -w net.core.wmem_max=26214400
```
## API Reference

### WebSocket API (Control Commands)

Connect to `ws://hostname:8080/ws`

**Send movement command:**
```json
{
  "type": "movement",
  "direction": "forward",
  "speed": 50,
  "timestamp": 1699999999999
}
```

**Direction values:** `forward`, `backward`, `left`, `right`, `stop`

**Send configuration:**
```json
{
  "type": "config",
  "max_speed": 0.8,
  "acceleration_limit": 1.0
}
```

### REST API (Status and Config)

**Get system status:**
```bash
GET http://hostname:8000/api/status
```

Response:
```json
{
  "battery_level": 85,
  "is_moving": false,
  "speed": 0,
  "direction": null,
  "services": {
    "teleopd": "running",
    "streamer": "running",
    "safety_agent": "running"
  }
}
```

**Get configuration:**
```bash
GET http://hostname:8000/api/config
```

**Update configuration:**
```bash
POST http://hostname:8000/api/config
Content-Type: application/json

{
  "max_speed": 0.8,
  "turn_speed": 0.6
}
```

**Emergency stop:**
```bash
POST http://hostname:8000/api/emergency-stop
```

See [docs/api.md](docs/api.md) for complete API documentation.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and test thoroughly
4. Run tests: `python3 -m pytest tests/ -v`
5. Format code: `black wheelchair_bot/`
6. Commit changes: `git commit -am "Add feature"`
7. Push to branch: `git push origin feature/my-feature`
8. Create Pull Request

### Code Standards

- Follow PEP 8 style guide
- Add docstrings to all functions/classes
- Include type hints
- Write tests for new features
- Update documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with FastAPI, WebRTC, and modern web technologies
- Inspired by the need for accessible, affordable robotic assistance
- Community contributions and feedback

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/mrhegemon/Wheelchair-Bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mrhegemon/Wheelchair-Bot/discussions)

## Roadmap

- [ ] Multi-wheelchair support (fleet management)
- [ ] Advanced autonomous features (obstacle avoidance)
- [ ] Voice control integration
- [ ] Mobile app (iOS/Android native)
- [ ] ROS2 bridge (optional)
- [ ] Multi-camera support
- [ ] Sensor fusion (LIDAR, ultrasonic)
- [ ] Cloud telemetry and analytics

---

**Safety Notice**: This system is designed for assistive robotics and should be used responsibly. Always ensure proper safety measures, including physical E-stop, are in place. Never rely solely on software safety features. Test thoroughly in safe environments before real-world use.

