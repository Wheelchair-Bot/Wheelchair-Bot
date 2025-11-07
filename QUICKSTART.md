# Quick Start Guide

## Testing Without Raspberry Pi

1. **Run the Demo**
   ```bash
   python3 demo.py
   ```
   This will show automated movement patterns using mock GPIO.

2. **Interactive Control**
   ```bash
   python3 main.py --mock
   ```
   Then use keyboard controls:
   - `w` - Forward
   - `s` - Backward
   - `a` - Turn Left
   - `d` - Turn Right
   - `space` - Stop
   - `q` - Quit

3. **Run Tests**
   ```bash
   python3 -m unittest discover -s tests -v
   ```

## Running on Raspberry Pi

1. **Install Dependencies**
   ```bash
   pip3 install RPi.GPIO
   ```

2. **Connect Motors**
   - Connect your motor driver board to GPIO pins as specified in README.md
   - Ensure proper power supply for motors
   - Double-check all connections

3. **Run Controller**
   ```bash
   sudo python3 main.py
   ```
   (Note: `sudo` is required for GPIO access)

4. **Customize Speed**
   ```bash
   sudo python3 main.py --max-speed 60 --turn-speed 40
   ```

## Configuration

Edit `config/default_config.json` to change:
- GPIO pin assignments
- Default speeds
- Safety parameters

## Troubleshooting

**"Permission denied" error:**
- Run with `sudo` on Raspberry Pi

**Motors don't respond:**
- Check GPIO connections
- Verify power supply
- Run with `--verbose` flag for detailed logs
- Test with mock mode first: `python3 main.py --mock --verbose`

**Import errors:**
- Make sure you're in the project directory
- On Raspberry Pi, ensure RPi.GPIO is installed

## Next Steps

- Customize GPIO pin assignments in `config/default_config.json`
- Adjust speed limits for your specific motors
- Add additional control interfaces (joystick, web, etc.)
- Implement sensor integration (ultrasonic, encoders, etc.)
