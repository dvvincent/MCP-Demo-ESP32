# ESP32 MicroPython Web Interface

A feature-rich MicroPython implementation for ESP32 with a modern web interface, providing LED control and system monitoring capabilities.

## Features

- **LED Control**: Turn on/off, blink, or pulse the built-in LED with PWM
- **Morse Code**: Flash messages in Morse code using the built-in LED
- **System Monitoring**: View memory usage and storage information
- **RESTful API**: Control the device programmatically via HTTP endpoints
- **Responsive Web UI**: Modern, mobile-friendly dark mode interface
- **MCP Integration**: Control via Model Context Protocol tools

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
- `GET /led/pulse?speed=X&min=Y&max=Z` - Create a smooth pulsing/breathing effect
  - `speed`: Controls the speed of the pulse (lower is faster, default: 20)
  - `min`: Minimum brightness (0-1023, default: 0)
  - `max`: Maximum brightness (0-1023, default: 1023)

  Example: `http://<device-ip>/led/pulse?speed=10&min=100&max=900`

### Morse Code
- `GET /morse?message=X` - Flash the message in Morse code using the LED
  - `message`: The text to flash in Morse code (URL-encoded)
  - `dot`: Duration of a dot in milliseconds (default: 100)
  - `dash`: Duration of a dash in milliseconds (default: 300)
  - `element_gap`: Gap between elements in milliseconds (default: 100)
  - `letter_gap`: Gap between letters in milliseconds (default: 300)
  - `word_gap`: Gap between words in milliseconds (default: 700)

  Example: `http://<device-ip>/morse?message=SOS&dot=100&dash=300`

### System Information
- `GET /status` - Get device status (LED state, uptime, IP address)
- `GET /memory` - Get detailed memory usage statistics
- `GET /storage` - Get filesystem storage information
- `GET /restart` - Restart the device



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

## MicroPython Examples

You can still use the serial REPL to interact with the ESP32 directly. Here are some useful commands:

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