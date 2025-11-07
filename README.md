# Wheelchair-Bot

A Python interface for controlling popular electric wheelchairs using game controllers (Xbox, PlayStation) or custom joysticks.

## Features

- **Multiple Wheelchair Models**: Pre-configured support for popular electric wheelchair models
  - Permobil M3 Corpus
  - Quantum Q6 Edge
  - Invacare TDX SP2
  - Pride Jazzy Elite HD

- **Controller Support**: 
  - Gamepad controllers (Xbox, PlayStation, etc.) via pygame
  - Custom joystick interfaces
  - Easy-to-extend controller base class

- **Motor Control**:
  - Differential drive kinematics
  - Direct motor speed control
  - Velocity-based control

- **Safety Features**:
  - Speed limiting
  - Acceleration limiting
  - Deadman switch
  - Emergency stop

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### View Supported Wheelchair Models

```bash
python examples/show_models.py
```

### Run Simulation

Test the interface with a simulated joystick controller:

```bash
python examples/simulated_control.py
```

### Control with Gamepad

Connect an Xbox or PlayStation controller and run:

```bash
python examples/basic_control.py
```

## Usage

### Basic Example

```python
from wheelchair_bot.wheelchairs.models import QuantumQ6Edge
from wheelchair_bot.controllers.gamepad import GamepadController
from wheelchair_bot.motors.differential import DifferentialDriveController
from wheelchair_bot.system import WheelchairControlSystem

# Create wheelchair instance
wheelchair = QuantumQ6Edge()

# Create controller (gamepad at index 0)
controller = GamepadController(controller_id=0)

# Create motor controller
motor_controller = DifferentialDriveController()

# Create and configure control system
control_system = WheelchairControlSystem(
    wheelchair=wheelchair,
    controller=controller,
    motor_controller=motor_controller,
)

# Set safety limits
control_system.speed_limiter.set_max_linear(0.5)  # 50% max speed

# Run the control system
control_system.run()
```

### Creating a Custom Wheelchair Model

```python
from wheelchair_bot.wheelchairs.base import Wheelchair

class MyWheelchair(Wheelchair):
    def __init__(self):
        super().__init__(
            name="My Custom Wheelchair",
            max_speed=2.0,  # m/s
            wheel_base=0.45,  # meters
            wheel_diameter=0.35,  # meters
        )
    
    def get_motor_config(self):
        return {
            "type": "mid_wheel_drive",
            "motor_count": 2,
            "motor_type": "brushless_dc",
            "max_voltage": 24,
            "max_current": 50,
        }
```

## Architecture

The system consists of four main components:

1. **Wheelchair Models** (`wheelchair_bot.wheelchairs`): Define physical properties and motor configurations
2. **Controllers** (`wheelchair_bot.controllers`): Handle input from various controller types
3. **Motor Controllers** (`wheelchair_bot.motors`): Convert velocity commands to motor outputs
4. **Safety Features** (`wheelchair_bot.safety`): Implement speed/acceleration limits and safety switches

## Safety

This interface includes multiple safety features:

- **Speed Limiter**: Caps maximum linear and angular velocities
- **Acceleration Limiter**: Smooths acceleration/deceleration
- **Deadman Switch**: Requires periodic confirmation of operator presence
- **Emergency Stop**: Immediately halts all motor activity

⚠️ **WARNING**: This is a software interface for educational and development purposes. Actual wheelchair control requires proper hardware integration, extensive testing, and compliance with medical device regulations. Always consult with medical professionals and follow all safety guidelines.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Disclaimer

This software is provided for educational and development purposes only. The authors are not responsible for any injury, damage, or other consequences resulting from the use of this software. Always prioritize safety and consult with qualified professionals before implementing any wheelchair control system.