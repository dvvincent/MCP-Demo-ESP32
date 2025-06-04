# ESP32 LED Controller with MCP

This project implements a Model Context Protocol (MCP) server that allows you to control an LED on an ESP32 device over your local network using MicroPython firmware.

## Project Structure

- `server/` - Contains the Python MCP server implementation
- `esp32_firmware_micropython/` - Contains the MicroPython code for the ESP32 device
- `esp32_firmware/` - Contains a sample ESP32 firmware for the ESP32 device
- `requirements.txt` - Python dependencies for the MCP server

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/dvvincent/MCP-Demo-ESP32.git
   cd MCP-Demo-ESP32
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   This will install the following dependencies:
   - fastmcp
   - requests
   - pydantic
   - typing-extensions
   - python-dotenv

3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

## Features

- Control an LED on an ESP32 device over WiFi
- Smooth LED pulsing with adjustable speed and brightness
- Morse code flashing for transmitting messages via the LED
- Web interface for manual control
- MCP server for programmatic control

### LED Control Functions

#### Pulse LED
Pulses the LED with a smooth breathing effect.

```python
pulse_led(speed=20, min_duty=0, max_duty=1023, times=1)
```

- `speed`: Controls the speed of the pulse (lower values = slower, more gradual pulse, default: 20)
  - Smaller numbers (e.g., 5) = slower, smoother pulse
  - Larger numbers (e.g., 50) = faster, more abrupt pulse
- `min_duty`: Minimum brightness (0-1023, default: 0)
- `max_duty`: Maximum brightness (0-1023, default: 1023)
- `times`: Number of times to repeat the pulse (default: 1)

Example:
```python
# Slow, smooth pulse (speed=5) that repeats 3 times
pulse_led(speed=5, times=3)

# Faster pulse (speed=30) with dimmer minimum brightness
pulse_led(speed=30, min_duty=100, max_duty=1023, times=5)
```

## MCP Configuration

To integrate this ESP32 controller with Windsurf, add the following entry to your `mcp_config.json` file (typically located at `~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "ESP32-LED-Controller": {
      "command": "python3",
      "args": [
        "/path/to/your/MCP-Demo-ESP32/server/esp32_mcp_server.py"
      ]
    }
  }
}
```

Make sure to update the path to the `esp32_mcp_server.py` file to match your system's directory structure.

## Setup Instructions

### 1. ESP32 Setup

1. Open the '`esp32_firmware_micropython/main.py`' file in an editor
2. Update the WiFi credentials with your network information:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";      // Replace with your WiFi SSID
   const char* password = "YOUR_WIFI_PASSWORD";  // Replace with your WiFi password
   ```
3. Connect your ESP32 to your computer
4. Install rshell with `pip install rshell`
5. Connect to your ESP32 with `rshell -p /dev/ttyUSB0`
6. Upload the main.py with `cp main.py /main.py`
7. Exit rshell with `exit`


### 2. MCP Server Setup

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
2. The default ESP32 IP is set to `192.168.2.150`. Update this in the server code or use environment variables:
   ```bash
   export ESP32_IP=your_esp32_ip
   export ESP32_PORT=80
   ```

## Using the MCP Server

The MCP server provides the following tools:

- `turn_led_on()` - Turns on the LED on the ESP32
- `turn_led_off()` - Turns off the LED on the ESP32
- `blink_led(count=3, interval_ms=200)` - Blinks the LED a specified number of times with given interval
- `flash_morse_code(message, dot_duration=100, dash_duration=300, element_gap=100, letter_gap=300, word_gap=700)` - Flashes a message in Morse code using the LED
- `get_esp32_status()` - Gets the current status of the ESP32 (LED state, uptime, IP)
- `get_memory_usage()` - Gets detailed memory usage statistics
- `get_storage_info()` - Gets filesystem storage information
- `restart_device()` - Restarts the ESP32 device
- `set_esp32_ip(ip, port=80)` - Sets the IP address and port of the ESP32


## Notes

1. if you setup the mcp config.json file in the .codeium/windsurf directory, the tools should work after windsurf UI loads. you then can use the mcp tools to control the ESP32.


## Environment Variables

- `ESP32_IP`: IP address of the ESP32 (default: 192.168.2.150)
- `ESP32_PORT`: Port of the ESP32 web server (default: 80)

## Dependencies

- Python 3.7+
- fastmcp
- requests
- pydantic
- typing-extensions
- python-dotenv

## License

This project is open source and available under the [MIT License](LICENSE).