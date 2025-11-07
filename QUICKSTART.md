# Quick Start Guide

Get your Wheelchair-Bot up and running in 5 minutes!

## Prerequisites

- Linux system (Raspberry Pi OS, Ubuntu, etc.)
- Python 3.9 or higher
- Camera (USB webcam or Pi Camera)
- Internet connection

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the System

```bash
chmod +x start.sh stop.sh
./start.sh
```

You should see output like:
```
Starting Wheelchair Robot services...
Starting teleopd service on port 8000...
Starting streamer service on port 8001...
Starting safety agent service on port 8002...
Starting net agent service on port 8003...
Starting web client on port 8080...

All services started!
================================
Teleopd:     http://localhost:8000
Streamer:    http://localhost:8001
Safety:      http://localhost:8002
Net Agent:   http://localhost:8003
Web Client:  http://localhost:8080
================================
```

### 4. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8080
```

Or from another device on the same network:
```
http://YOUR_PI_IP_ADDRESS:8080
```

## First Steps

### Test the Interface

1. **Check Connection Status** - Should show "Connected" in green
2. **Check E-Stop Status** - Should show "Normal" in green
3. **Try the Joystick** - Click and drag the blue circle
4. **Adjust Speed** - Use the slider below the joystick
5. **Test E-Stop** - Click the red "EMERGENCY STOP" button
6. **Reset E-Stop** - Click "Reset E-Stop" to resume

### Keyboard Controls

- **Arrow Keys** - Control direction (↑ ↓ ← →)
- **Spacebar** - Emergency stop
- **1-9 Keys** - Set speed (1=10%, 9=90%)

## Verify Services

Run the test script:

```bash
python test_services.py
```

Expected output:
```
============================================================
Wheelchair-Bot Service Integration Tests
============================================================

=== Testing Teleopd Service ===
Testing Teleopd... ✓ OK - teleopd v1.0.0
Testing status endpoint... ✓ OK - 0 clients
Testing config endpoint... ✓ OK - max_speed: 1.0

=== Testing Streamer Service ===
Testing Streamer... ✓ OK - streamer v1.0.0
Testing status endpoint... ✓ OK - active: False, connections: 0

=== Testing Safety Agent Service ===
Testing Safety Agent... ✓ OK - safety-agent v1.0.0
Testing status endpoint... ✓ OK - monitoring: True, estop: False
Testing alerts endpoint... ✓ OK - 0 alerts

=== Testing Net Agent Service ===
Testing Net Agent... ✓ OK - net-agent v1.0.0
Testing status endpoint... ✓ OK - interfaces: 2, internet: True

============================================================
✓ All tests passed!
============================================================
```

## Try the Example Script

### Demo Mode (Automated Movement)

```bash
python example_control.py demo
```

This runs a pre-programmed sequence of movements.

### Status Mode (Check All Services)

```bash
python example_control.py status
```

Shows detailed status of all services.

### Control Mode (Keyboard Control)

```bash
python example_control.py control
```

Interactive command-line control:
- `w` - Forward
- `s` - Backward
- `a` - Left
- `d` - Right
- `x` - Stop
- `e` - E-stop
- `1-9` - Speed
- `q` - Quit

## Configuration

### Camera Settings

Edit `config/config.example.yaml`:

```yaml
streamer:
  camera:
    device: "/dev/video0"    # Change if needed
    resolution: "640x480"    # 1280x720 for HD
    framerate: 30            # Lower if laggy
```

Then copy to config.yaml:
```bash
cp config/config.example.yaml config/config.yaml
```

### Service Ports

Default ports:
- **8000** - Teleopd (control)
- **8001** - Streamer (video)
- **8002** - Safety Agent
- **8003** - Net Agent
- **8080** - Web Client

Change in each service's `main.py` if needed.

## Stopping the System

```bash
./stop.sh
```

## Troubleshooting

### Services Won't Start

**Check if ports are in use:**
```bash
lsof -i :8000
lsof -i :8001
```

**Kill processes on ports:**
```bash
./stop.sh
```

### Camera Not Working

**List cameras:**
```bash
v4l2-ctl --list-devices
```

**Test camera:**
```bash
# For USB webcam
ffplay /dev/video0

# For Pi Camera
libcamera-hello
```

**Fix permissions:**
```bash
sudo usermod -a -G video $USER
# Log out and back in
```

### Can't Access from Another Device

**Check firewall:**
```bash
sudo ufw allow 8080
```

**Find your IP:**
```bash
ip addr show
# Look for inet address (e.g., 192.168.1.100)
```

**Access from browser:**
```
http://192.168.1.100:8080
```

### WebSocket Won't Connect

1. Check teleopd is running: `curl http://localhost:8000/status`
2. Check browser console (F12) for errors
3. Verify URL in `web_client/app.js` matches your setup

## Next Steps

### For Development
📖 Read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

### For Hardware Setup
📖 Read [docs/HARDWARE.md](docs/HARDWARE.md)

### For API Integration
📖 Read [docs/API.md](docs/API.md)

### For System Overview
📖 Read [docs/OVERVIEW.md](docs/OVERVIEW.md)

## Docker Deployment (Alternative)

If you prefer Docker:

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Safety Reminder

⚠️ **IMPORTANT SAFETY NOTES:**

1. **Test in safe area** - Start in open space with obstacles
2. **E-stop accessible** - Always have emergency stop ready
3. **Supervised operation** - Never leave unattended
4. **Start slowly** - Use low speed (10-30%) initially
5. **Check connections** - Verify all hardware is secure

## Getting Help

- **Documentation** - Check the `docs/` folder
- **Examples** - See `example_control.py`
- **Issues** - Open issue on GitHub
- **Tests** - Run `test_services.py`

## Success Checklist

- [ ] All services started successfully
- [ ] Web interface loads at http://localhost:8080
- [ ] Connection status shows "Connected"
- [ ] Joystick responds to mouse/touch
- [ ] E-stop button works
- [ ] Test script passes all tests
- [ ] Camera device detected (check in streamer logs)

If all checked, you're ready to go! 🎉

---

**Version:** 1.0.0
**License:** MIT
**Repository:** https://github.com/mrhegemon/Wheelchair-Bot
