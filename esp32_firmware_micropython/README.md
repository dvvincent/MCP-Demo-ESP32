# ESP32 MicroPython Web Interface

A feature-rich MicroPython implementation for ESP32 with a modern web interface, providing LED control, system monitoring, and an interactive REPL terminal.

## Features

- **LED Control**: Turn on/off or blink the built-in LED
- **System Monitoring**: View memory usage and storage information
- **Web REPL Terminal**: Execute Python commands directly from the web interface
- **RESTful API**: Control the device programmatically via HTTP endpoints
- **Responsive Web UI**: Modern, mobile-friendly interface built with Tailwind CSS

## File Structure
- `main.py` - Main application with web server and all functionality

## Setup

1. **Flash MicroPython**
   ```bash
   # Install esptool
   pip install esptool
   
   # Erase flash (replace /dev/ttyUSB0 with your port)
   esptool.py --port /dev/ttyUSB0 erase_flash
   
   # Flash MicroPython (download the latest firmware from micropython.org)
   esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 ESP32_GENERIC-20250415-v1.25.0.bin
   ```

2. **Upload Code**
   ```bash
   # Using ampy (recommended)
   pip install adafruit-ampy
   ampy --port /dev/ttyUSB0 put main.py
   
   # Or using rshell
   pip install rshell
   rshell -p /dev/ttyUSB0 cp main.py /main.py
   ```

3. **Connect to WiFi**
   - The device will automatically connect to the WiFi network specified in `main.py`
   - Check the serial output for the assigned IP address
   - Access the web interface at `http://<device-ip>`

## Web Interface Endpoints

### LED Control
- `GET /led/on` - Turn the built-in LED on
- `GET /led/off` - Turn the built-in LED off
- `GET /led/blink?count=X&interval=Y` - Blink the LED X times with Y ms interval

### System Information
- `GET /status` - Get device status (LED state, uptime, IP address)
- `GET /memory` - Get detailed memory usage statistics
- `GET /storage` - Get filesystem storage information
- `GET /restart` - Restart the device

### Web REPL Terminal
- `GET /repl` - Access the interactive Python REPL terminal
- `GET /execute?cmd=<command>` - Execute a Python command (used by the web interface)

## MCP Integration

This firmware is compatible with the MCP server's control interface, providing the following functions:

### LED Control
- `turn_led_on()` - Turn the LED on
- `turn_led_off()` - Turn the LED off
- `blink_led(count=3, interval_ms=200)` - Blink the LED a specified number of times

### System Information
- `get_esp32_status()` - Get current device status (LED state, uptime, IP)
- `get_memory_usage()` - Get detailed memory statistics
- `get_storage_info()` - Get filesystem information
- `restart_device()` - Restart the ESP32

## Web REPL Features

### Special Commands
- `help()` - Display help information for the web REPL
- `modules()` - List available MicroPython modules

### Example Commands
```python
# Basic Python
2 + 2
x = [1, 2, 3]; print(len(x))

# Hardware Control
import machine
led = machine.Pin(2, machine.Pin.OUT)
led.value(1)  # Turn on
led.value(0)  # Turn off

# System Information
import gc; gc.collect(); gc.mem_free()
import os; os.listdir()
```

## Configuration

Edit the following variables in `main.py` to customize the device:
- `SSID` - Your WiFi network name
- `PASSWORD` - Your WiFi password
- `led_pin` - The GPIO pin for the LED (default: 2)

## Notes
- **Port**: 80 (default HTTP)
- **WiFi**: Credentials are configured in `main.py`
- **LED**: Uses the built-in LED on GPIO2 by default
- **File Transfer**: Use `ampy` or `rshell` for file operations
- **REPL Access**: Available via serial connection or the web interface
- **Memory**: The device has limited memory; complex operations may require memory management

## Troubleshooting

1. **Device not connecting to WiFi**
   - Verify SSID and password are correct
   - Check if the network is in range
   - Monitor serial output for connection errors

2. **Web interface not loading**
   - Verify the device has a valid IP address
   - Check if any firewall is blocking port 80
   - Try accessing by IP address directly

3. **REPL commands not working**
   - Some complex commands may exceed memory limits
   - Break down complex operations into smaller steps
   - Use `gc.collect()` to free up memory

## License

MIT License - Feel free to use and modify for your projects.