# Architecture - Wheelchair-Bot Tele-Robotics Kit

This document describes the architecture of the Wheelchair-Bot universal tele-robotics kit.

## Overview

Wheelchair-Bot is a lightweight, service-based tele-robotics system designed to turn almost any powered wheelchair into a remotely controllable robot. The architecture is modular, using commodity hardware and avoiding heavy frameworks like ROS.

## Design Principles

1. **Lightweight**: No ROS dependency, minimal overhead
2. **Modular**: Services can run independently
3. **Platform Agnostic**: Works on Raspberry Pi, Android, or standard Linux
4. **Safety First**: Multiple layers of safety features
5. **Real-Time**: Low latency control and video streaming
6. **Accessible**: Web-based interface, no app installation needed

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│                   (Control Interface)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Video      │  │   Joystick   │  │   Status     │     │
│  │   Display    │  │   Control    │  │   Monitor    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────┬──────────────┬──────────────┬─────────────────┘
             │              │              │
         WebRTC         WebSocket        REST
       (video/audio)    (commands)       (config/status)
             │              │              │
┌────────────▼──────────────▼──────────────▼─────────────────┐
│                    Raspberry Pi / Android                   │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   webrtc    │  │   teleopd    │  │  safety-agent   │  │
│  │   service   │  │   service    │  │    service      │  │
│  └──────┬──────┘  └───────┬──────┘  └────────┬────────┘  │
│         │                 │                    │           │
│  ┌──────▼──────┐  ┌───────▼──────┐  ┌────────▼────────┐  │
│  │  streamer   │  │    motor     │  │   deadman       │  │
│  │  service    │  │   control    │  │   switch        │  │
│  └──────┬──────┘  └───────┬──────┘  └────────┬────────┘  │
│         │                 │                    │           │
│  ┌──────▼──────┐  ┌───────▼──────────────────▼────────┐  │
│  │   Camera    │  │         GPIO / Motors             │  │
│  │ (libcamera/ │  │      (Motor Driver Board)         │  │
│  │  GStreamer) │  │                                    │  │
│  └─────────────┘  └────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              net-agent service                       │  │
│  │  (LTE/Wi-Fi management, DNS, secure access)         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Services

### 1. teleopd (Teleoperations Daemon)

**Purpose**: Main control service handling commands and configuration

**Technology**: Python FastAPI

**Responsibilities**:
- WebSocket server for real-time control commands
- REST API for configuration and status queries
- Command validation and rate limiting
- Motor control interface
- System orchestration

**Endpoints**:
- `ws://host:8080/ws` - WebSocket for commands
- `http://host:8000/api/status` - GET status
- `http://host:8000/api/config` - GET/POST configuration
- `http://host:8000/api/move` - POST movement commands
- `http://host:8000/health` - Health check

**Implementation**: `wheelchair_bot/services/teleopd.py`

### 2. webrtc (Video/Audio Streaming)

**Purpose**: Real-time video and audio streaming to web clients

**Technology**: WebRTC (with Python aiortc or similar)

**Responsibilities**:
- WebRTC peer connection management
- Video encoding and transmission
- Audio capture and streaming (optional)
- ICE candidate exchange
- Data channel for control backup

**Features**:
- Low latency (<100ms typical)
- Adaptive bitrate
- H.264 encoding
- STUN/TURN server support

**Implementation**: `wheelchair_bot/services/webrtc.py`, `webrtc.js`

### 3. streamer (Camera Capture)

**Purpose**: Camera capture and encoding for streaming

**Technology**: libcamera (Raspberry Pi) or GStreamer (general)

**Responsibilities**:
- Camera device management
- Video capture at configured resolution/framerate
- H.264 encoding
- Frame buffering
- Multiple camera support (future)

**Supported Cameras**:
- Raspberry Pi Camera Module (v1, v2, v3, HQ)
- USB webcams (UVC compatible)
- Android device cameras
- IP cameras (future)

**Configuration**:
```json
{
  "device": "/dev/video0",
  "backend": "libcamera",
  "width": 1280,
  "height": 720,
  "framerate": 30,
  "codec": "h264",
  "bitrate": 2000000
}
```

**Implementation**: `wheelchair_bot/services/streamer.py`

### 4. safety-agent (Safety Monitoring)

**Purpose**: Monitor and enforce safety constraints

**Technology**: Python with hardware interrupts

**Responsibilities**:
- E-stop button monitoring (GPIO interrupt)
- Deadman switch timeout enforcement
- Speed and acceleration limiting
- Watchdog timer for service health
- Emergency procedures

**Safety Features**:
- Hardware E-stop with GPIO interrupt
- Software deadman requiring periodic confirmation
- Configurable speed/acceleration limits
- Service health monitoring
- Automatic shutdown on failures

**Configuration**:
```json
{
  "estop_gpio": 27,
  "deadman_timeout": 0.5,
  "max_speed": 0.8,
  "max_angular_speed": 0.8,
  "watchdog_timeout": 2.0
}
```

**Implementation**: `wheelchair_bot/services/safety_agent.py`

### 5. net-agent (Network Management)

**Purpose**: Manage network connectivity and remote access

**Technology**: Python with system network tools

**Responsibilities**:
- Monitor LTE/Wi-Fi connectivity
- Automatic failover between interfaces
- Dynamic DNS updates
- VPN/secure tunnel management
- Connection quality reporting

**Features**:
- Multi-interface support (Wi-Fi, LTE, Ethernet)
- Automatic reconnection
- Dynamic DNS (DuckDNS, No-IP, etc.)
- Optional VPN (WireGuard, OpenVPN)
- Bandwidth monitoring

**Configuration**:
```json
{
  "interfaces": ["wlan0", "usb0", "eth0"],
  "priority": ["eth0", "wlan0", "usb0"],
  "ddns_enabled": true,
  "ddns_provider": "duckdns",
  "ddns_hostname": "mychair.duckdns.org",
  "vpn_enabled": false
}
```

**Implementation**: `wheelchair_bot/services/net_agent.py`

## Communication Flow

### Control Flow (User → Robot)

1. **User Input**: User interacts with web interface (joystick, keyboard)
2. **Command Generation**: JavaScript creates command JSON
3. **WebSocket Send**: Command sent via WebSocket to teleopd
4. **Validation**: teleopd validates command (safety-agent consulted)
5. **Execution**: Command converted to motor control signals
6. **GPIO Output**: Motor driver receives PWM signals
7. **Motion**: Wheelchair moves

### Video Flow (Robot → User)

1. **Capture**: streamer captures frames from camera
2. **Encode**: Frames encoded to H.264
3. **Stream**: Encoded stream sent to webrtc service
4. **WebRTC**: Peer connection transmits to browser
5. **Decode**: Browser decodes and displays video
6. **Display**: User sees real-time video

### Status Flow (Bidirectional)

1. **Status Collection**: Services report status to teleopd
2. **REST API**: Web client polls `/api/status`
3. **Response**: JSON with current system state
4. **UI Update**: Status displayed in web interface

## Component Details

### Motor Control System

**Package**: `wheelchair_bot/motors/`

**Components**:
- `base.py`: Abstract motor controller interface
- `differential.py`: Differential drive implementation
- `gpio_driver.py`: GPIO-based motor driver (L298N, etc.)

**Control Pipeline**:
```
Velocity Command (linear, angular)
    ↓
Differential Drive Calculation
    ↓
Motor Speeds (left, right)
    ↓
PWM Signals (GPIO)
    ↓
Motor Driver Board
    ↓
DC Motors
```

### Safety System

**Package**: `wheelchair_bot/safety/`

**Components**:
- `deadman.py`: Deadman switch with timeout
- `limiter.py`: Speed and acceleration limiting
- `estop.py`: Emergency stop handling (future)
- `watchdog.py`: Service health monitoring (future)

**Safety Layers**:
1. **Hardware E-Stop**: Physical button → GPIO interrupt → immediate stop
2. **Deadman Switch**: Requires command within timeout period
3. **Speed Limits**: Maximum velocity constraints
4. **Acceleration Limits**: Rate of change constraints
5. **Watchdog**: Service health monitoring

### Web Client

**Location**: `web/` and root directory

**Files**:
- `index.html`: Main UI structure
- `webrtc.js`: WebRTC connection management
- `controller.js`: Control logic and event handling
- `styles.css`: UI styling

**Features**:
- Virtual joystick control
- Keyboard input
- Touch support for mobile
- Real-time video display
- Connection status monitoring
- Speed adjustment

## Technology Stack

### Backend Services
- **Language**: Python 3.9+
- **Web Framework**: FastAPI
- **WebSocket**: FastAPI WebSockets / asyncio
- **WebRTC**: aiortc or similar (Python WebRTC)
- **Video**: libcamera, GStreamer
- **GPIO**: RPi.GPIO (Raspberry Pi)
- **Async**: asyncio, aiohttp

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling with responsive design
- **JavaScript**: ES6+ (no frameworks required)
- **WebRTC**: Native browser APIs
- **WebSocket**: Native WebSocket API

### Protocols
- **WebRTC**: Video/audio streaming
- **WebSocket**: Real-time commands
- **REST**: Configuration and status
- **HTTP/HTTPS**: Web interface delivery
- **STUN/TURN**: NAT traversal

### Hardware Interfaces
- **GPIO**: Motor control, E-stop input
- **CSI**: Camera interface (Raspberry Pi)
- **USB**: Webcams, LTE modems
- **I2C/SPI**: Sensors (optional)

## Design Decisions

### Why No ROS?
- **Simplicity**: Lower barrier to entry
- **Resources**: Lighter on CPU/RAM
- **Complexity**: Easier to understand and modify
- **Dependencies**: Fewer packages to maintain

Note: ROS2 bridge can be added as optional component for advanced users.

### Why FastAPI?
- **Performance**: Async I/O for concurrent connections
- **Documentation**: Automatic OpenAPI docs
- **Validation**: Built-in with Pydantic
- **Modern**: Type hints, async/await support

### Why WebRTC?
- **Low latency**: Near real-time video
- **NAT traversal**: Works across networks
- **Browser support**: No plugins needed
- **Adaptive**: Bitrate adjustment for varying conditions

### Why Python?
- **Rapid development**: Quick to iterate
- **Libraries**: Rich ecosystem for robotics
- **Accessibility**: Easy for contributors
- **GPIO support**: Native Raspberry Pi support

## Future Enhancements

- Multi-wheelchair fleet management
- Cloud telemetry backend
- ROS2 bridge for advanced autonomy (optional)
- Multi-camera support
- Sensor fusion (LIDAR, ultrasonic, IMU)
- Voice control interface
- Autonomous obstacle avoidance
- Path planning and navigation
- Battery management system integration
- Mobile app (iOS/Android native)
