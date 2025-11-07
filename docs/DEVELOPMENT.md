# Development Guide

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Text editor or IDE (VSCode recommended)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install black flake8 pytest pytest-asyncio
```

## Running Services for Development

### Option 1: Individual Services

Run each service in a separate terminal:

```bash
# Terminal 1 - Teleopd
cd services/teleopd
python main.py

# Terminal 2 - Streamer
cd services/streamer
python main.py

# Terminal 3 - Safety Agent
cd services/safety_agent
python main.py

# Terminal 4 - Net Agent
cd services/net_agent
python main.py

# Terminal 5 - Web Client
cd web_client
python -m http.server 8080
```

### Option 2: All Services

```bash
./start.sh
```

### Option 3: Docker Compose

```bash
docker-compose up
```

## Code Style

### Python

Use Black for formatting:

```bash
black services/
```

Use Flake8 for linting:

```bash
flake8 services/ --max-line-length=100
```

### JavaScript

Follow standard JavaScript conventions:
- Use camelCase for variables and functions
- Use PascalCase for classes
- 4-space indentation
- Semicolons optional but consistent

## Testing

### Run Integration Tests

```bash
# Make sure services are running first
./start.sh

# Run tests in another terminal
python test_services.py
```

### Manual Testing

1. Open web client: `http://localhost:8080`
2. Check browser console for errors (F12)
3. Test joystick control
4. Test E-stop functionality
5. Verify video stream (if camera available)

### API Testing with cURL

```bash
# Test teleopd status
curl http://localhost:8000/status

# Trigger E-stop
curl -X POST http://localhost:8000/estop

# Reset E-stop
curl -X POST http://localhost:8000/estop/reset

# Update config
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{"max_speed": 0.8, "enable_estop": true, "control_mode": "joystick", "timeout_seconds": 5}'
```

### WebSocket Testing

Use a WebSocket client like `websocat` or browser DevTools:

```bash
# Install websocat
cargo install websocat

# Connect to teleopd
websocat ws://localhost:8000/ws/commands
```

## Project Structure

```
Wheelchair-Bot/
├── services/              # Backend services
│   ├── __init__.py
│   ├── teleopd/          # Teleoperation daemon
│   │   ├── __init__.py
│   │   └── main.py
│   ├── streamer/         # Video streaming
│   │   ├── __init__.py
│   │   └── main.py
│   ├── safety_agent/     # Safety monitoring
│   │   ├── __init__.py
│   │   └── main.py
│   └── net_agent/        # Network monitoring
│       ├── __init__.py
│       └── main.py
├── web_client/           # Frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
├── config/               # Configuration
│   └── config.example.yaml
├── docs/                 # Documentation
│   ├── API.md
│   ├── HARDWARE.md
│   └── DEVELOPMENT.md (this file)
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container image
├── docker-compose.yml   # Multi-container setup
├── start.sh             # Start all services
├── stop.sh              # Stop all services
└── test_services.py     # Integration tests
```

## Adding New Features

### Adding a New Command Type

1. **Update teleopd Command model**:

```python
# services/teleopd/main.py
class Command(BaseModel):
    type: str  # Add your new type here
    # ... add new fields
```

2. **Handle command in WebSocket endpoint**:

```python
# In websocket_commands function
if command.type == "your_new_type":
    # Handle the new command
    pass
```

3. **Update web client**:

```javascript
// web_client/app.js
sendCustomCommand() {
    const command = {
        type: 'your_new_type',
        // ... add fields
        timestamp: Date.now() / 1000
    };
    this.sendCommand(command);
}
```

### Adding a New Service

1. Create new service directory:

```bash
mkdir -p services/new_service
touch services/new_service/__init__.py
```

2. Create `services/new_service/main.py`:

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="New Service")

@app.get("/")
async def root():
    return {"service": "new_service", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004)
```

3. Update `start.sh` to include new service

4. Update `docker-compose.yml` if using Docker

### Adding New Sensors

1. Create sensor interface in appropriate service
2. Update status models to include sensor data
3. Update web client to display sensor data

Example:

```python
# In net_agent or safety_agent
class SensorData(BaseModel):
    temperature: float
    battery_voltage: float
    # ...

async def read_sensors():
    # Read sensor values
    return SensorData(temperature=25.5, battery_voltage=12.4)
```

## Debugging

### Enable Debug Logging

```python
# In any service main.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Browser DevTools

- Open DevTools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for WebSocket messages
- Check Application tab for storage

### Service Logs

```bash
# If using systemd
journalctl -u wheelchair-bot -f

# If using Docker
docker-compose logs -f

# If using start.sh
# Check terminal output
```

## Common Issues

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Camera Not Working

```bash
# Check camera device
ls -l /dev/video*

# Test with ffplay
ffplay /dev/video0

# Check permissions
sudo usermod -a -G video $USER
```

### WebSocket Connection Refused

- Check if teleopd service is running
- Check firewall settings
- Verify correct URL in web_client/app.js

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Performance Optimization

### Video Streaming

- Lower resolution for better performance
- Adjust framerate based on network
- Use hardware encoding if available

```yaml
# config/config.yaml
streamer:
  camera:
    resolution: "640x480"  # Lower for better performance
    framerate: 15          # Lower for slower networks
```

### Network Optimization

- Increase check intervals if CPU is constrained
- Use local network instead of internet when possible

### Safety Checks

- Balance check frequency with system load
- Use efficient monitoring algorithms

## Contributing

### Workflow

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes
4. Test thoroughly
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

### Commit Messages

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build/tooling changes

Example: `feat: add obstacle detection sensor`

### Code Review

- Follow existing code style
- Add tests for new features
- Update documentation
- Ensure no security vulnerabilities

## Deployment

### Production Checklist

- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Configure proper CORS
- [ ] Set up VPN for remote access
- [ ] Configure firewall
- [ ] Test E-stop thoroughly
- [ ] Set up monitoring/logging
- [ ] Create backup strategy
- [ ] Document deployment process

### Monitoring

Consider adding:
- Prometheus metrics
- Grafana dashboards
- Log aggregation (ELK stack)
- Uptime monitoring
- Alert system

## Resources

### Documentation

- FastAPI: https://fastapi.tiangolo.com/
- WebSockets: https://websockets.readthedocs.io/
- aiortc: https://github.com/aiortc/aiortc
- psutil: https://psutil.readthedocs.io/

### Community

- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas

### Learning

- WebRTC: https://webrtc.org/
- Python async: https://docs.python.org/3/library/asyncio.html
- WebSocket protocol: https://datatracker.ietf.org/doc/html/rfc6455

---

Happy coding! 🚀
