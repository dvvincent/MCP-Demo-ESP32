import machine
import time
import network
import _thread
import collections

# WiFi credentials
SSID = "NETGEAR25"
PASSWORD = "hotdogfingers"

# Command queue for LED operations
cmd_queue = collections.deque((), 20)  # Max 20 commands in queue
queue_lock = _thread.allocate_lock()
queue_running = False

# Morse code dictionary
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ',': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-',
    '(': '-.--.', ')': '-.--.-', ' ': '/', "'": '.----.', ':': '---...',
    ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.', '!': '-.-.--', '&': '.-...'
}

# Timing constants (in milliseconds)
DOT_DURATION = 100      # Duration of a dot
DASH_DURATION = 300     # Duration of a dash (3x dot)
ELEMENT_GAP = 100       # Gap between elements of the same letter (1x dot)
LETTER_GAP = 300        # Gap between letters (3x dot)
WORD_GAP = 700          # Gap between words (7x dot)

# Set up the LED with PWM for smooth fading
led_pin = machine.Pin(2, machine.Pin.OUT)
led_pwm = machine.PWM(led_pin, freq=1000)  # 1kHz PWM frequency
led_pwm.duty(0)  # Start with LED off
led_state = False

def set_led(on):
    """Turn LED on or off"""
    global led_state
    led_state = on
    led_pwm.duty(1023 if on else 0)

# Command types
CMD_LED_ON = 1
CMD_LED_OFF = 2
CMD_MORSE = 3
CMD_BLINK = 4
CMD_PULSE = 5

def process_queue_thread():
    """Thread function to process the command queue"""
    global queue_running
    
    print("Command queue processor started")
    queue_running = True
    
    while True:
        # Check if there are commands in the queue
        if len(cmd_queue) > 0:
            # Get command from queue with thread safety
            with queue_lock:
                if len(cmd_queue) > 0:  # Check again inside lock
                    cmd = cmd_queue.popleft()
                else:
                    continue
            
            # Process the command
            cmd_type = cmd[0]
            
            if cmd_type == CMD_LED_ON:
                print("Processing: LED ON")
                _set_led_direct(True)
            
            elif cmd_type == CMD_LED_OFF:
                print("Processing: LED OFF")
                _set_led_direct(False)
            
            elif cmd_type == CMD_MORSE:
                print("Processing: Morse Code")
                text, params = cmd[1], cmd[2]
                _flash_morse_code_direct(
                    text, 
                    params.get('dot_duration', 100),
                    params.get('dash_duration', 300),
                    params.get('element_gap', 100),
                    params.get('letter_gap', 300),
                    params.get('word_gap', 700)
                )
            
            elif cmd_type == CMD_BLINK:
                print("Processing: Blink")
                count, interval = cmd[1], cmd[2]
                _blink_led_direct(count, interval)
            
            elif cmd_type == CMD_PULSE:
                print("Processing: Pulse")
                speed, min_duty, max_duty, times = cmd[1], cmd[2], cmd[3], cmd[4]
                _pulse_led_direct(speed, min_duty, max_duty, times)
        
        # Small delay to prevent tight loop
        time.sleep_ms(10)

def _set_led_direct(on):
    """Direct LED control without queuing"""
    global led_state
    led_state = on
    led_pwm.duty(1023 if on else 0)

def set_led(on):
    """Queue an LED on/off command"""
    with queue_lock:
        cmd_queue.append((CMD_LED_ON if on else CMD_LED_OFF,))
    return True

def _flash_morse_code_direct(text, dot_duration=100, dash_duration=300, 
                          element_gap=100, letter_gap=300, word_gap=700):
    """Direct Morse code flashing without queuing"""
    print("Flashing Morse code:", text)
    # Convert text to uppercase since our dictionary uses uppercase keys
    text = text.upper()
    
    for char in text:
        print("Processing character:", char)
        if char == ' ':
            # Gap between words
            print("Word gap:", word_gap, "ms")
            time.sleep_ms(word_gap)
            continue
            
        if char in MORSE_CODE_DICT:
            code = MORSE_CODE_DICT[char]
            print(char + ":", code)
            
            # Flash each element of the Morse code
            for i, element in enumerate(code):
                print(" " + element, end='')
                led_pwm.duty(1023)  # Turn on LED
                if element == '.':
                    time.sleep_ms(dot_duration)
                else:  # dash
                    time.sleep_ms(dash_duration)
                led_pwm.duty(0)  # Turn off LED
                if i < len(code) - 1:  # Don't add gap after last element
                    time.sleep_ms(element_gap)
            print()  # New line after each character
            
            # Gap between letters
            time.sleep_ms(letter_gap)
    
    # Ensure LED is off after finishing
    led_pwm.duty(0)
    print("Morse code complete")

def flash_morse_code(text, dot_duration=100, dash_duration=300, 
                   element_gap=100, letter_gap=300, word_gap=700):
    """Queue a Morse code command"""
    params = {
        'dot_duration': dot_duration,
        'dash_duration': dash_duration,
        'element_gap': element_gap,
        'letter_gap': letter_gap,
        'word_gap': word_gap
    }
    
    with queue_lock:
        cmd_queue.append((CMD_MORSE, text, params))
    
    return True

def _pulse_led_direct(speed=20, min_duty=0, max_duty=1023, times=1):
    """Direct LED pulsing without queuing"""
    for _ in range(times):
        # Fade in
        for duty in range(min_duty, max_duty, speed):
            led_pwm.duty(duty)
            time.sleep_ms(10)
        # Fade out
        for duty in range(max_duty, min_duty, -speed):
            led_pwm.duty(duty)
            time.sleep_ms(10)
    led_pwm.duty(0)  # Turn off after pulsing

def pulse_led(speed=20, min_duty=0, max_duty=1023, times=1):
    """Queue an LED pulse command
    
    Args:
        speed: Controls the speed of the pulse (lower is faster)
        min_duty: Minimum brightness (0-1023)
        max_duty: Maximum brightness (0-1023)
        times: Number of times to repeat the pulse
    """
    with queue_lock:
        cmd_queue.append((CMD_PULSE, speed, min_duty, max_duty, times))
    return True

def _blink_led_direct(count=3, interval_ms=200):
    """Direct LED blinking without queuing"""
    for _ in range(count):
        led_pwm.duty(1023)  # On
        time.sleep_ms(interval_ms // 2)
        led_pwm.duty(0)     # Off
        time.sleep_ms(interval_ms // 2)
    
    # Restore previous state
    if led_state:
        led_pwm.duty(1023)
    else:
        led_pwm.duty(0)

def blink_led(count=3, interval_ms=200):
    """Queue an LED blink command
    
    Args:
        count: Number of times to blink
        interval_ms: Duration of each blink in milliseconds
    """
    with queue_lock:
        cmd_queue.append((CMD_BLINK, count, interval_ms))
    return True

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(SSID, PASSWORD)
        
        # Wait for connection with timeout
        timeout = 0
        while not wlan.isconnected() and timeout < 20:  # 10 second timeout
            print('Waiting for connection...')
            time.sleep(0.5)
            timeout += 1
    
    if wlan.isconnected():
        print('Network config:', wlan.ifconfig())
        return wlan.ifconfig()[0]
    else:
        print('Failed to connect to WiFi')
        return None

def start_web_server():
    import socket
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(5)
    
    print('Web server started on http://' + ip)
    
    while True:
        try:
            conn, addr = s.accept()
            request = conn.recv(1024).decode('utf-8')
            
            # Handle LED control
            if 'GET /led/on' in request:
                set_led(True)
                response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED ON'
            elif 'GET /led/off' in request:
                set_led(False)
                response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED OFF'
            elif 'GET /morse' in request:
                # Extract message from request
                msg_start = request.find('message=') + 8
                if msg_start > 7:
                    msg_end = request.find(' ', msg_start)
                    if msg_end == -1:  # If no space after message
                        msg_end = len(request)
                    message = request[msg_start:msg_end].split('&')[0]
                    message = message.replace('+', ' ')
                    
                    # Extract optional parameters
                    params = {}
                    param_names = ['dot', 'dash', 'element_gap', 'letter_gap', 'word_gap']
                    for param in param_names:
                        param_start = request.find(param + '=')
                        if param_start > -1:
                            param_start += len(param) + 1
                            param_end = request.find('&', param_start)
                            if param_end == -1:
                                param_end = request.find(' ', param_start)
                            if param_end == -1:
                                param_end = len(request)
                            try:
                                params[param] = int(request[param_start:param_end])
                            except ValueError:
                                pass
                    
                    # Queue the Morse code command (non-blocking)
                    flash_morse_code(
                        message,
                        dot_duration=params.get('dot', 100),
                        dash_duration=params.get('dash', 300),
                        element_gap=params.get('element_gap', 100),
                        letter_gap=params.get('letter_gap', 300),
                        word_gap=params.get('word_gap', 700)
                    )
                    response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nMorse code queued'
                else:
                    response = 'HTTP/1.1 400 Bad Request\nContent-Type: text/plain\n\nMissing message parameter'
            elif 'GET /storage' in request:
                # Get storage information
                import os
                try:
                    # Get filesystem stats
                    fs_stat = os.statvfs('/')
                    block_size = fs_stat[0]
                    total_blocks = fs_stat[2]
                    free_blocks = fs_stat[3]
                    
                    total_space = block_size * total_blocks
                    free_space = block_size * free_blocks
                    used_space = total_space - free_space
                    
                    # Create JSON response
                    storage_json = {
                        "total_bytes": total_space,
                        "used_bytes": used_space,
                        "free_bytes": free_space,
                        "used_percent": round((used_space / total_space) * 100, 1) if total_space > 0 else 0
                    }
                    
                    import json
                    json_response = json.dumps(storage_json)
                    response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json_response
                except Exception as e:
                    response = 'HTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\n\nError: ' + str(e)
            elif 'GET /memory' in request:
                # Get memory information
                import gc
                try:
                    # Force garbage collection to get accurate numbers
                    gc.collect()
                    
                    # Get memory stats
                    free = gc.mem_free()
                    allocated = gc.mem_alloc()
                    total = free + allocated
                    
                    # Calculate fragmentation
                    # Higher fragmentation means memory is more scattered
                    fragmentation = 0
                    if total > 0:
                        fragmentation = round((1 - (free / total)) * 100, 1)
                    
                    # Create JSON response
                    memory_json = {
                        "free": free,
                        "allocated": allocated,
                        "total": total,
                        "free_percent": round((free / total) * 100, 1) if total > 0 else 0,
                        "fragmentation": fragmentation
                    }
                    
                    import json
                    json_response = json.dumps(memory_json)
                    response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json_response
                except Exception as e:
                    response = 'HTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\n\nError: ' + str(e)
            elif 'GET /status' in request:
                # Get system status information
                try:
                    import json
                    import time
                    
                    # Get queue information
                    with queue_lock:
                        queue_length = len(cmd_queue)
                        queue_is_running = queue_running
                    
                    # Create JSON response with system status
                    status_json = {
                        "uptime_seconds": time.time(),
                        "queue_length": queue_length,
                        "queue_running": queue_is_running,
                        "led_state": led_state,
                        "wifi_connected": network.WLAN(network.STA_IF).isconnected(),
                        "ip_address": network.WLAN(network.STA_IF).ifconfig()[0]
                    }
                    
                    json_response = json.dumps(status_json)
                    response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json_response
                except Exception as e:
                    response = 'HTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\n\nError: ' + str(e)
            else:
                response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\nEndpoint not found'
                
            conn.send(response.encode('utf-8'))
            conn.close()
        except Exception as e:
            print('Error handling request:', e)

# Main execution
print("Starting ESP32...")
ip = connect_wifi()

# Start the command queue processor thread
print("Starting command queue processor...")
_thread.start_new_thread(process_queue_thread, ())

# Wait for the queue processor to start
time.sleep(0.5)

# Simple test sequence
print("Testing LED...")
set_led(True)
time.sleep(1)
set_led(False)
time.sleep(0.5)

print("Testing pulse...")
pulse_led(times=2)
time.sleep(1)

print("Testing Morse code...")
flash_morse_code("SOS")

# Start the web server
print("Starting web server...")
start_web_server()