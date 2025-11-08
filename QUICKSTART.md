# Quick Start Guide - Wheelchair-Bot Tele-Robotics Kit

Get up and running in minutes with the universal tele-robotics kit.

## Quick Setup Options

### Option 1: Testing Without Hardware (Recommended First)

Perfect for trying the system before setting up physical hardware.

```bash
# Clone repository
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot

# Install Python dependencies
pip3 install -r requirements.txt

# Run in mock mode
python3 main.py --mock
```

Then open your browser to `http://localhost:8080` and start controlling!

### Option 2: Raspberry Pi Setup (Full System)

Complete setup for deploying on a powered wheelchair.

#### Step 1: Install Operating System

1. Flash Raspberry Pi OS (64-bit recommended) to SD card
2. Enable SSH and configure Wi-Fi in Raspberry Pi Imager
3. Boot and SSH into your Pi: `ssh pi@raspberrypi.local`

#### Step 2: Install System Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libcamera-apps \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-good \
    git

# Add user to GPIO and video groups
sudo usermod -a -G gpio,video $USER
```

#### Step 3: Install Wheelchair-Bot

```bash
# Clone repository
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot

# Install Python dependencies
pip3 install -r requirements.txt
```

#### Step 4: Configure Hardware

Edit `config/default_config.json`:

```json
{
  "gpio": {
    "left_motor_forward": 17,
    "left_motor_backward": 18,
    "left_motor_enable": 12,
    "right_motor_forward": 22,
    "right_motor_backward": 23,
    "right_motor_enable": 13,
    "estop_input": 27
  },
  "camera": {
    "device": "libcamera",
    "width": 1280,
    "height": 720,
    "framerate": 30
  },
  "safety": {
    "max_speed": 0.8,
    "deadman_timeout": 0.5
  }
}
```

#### Step 5: Connect Hardware

1. **Motor Driver**: Connect to GPIO pins as configured
2. **Camera**: Attach Raspberry Pi Camera Module or USB webcam
3. **E-Stop**: Connect physical emergency stop button to GPIO 27
4. **Power**: Ensure separate power for motors (do not power from Pi!)

#### Step 6: Test and Run

```bash
# Test with mock GPIO first
python3 main.py --mock --verbose

# When ready, run with real hardware
sudo python3 main.py

# Or run as background service
sudo systemctl enable wheelchair-bot
sudo systemctl start wheelchair-bot
```

### Option 3: Android Device Setup

Use an Android phone/tablet as the control platform.

#### Step 1: Install Termux

1. Install Termux from F-Droid (not Google Play)
2. Open Termux

#### Step 2: Install Dependencies

```bash
# Update packages
pkg update && pkg upgrade

# Install required packages
pkg install python git libusb

# Clone repository
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 3: Configure for Android

```bash
# Run with Android platform configuration
python main.py --platform android --camera /dev/video0
```

The Android device will use its camera for video streaming.

## Access the Web Interface

Once running, access the control interface:

### Local Network Access
```
http://raspberrypi.local:8080
or
http://[raspberry-pi-ip]:8080
```

### From the Same Device
```
http://localhost:8080
```

### Remote Access (with Dynamic DNS configured)
```
https://yourname.duckdns.org:8080
```

## Using the Controls

### Web Interface

1. **Connect**: Click "Connect" button
2. **Wait**: Allow WebRTC connection to establish (5-10 seconds)
3. **Control**: Use on-screen joystick or keyboard

### Keyboard Controls

- **W** or **↑** - Forward
- **S** or **↓** - Backward
- **A** or **←** - Turn Left
- **D** or **→** - Turn Right
- **Space** or **Esc** - Emergency Stop
- **+/-** - Adjust speed

### Touch Controls (Mobile)

- Use the virtual joystick for precise directional control
- Tap speed buttons for quick speed adjustment
- Red emergency stop button always visible

## Running Individual Services

For development or debugging, run services separately:

```bash
# Terminal 1: Teleopd (control server)
python3 -m wheelchair_bot.services.teleopd

# Terminal 2: Video streamer
python3 -m wheelchair_bot.services.streamer

# Terminal 3: Safety agent
python3 -m wheelchair_bot.services.safety_agent

# Terminal 4: Network agent
python3 -m wheelchair_bot.services.net_agent
```

## Quick Tests

### Test Video Stream
```bash
# Raspberry Pi Camera
libcamera-hello --timeout 5000

# USB Camera
gst-launch-1.0 v4l2src ! autovideosink
```

### Test GPIO
```bash
# Run motor diagnostic
python3 -m wheelchair_bot.diagnostics.motors --test

# Test individual GPIO pins
python3 -m wheelchair_bot.diagnostics.gpio --pin 17
```

### Test WebSocket Connection
```bash
# Test teleopd API
curl http://localhost:8000/health

# Test WebSocket (using websocat)
websocat ws://localhost:8080/ws
```

## Common Issues & Solutions

### Cannot connect to web interface
```bash
# Check if service is running
sudo systemctl status wheelchair-bot

# Check firewall
sudo ufw allow 8080/tcp
sudo ufw allow 8000/tcp
```

### Camera not working
```bash
# List available cameras
v4l2-ctl --list-devices

# Test camera directly
libcamera-hello  # Raspberry Pi
```

### Motors not responding
```bash
# Check GPIO permissions
sudo usermod -a -G gpio $USER
# Then logout and login again

# Test in mock mode first
python3 main.py --mock --verbose
```

### High latency
```bash
# Use lower resolution in config/camera.json
{
  "width": 640,
  "height": 480,
  "framerate": 24
}
```

## Next Steps

1. **Customize Configuration**: Edit files in `config/` directory
2. **Set Up Auto-Start**: Enable systemd service for boot startup
3. **Configure Remote Access**: Set up dynamic DNS or VPN
4. **Add Safety Features**: Configure E-stop and deadman switch
5. **Read Full Documentation**: Check `docs/` for detailed guides

## Safety Checklist

Before first real-world use:

- [ ] Physical E-stop button installed and tested
- [ ] Deadman switch configured and working
- [ ] Speed limits set appropriately
- [ ] All connections secure and insulated
- [ ] Separate motor power supply (not from Pi)
- [ ] Tested in safe, controlled environment
- [ ] Emergency procedures documented
- [ ] Backup operator available

## Getting Help

- **Documentation**: See `README.md` and `docs/` folder
- **Issues**: https://github.com/mrhegemon/Wheelchair-Bot/issues
- **Logs**: Check with `journalctl -u wheelchair-bot -f`

---

**Remember**: Start with mock mode, test thoroughly, prioritize safety!
