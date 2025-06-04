from fastmcp import FastMCP
import requests
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import os
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("ESP32-LED-Controller")

# Configuration
ESP32_IP = os.getenv("ESP32_IP", "192.168.2.150")  # Your ESP32's IP
ESP32_PORT = int(os.getenv("ESP32_PORT", "80"))
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
mock_led_state = False

@mcp.tool()
def blink_led(count: int = 3, interval_ms: int = 200) -> Dict[str, Any]:
    """Blink the ESP32 LED a number of times with a specified interval (ms)."""
    endpoint = f"led/blink?count={count}&interval={interval_ms}"
    return call_esp32(endpoint)

@mcp.tool()
def restart_device() -> Dict[str, Any]:
    """Restart the ESP32 device."""
    endpoint = "restart"
    try:
        # The ESP32 will restart immediately after sending the response,
        # so we use a shorter timeout and handle the potential connection reset
        response = requests.get(
            f"http://{ESP32_IP}:{ESP32_PORT}/{endpoint}",
            timeout=2
        )
        # This line will only be reached if the device doesn't restart immediately
        return {"success": True, "message": response.text.strip()}
    except requests.exceptions.RequestException as e:
        # If the device restarts, the connection will be reset
        if "Connection reset" in str(e) or "Connection aborted" in str(e):
            return {"success": True, "message": "Device is restarting..."}
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_memory_usage() -> Dict[str, Any]:
    """Get memory usage statistics from the ESP32."""
    endpoint = "memory"
    try:
        response = requests.get(
            f"http://{ESP32_IP}:{ESP32_PORT}/{endpoint}",
            timeout=5
        )
        response.raise_for_status()
        memory_data = response.json()
        
        # Format the response for better readability
        return {
            "success": True,
            "memory": {
                "free": f"{memory_data['free']:,} bytes",
                "allocated": f"{memory_data['allocated']:,} bytes",
                "total": f"{memory_data['total']:,} bytes",
                "free_percent": f"{memory_data['free_percent']}%",
                "fragmentation": f"{memory_data['fragmentation']}%"
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def get_storage_info() -> Dict[str, Any]:
    """Get storage information from the ESP32's filesystem."""
    endpoint = "storage"
    try:
        response = requests.get(
            f"http://{ESP32_IP}:{ESP32_PORT}/{endpoint}",
            timeout=5
        )
        response.raise_for_status()
        storage_data = response.json()
        
        # Helper function to format bytes
        def format_bytes(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} TB"
        
        # Format the response to match ESP32's format
        return {
            "success": True,
            "storage": {
                "total_bytes": storage_data['total_bytes'],
                "used_bytes": storage_data['used_bytes'],
                "free_bytes": storage_data['free_bytes'],
                "used_percent": storage_data['used_percent']
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def call_esp32(endpoint: str) -> Dict[str, Any]:
    """Helper function to make HTTP requests to the ESP32"""
    if MOCK_MODE:
        logger.info(f"[MOCK] Would call: {endpoint}")
        return {"success": True, "message": f"Mock call to {endpoint}"}
    
    url = f"http://{ESP32_IP}:{ESP32_PORT}/{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return {"success": True, "message": response.text.strip()}
    except Exception as e:
        logger.error(f"Error calling ESP32: {str(e)}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def turn_led_on() -> Dict[str, Any]:
    """Turn on the LED on the ESP32 device."""
    global mock_led_state
    logger.info("Turning LED ON")
    
    if MOCK_MODE:
        mock_led_state = True
        return {"success": True, "message": "LED turned ON (mock mode)"}
    
    return call_esp32("led/on")

@mcp.tool()
def pulse_led(speed: int = 20, min_duty: int = 0, max_duty: int = 1023, times: int = 1) -> Dict[str, Any]:
    """Pulse the LED with a smooth breathing effect.
    
    Args:
        speed: Controls the speed of the pulse (lower is faster, default: 20)
        min_duty: Minimum brightness (0-1023, default: 0)
        max_duty: Maximum brightness (0-1023, default: 1023)
    """
    logger.info(f"Starting LED pulse with speed={speed}, min={min_duty}, max={max_duty}")
    
    if MOCK_MODE:
        return {"success": True, "message": f"LED pulsing with speed {speed} (mock mode)"}
    
    # Pass through the times parameter to the ESP32
    endpoint = f"led/pulse?speed={speed}&min={min_duty}&max={max_duty}&times={times}"
    return call_esp32(endpoint)

@mcp.tool()
def turn_led_off() -> Dict[str, Any]:
    """Turn off the LED on the ESP32 device."""
    global mock_led_state
    logger.info("Turning LED OFF")
    
    if MOCK_MODE:
        mock_led_state = False
        return {"success": True, "message": "LED turned OFF (mock mode)"}
    
    return call_esp32("led/off")

@mcp.tool()
def get_esp32_status() -> Dict[str, Any]:
    """Get the current status of the ESP32 device."""
    logger.info("Getting ESP32 status")
    
    if MOCK_MODE:
        return {
            "success": True,
            "status": {
                "led_state": "ON" if mock_led_state else "OFF",
                "mode": "MOCK",
                "ip_address": ESP32_IP,
                "port": ESP32_PORT
            }
        }
    
    return call_esp32("status")

class IPConfig(BaseModel):
    ip: str
    port: Optional[int] = 80

@mcp.tool()
def set_esp32_ip(ip: str, port: int = 80) -> Dict[str, Any]:
    """Set the IP address and port of the ESP32 device."""
    global ESP32_IP, ESP32_PORT
    ESP32_IP = ip
    ESP32_PORT = port
    
    logger.info(f"ESP32 IP set to {ESP32_IP}:{ESP32_PORT}")
    return {
        "success": True,
        "message": f"ESP32 IP address set to {ESP32_IP}:{ESP32_PORT}"
    }


@mcp.tool()
def flash_morse_code(
    message: str = Field(..., description="Text message to flash in Morse code"),
    dot_duration: int = Field(100, description="Duration of a dot in milliseconds (default: 100)"),
    dash_duration: int = Field(300, description="Duration of a dash in milliseconds (default: 300)"),
    element_gap: int = Field(100, description="Gap between elements in milliseconds (default: 100)"),
    letter_gap: int = Field(300, description="Gap between letters in milliseconds (default: 300)"),
    word_gap: int = Field(700, description="Gap between words in milliseconds (default: 700)")
) -> Dict[str, Any]:
    """Flash a message in Morse code using the ESP32's LED.
    
    Args:
        message: The text message to flash in Morse code
        dot_duration: Duration of a dot in milliseconds (default: 100)
        dash_duration: Duration of a dash in milliseconds (default: 300)
        element_gap: Gap between elements of the same letter (default: 100)
        letter_gap: Gap between letters (default: 300)
        word_gap: Gap between words (default: 700)
    """
    logger.info(f"Flashing Morse code: {message}")
    
    if MOCK_MODE:
        return {
            "success": True, 
            "message": f"Would flash Morse code: {message} (mock mode)",
            "dot_duration": dot_duration,
            "dash_duration": dash_duration,
            "element_gap": element_gap,
            "letter_gap": letter_gap,
            "word_gap": word_gap
        }
    
    try:
        # Encode the message for URL
        encoded_message = urllib.parse.quote_plus(message)
        
        # Build the endpoint URL with parameters
        endpoint = (
            f"morse?message={encoded_message}"
            f"&dot={dot_duration}"
            f"&dash={dash_duration}"
            f"&element_gap={element_gap}"
            f"&letter_gap={letter_gap}"
            f"&word_gap={word_gap}"
        )
        
        # Call the ESP32
        return call_esp32(endpoint)
    except Exception as e:
        logger.error(f"Error flashing Morse code: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    logger.info("Starting ESP32 LED Controller MCP Server")
    logger.info(f"Default ESP32 IP: {ESP32_IP}:{ESP32_PORT}")
    logger.info("Server starting...")
    
    # Start the MCP server
    mcp.run()