# Wheelchair-Bot

A Raspberry Pi-based controller application for wheelchair robots with motor control, keyboard interface, and safety features.

## Features

- **Motor Control**: Differential drive motor control using GPIO pins
- **Keyboard Interface**: Simple keyboard control for testing and operation
- **Safety Features**: Emergency stop and speed limiting
- **Mock Mode**: Test without Raspberry Pi hardware
- **PWM Speed Control**: Smooth speed control using PWM
- **Configurable**: JSON-based configuration for easy customization

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- Motor driver board (L298N, L293D, or similar)
- Two DC motors for differential drive
- Power supply appropriate for your motors
- (Optional) Motor encoders for feedback

## GPIO Pin Configuration

Default GPIO pin assignments (BCM mode):

| Function | GPIO Pin |
|----------|----------|
| Left Motor Forward | 17 |
| Left Motor Backward | 18 |
| Left Motor Enable (PWM) | 12 |
| Right Motor Forward | 22 |
| Right Motor Backward | 23 |
| Right Motor Enable (PWM) | 13 |

These can be customized in `config/default_config.json`.

## Installation

### On Raspberry Pi

1. Clone the repository:
```bash
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

Note: Uncomment `RPi.GPIO` in `requirements.txt` when installing on actual Raspberry Pi hardware.

### For Development/Testing (without Raspberry Pi)

```bash
git clone https://github.com/mrhegemon/Wheelchair-Bot.git
cd Wheelchair-Bot
```

No additional dependencies required for mock mode.

## Usage

### Basic Usage

Run the controller with mock GPIO (for testing without hardware):

```bash
python3 main.py --mock
```

Run on actual Raspberry Pi hardware:

```bash
sudo python3 main.py
```

Note: `sudo` is required for GPIO access on Raspberry Pi.

### Command Line Options

```bash
python3 main.py [OPTIONS]

Options:
  --mock              Use mock GPIO (for testing without Raspberry Pi)
  --max-speed SPEED   Maximum speed percentage (0-100, default: 80)
  --turn-speed SPEED  Turn speed percentage (0-100, default: 60)
  --verbose, -v       Enable verbose logging
  -h, --help          Show help message
```

### Keyboard Controls

Once running, use these keys to control the wheelchair:

- **W** - Move Forward
- **S** - Move Backward
- **A** - Turn Left
- **D** - Turn Right
- **Space** - Stop
- **Q** - Quit

## Project Structure

```
Wheelchair-Bot/
├── wheelchair_controller/      # Main controller package
│   ├── __init__.py            # Package initialization
│   ├── controller.py          # Main wheelchair controller
│   ├── motor_driver.py        # Motor driver interface
│   └── keyboard_control.py    # Keyboard control interface
├── config/                    # Configuration files
│   └── default_config.json    # Default configuration
├── tests/                     # Test files (future)
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Configuration

Edit `config/default_config.json` to customize:

- GPIO pin assignments
- Speed limits
- Safety features
- Motor parameters

## Safety Features

- **Speed Limiting**: Maximum speed can be configured
- **Emergency Stop**: Immediate halt capability
- **Input Validation**: All speed values are clamped to safe ranges
- **Graceful Shutdown**: Proper cleanup of GPIO resources

## Development

### Running Tests

```bash
python3 main.py --mock --verbose
```

This runs the controller in mock mode with verbose logging for testing.

### Adding New Control Methods

The modular design makes it easy to add new control interfaces:

1. Create a new control class in `wheelchair_controller/`
2. Import and initialize in `main.py`
3. Implement your control logic using the `WheelchairController` API

## Troubleshooting

### GPIO Permission Errors

Run with `sudo`:
```bash
sudo python3 main.py
```

### Import Errors

Ensure you're in the correct directory:
```bash
cd /path/to/Wheelchair-Bot
python3 main.py
```

### Motor Not Responding

1. Check GPIO connections
2. Verify power supply to motors
3. Test with `--verbose` flag for detailed logging
4. Verify pin assignments in configuration

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source. Please check the repository for license details.

## Authors

Wheelchair-Bot Project Contributors