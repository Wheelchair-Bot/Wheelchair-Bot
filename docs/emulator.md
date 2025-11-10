# Wheelchair Emulator and Testing Framework

This document describes the wheelchair emulator layer that enables development and testing without physical hardware.

## Architecture

The emulator provides complete simulation of all wheelchair subsystems:

### Core Interfaces

All subsystems implement abstract interfaces defined in `src/wheelchair/interfaces.py`:

- **WheelchairDrive**: Motor control and movement physics
- **Controller**: Input from joystick/gamepad/scripted commands
- **SensorSuite**: IMU, proximity sensors with configurable noise
- **PowerSystem**: Battery simulation with discharge modeling
- **SafetyMonitor**: Deadman switch, obstacle avoidance, safety checks

### Controller Families

The emulator now supports realistic simulation of different commercial wheelchair controller families, as documented in `docs/wheelchair-support.md`. This allows testing with the specific signal characteristics and behavior of real wheelchair controllers.

**Supported Controller Families:**

**Tier 1 - Analog Controllers (~60% market coverage):**
- **PG Drives R-Net**: DB9 connector, 0-5V analog proportional control
  - Used in: Permobil M3/M5, Quickie Q500/Q300/Q400/Q700
  - Features: 15% deadzone, mode selection, enable line
  
- **Dynamic Controls Shark/DX**: 4-pin DCI connector, Hall effect sensors
  - Used in: Merits Vision, Shoprider 6Runner
  - Features: 0-3.3V range, 12% deadzone, simple analog axes
  
- **PG Drives VR2/Pilot+/VSI**: 4-pin connector, analog proportional
  - Used in: Pride Jazzy series, Golden Technologies, Hoveround
  - Features: Speed potentiometer, 10% deadzone, most common in US

**Tier 2 - Digital Bus Controllers (~25% market coverage):**
- **Dynamic Controls LiNX DX**: 4-pin micro with CAN-like digital bus
  - Used in: Invacare TDX SP2, Aviva RX, Drive Titan AXS
  - Features: Telemetry support, configuration via bus, 8% deadzone
  
- **Q-Logic 3/NE Series**: CAN/RS485 hybrid digital bus
  - Used in: Quantum Edge 3, Quantum 4 Front 2
  - Features: Drive profiles, specialty controls, advanced diagnostics

**Generic Fallback**: Basic analog controller for unspecified systems

### Emulator Implementations

Located in `src/wheelchair/emulator/`:

- **EmulatedDrive**: Differential drive kinematics with acceleration limits
- **EmulatedController**: Scriptable or interactive input source with controller family support
- **EmulatedSensorSuite**: Sensor simulation with Gaussian noise
- **EmulatedPowerSystem**: Battery discharge based on power consumption
- **EmulatedSafetyMonitor**: Safety checks and speed limiting
- **SimulationLoop**: Event loop coordinating all subsystems at fixed rate

### Key Features

- **Dependency Injection**: Real hardware can replace emulator classes
- **Configurable**: YAML/TOML configuration for all parameters
- **Deterministic**: Seedable RNG for reproducible tests
- **Realistic Physics**: Kinematic model with velocity/acceleration limits
- **Safety First**: Emergency stop, deadman switch, obstacle avoidance
- **Controller Family Simulation**: Accurate modeling of commercial controller behavior

## Getting Started

### Installation

```bash
# Install package with development dependencies
pip install -e ".[dev]"

# Or use the Makefile
make install
```

### Running the Emulator

```bash
# Run with default configuration
wheelchair-sim

# Run with custom configuration
wheelchair-sim --config config/default.yaml

# Run for specific duration
wheelchair-sim --duration 30

# Run in interactive mode (future feature)
wheelchair-sim --interactive

# Or use Makefile
make sim
```

### Configuration

Edit `config/default.yaml` to customize emulator behavior:

```yaml
wheelchair:
  wheelbase: 0.6          # Distance between wheels (m)
  max_velocity: 2.0       # Maximum speed (m/s)
  max_acceleration: 1.0   # Maximum acceleration (m/s²)
  controller_family: vr2_pilot  # Controller family to emulate (optional)

sensors:
  imu_noise_stddev: 0.01  # IMU noise level
  proximity_range: 5.0    # Sensor range (m)

safety:
  deadman_timeout: 0.5    # Deadman timeout (s)
  obstacle_stop_distance: 0.5  # Emergency stop distance (m)

simulation:
  update_rate: 50.0       # Simulation frequency (Hz)
  seed: 42                # Random seed (null for random)
```

### Using Controller Families

The emulator supports simulating specific wheelchair controller families for realistic testing:

```python
from wheelchair.emulator.controller import EmulatedController
from wheelchair.controller_families import ControllerFamily

# Create controller with R-Net family (Permobil, Quickie)
controller = EmulatedController(controller_family=ControllerFamily.RNET)

# Set raw voltage signals (0-5V, 2.5V center)
controller.set_raw_signals(
    axis_x_voltage=2.5,  # Centered left/right
    axis_y_voltage=4.0,  # Forward movement
    enable_line=True,    # Deadman switch pressed
)

# Read processed input (with R-Net's 15% deadzone applied)
input_data = controller.read_input()
print(f"Linear: {input_data.linear}, Angular: {input_data.angular}")

# Get controller characteristics
chars = controller.get_signal_characteristics()
print(f"Family: {chars['family']}, Connector: {chars['connector']}")
```

**Available Controller Families:**
- `ControllerFamily.RNET` - PG Drives R-Net (DB9, 0-5V)
- `ControllerFamily.SHARK_DX` - Dynamic Shark/DX (4-pin DCI, 0-3.3V)
- `ControllerFamily.VR2_PILOT` - PG Drives VR2/Pilot+ (4-pin, 0-5V, speed pot)
- `ControllerFamily.LINX_DX` - Dynamic LiNX (digital bus)
- `ControllerFamily.QLOGIC` - Q-Logic 3/NE (CAN/RS485 bus)
- `ControllerFamily.GENERIC` - Generic analog fallback

**Example: VR2 with Speed Potentiometer:**
```python
controller = EmulatedController(controller_family=ControllerFamily.VR2_PILOT)

# Full joystick forward at 50% speed setting
controller.set_raw_signals(
    axis_y_voltage=5.0,       # Full forward
    speed_pot_voltage=2.5,    # 50% speed (0-5V range)
)

input_data = controller.read_input()
# Output will be scaled by 50%: linear ≈ 0.45 instead of 0.9
```

**Example: Digital Bus Controllers (LiNX, Q-Logic):**
```python
controller = EmulatedController(controller_family=ControllerFamily.LINX_DX)

# Set bus data (already normalized -1.0 to 1.0)
controller.set_raw_signals(
    bus_data={
        "linear_axis": 0.8,
        "angular_axis": -0.3,
        "enable": True,
        "emergency_stop": False,
    }
)

input_data = controller.read_input()
```

## Running Tests

### All Tests

```bash
# Run complete test suite
python scripts/run_tests.py

# Or use Makefile
make test

# Run specific test file
pytest src/tests/test_drive.py -v

# Run with specific coverage
pytest --cov=src/wheelchair --cov-report=html
```

### Test Coverage

Tests cover:

- ✓ Motor speed clamping and acceleration limits
- ✓ Controller input validation and scripting
- ✓ Controller family signal processing (R-Net, VR2, Shark, LiNX, Q-Logic)
- ✓ Analog and digital bus controller behavior
- ✓ Deadzone application for different controller types
- ✓ Speed potentiometer effects (VR2)
- ✓ Drive profile scaling (Q-Logic)
- ✓ Voltage range conversions (5V vs 3.3V systems)
- ✓ Sensor noise and obstacle injection
- ✓ Battery discharge and voltage curves
- ✓ Safety triggers and speed limiting
- ✓ Integration of all subsystems
- ✓ Property-based testing with Hypothesis

Current coverage: ~85%+

**Controller Family Test Statistics:**
- 52 controller family-specific tests
- 26 emulator integration tests with families
- 11 backward compatibility tests
- Total: 154 tests (all passing)

## Extending with Real Hardware

The emulator architecture uses dependency injection to allow real hardware integration:

### Example: Real Motor Driver

```python
from wheelchair.interfaces import WheelchairDrive

class RPiMotorDriver(WheelchairDrive):
    """Real motor driver using Raspberry Pi GPIO."""
    
    def __init__(self, config):
        # Initialize GPIO, motor controller
        pass
    
    def set_motor_speeds(self, left, right):
        # Send PWM signals to motor controller
        pass
    
    def get_motor_speeds(self):
        # Read encoder feedback
        pass
    
    def emergency_stop(self):
        # Immediately halt motors
        pass
    
    def update(self, dt):
        # Read encoder position, update odometry
        pass

# Use in place of emulator
from wheelchair.factory import create_emulator

config = EmulatorConfig()
loop = create_emulator(config)

# Replace emulated drive with real hardware
loop.drive = RPiMotorDriver(config.wheelchair)
```

### Integration Steps

1. **Implement Interface**: Create class implementing the appropriate interface
2. **Replace Component**: Substitute in factory or loop creation
3. **Test Incrementally**: Start with one component, validate before adding more
4. **Keep Emulator**: Use emulator for CI/CD and offline development

### Interfaces to Implement

- `WheelchairDrive`: GPIO motor control, encoder feedback
- `Controller`: Bluetooth gamepad, physical joystick
- `SensorSuite`: Real IMU (MPU6050), ultrasonic/lidar sensors
- `PowerSystem`: Battery voltage monitoring via ADC
- `SafetyMonitor`: Hardware emergency stop button

## Development Workflow

### Typical Development Cycle

```bash
# 1. Make code changes
vim src/wheelchair/emulator/drive.py

# 2. Run tests
make test

# 3. Test emulator
make sim

# 4. Format code
make format

# 5. Run linters
make lint

# 6. Commit changes
git add .
git commit -m "Improved acceleration model"
```

### Adding New Features

1. Update interfaces if needed (`src/wheelchair/interfaces.py`)
2. Implement in emulator classes (`src/wheelchair/emulator/`)
3. Add configuration parameters (`src/wheelchair/config.py`)
4. Write tests (`src/tests/`)
5. Update documentation

### Writing Tests

Tests use pytest with fixtures:

```python
import pytest
from wheelchair.config import WheelchairConfig
from wheelchair.emulator.drive import EmulatedDrive

class TestMyFeature:
    @pytest.fixture
    def drive(self):
        config = WheelchairConfig()
        state = WheelchairState()
        return EmulatedDrive(config, state)
    
    def test_my_feature(self, drive):
        # Test implementation
        assert drive.some_method() == expected_value
```

## Project Structure

```
Wheelchair-Bot/
├── src/wheelchair/              # Emulator source code
│   ├── interfaces.py            # Abstract interfaces
│   ├── config.py                # Configuration models
│   ├── factory.py               # Factory for creating emulator
│   ├── cli.py                   # Command-line interface
│   └── emulator/                # Emulator implementations
│       ├── drive.py             # Drive system
│       ├── controller.py        # Controller input
│       ├── sensors.py           # Sensor suite
│       ├── power.py             # Power system
│       ├── safety.py            # Safety monitor
│       └── loop.py              # Simulation loop
├── src/tests/                   # Emulator tests
│   ├── test_drive.py
│   ├── test_controller.py
│   ├── test_sensors.py
│   ├── test_power.py
│   ├── test_safety.py
│   ├── test_integration.py
│   └── test_properties.py       # Hypothesis property tests
├── wheelchair_bot/              # Existing wheelchair package
├── wheelchair_controller/       # Existing controller package
├── tests/                       # Existing tests
├── config/                      # Configuration files
│   └── default.yaml             # Default emulator config
├── scripts/
│   └── run_tests.py             # Test runner
├── Makefile                     # Build targets
└── pyproject.toml               # Project metadata
```

## Troubleshooting

### Import Errors

```bash
# Install in development mode
pip install -e .
```

### Test Failures

```bash
# Run specific test with verbose output
pytest src/tests/test_drive.py::TestEmulatedDrive::test_forward_movement -vv

# Check for environment issues
python -c "import wheelchair; print(wheelchair.__version__)"
```

### Emulator Won't Start

```bash
# Verify configuration is valid
python -c "from wheelchair.config import EmulatorConfig; EmulatorConfig.from_yaml('config/default.yaml')"

# Check dependencies
pip list | grep -E "(pydantic|pyyaml|pytest)"
```

## Performance Considerations

- Default update rate: 50 Hz (adequate for most testing)
- Increase `realtime_factor` for faster-than-realtime simulation
- Use `seed` parameter for deterministic, reproducible tests
- Profile with: `python -m cProfile -o profile.stats wheelchair-sim`

## Contributing

When contributing emulator improvements:

1. Follow existing code style (Black formatting)
2. Add comprehensive tests (aim for >85% coverage)
3. Update configuration schema if adding parameters
4. Document new interfaces and public APIs
5. Test with both emulator and on hardware (if available)

## License

See LICENSE file in repository root.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
