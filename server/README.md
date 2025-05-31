# ESP32 LED Controller MCP Server

This MCP (Model Context Protocol) server provides a bridge between Windsurf and an ESP32 device running MicroPython. It allows you to control an LED and monitor system resources on the ESP32 through a simple API.

## Overview

The server is built using FastMCP and provides the following functionality:
- Control the built-in LED (on/off/blink)
- Monitor system resources (memory usage, storage)
- Restart the ESP32 device
- Configure the ESP32's IP address

## Requirements

- Python 3.7+
- Packages listed in `requirements.txt`
- An ESP32 device running the MicroPython firmware (from the `esp32_firmware_micropython` directory)

## Configuration

Server behavior can be configured using environment variables:

- `ESP32_IP`: IP address of the ESP32 (default: `192.168.2.150`)
- `ESP32_PORT`: Port of the ESP32 web server (default: `80`)
- `MOCK_MODE`: Set to `true` to enable mock mode for testing without hardware (default: `false`)

## Available Tools

### LED Control

- `turn_led_on()`: Turn on the LED
- `turn_led_off()`: Turn off the LED
- `blink_led(count=3, interval_ms=200)`: Blink the LED a specified number of times with a given interval

### System Information

- `get_esp32_status()`: Get current status (LED state, uptime, IP address)
- `get_memory_usage()`: Get detailed memory usage statistics
- `get_storage_info()`: Get filesystem storage information

### Device Management

- `restart_device()`: Restart the ESP32
- `set_esp32_ip(ip, port=80)`: Update the ESP32's IP address configuration

## Code Structure

### Main Components

1. **MCP Server Initialization**
   - Sets up logging and configuration
   - Creates a FastMCP instance with the name "ESP32-LED-Controller"

2. **Helper Functions**
   - `call_esp32(endpoint)`: Makes HTTP requests to the ESP32
   - `format_bytes(size_bytes)`: Helper to format byte sizes for display

3. **Tool Functions**
   - Each tool is decorated with `@mcp.tool()`
   - Tools make HTTP requests to the ESP32's web server
   - Responses are formatted for better readability

4. **Error Handling**
   - Comprehensive error handling for network issues
   - Graceful handling of device restarts

## Usage Example

```python
# Example of using the MCP server programmatically
from esp32_mcp_server import (
    turn_led_on,
    turn_led_off,
    get_esp32_status
)

# Turn on the LED
result = turn_led_on()
print(result)

# Get device status
status = get_esp32_status()
print(status)
```

## Testing with Mock Mode

To test without an actual ESP32 device, set the `MOCK_MODE` environment variable:

```bash
export MOCK_MODE=true
python esp32_mcp_server.py
```

In mock mode, LED state changes will be simulated in memory.

## Error Handling

The server includes robust error handling for:
- Network timeouts
- Connection errors
- Invalid responses
- Device restarts

## Logging

Logs are output to stdout with timestamps and log levels. The log level can be adjusted by modifying the `logging.basicConfig` call in the code.

## Security Considerations

- The server makes unauthenticated HTTP requests to the ESP32
- Ensure your ESP32 is on a trusted network
- Consider adding authentication if exposing the ESP32 to untrusted networks

## Dependencies

- `fastmcp`: For the MCP server implementation
- `requests`: For making HTTP requests to the ESP32
- `pydantic`: For data validation
- `python-dotenv`: For loading environment variables (optional)

## License

This project is open source and available under the MIT License.
