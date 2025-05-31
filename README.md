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
   git clone https://github.com/yourusername/MCP-Demo-ESP32.git
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
- `get_esp32_status()` - Gets the current status of the ESP32 (LED state, uptime, IP)
- `get_memory_usage()` - Gets detailed memory usage statistics
- `get_storage_info()` - Gets filesystem storage information
- `restart_device()` - Restarts the ESP32 device
- `set_esp32_ip(ip, port=80)` - Sets the IP address and port of the ESP32

## Example Usage

1. Start the MCP server:
   ```bash
   python server/esp32_mcp_server.py
   ```

2. In another terminal, use the MCP CLI to control the LED:
   ```bash
   # Turn on the LED
   mcp tools run ESP32-LED-Controller turn_led_on
   
   # Turn off the LED
   mcp tools run ESP32-LED-Controller turn_led_off
   
   # Get ESP32 status
   mcp tools run ESP32-LED-Controller get_esp32_status
   
   # Set ESP32 IP address
   mcp tools run ESP32-LED-Controller set_esp32_ip --ip 192.168.1.100 --port 80
   ```

## Environment Variables

- `ESP32_IP`: IP address of the ESP32 (default: 192.168.2.150)
- `ESP32_PORT`: Port of the ESP32 web server (default: 80)
- `MOCK_MODE`: Set to 'true' to enable mock mode (default: false)

## Dependencies

- Python 3.7+
- fastmcp
- requests
- pydantic
- typing-extensions
- python-dotenv

## License

This project is open source and available under the [MIT License](LICENSE).