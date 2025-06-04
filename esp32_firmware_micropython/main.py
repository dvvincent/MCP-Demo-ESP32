import machine
import time
import network
import _thread

# WiFi credentials
SSID = "SSID"
PASSWORD = "PASSWORD"

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

def flash_morse_code(text, dot_duration=100, dash_duration=300, 
                   element_gap=100, letter_gap=300, word_gap=700):
    """Flash the LED to display Morse code for the given text.
    
    Args:
        text: Text to convert to Morse code
        dot_duration: Duration of a dot in milliseconds (default: 100)
        dash_duration: Duration of a dash in milliseconds (default: 300)
        element_gap: Gap between elements of the same letter (default: 100)
        letter_gap: Gap between letters (default: 300)
        word_gap: Gap between words (default: 700)
    """
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

def pulse_led(speed=20, min_duty=0, max_duty=1023, times=1):
    """Pulse the LED with a smooth breathing effect.
    
    Args:
        speed: Controls the speed of the pulse (lower is faster)
        min_duty: Minimum brightness (0-1023)
        max_duty: Maximum brightness (0-1023)
        times: Number of times to repeat the pulse
    """
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

def blink_led(count=3, interval_ms=200):
    """Blink the LED a specified number of times.
    
    Args:
        count: Number of times to blink
        interval_ms: Duration of each blink in milliseconds
    """
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
                    message = request[msg_start:msg_end].split('&')[0]
                    message = message.replace('+', ' ')
                    flash_morse_code(message)
                    response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nMorse code started'
                else:
                    response = 'HTTP/1.1 400 Bad Request\nContent-Type: text/plain\n\nMissing message parameter'
            else:
                response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\nEndpoint not found'
                
            conn.send(response.encode('utf-8'))
            conn.close()
        except Exception as e:
            print('Error handling request:', e)

# Main execution
print("Starting ESP32...")
ip = connect_wifi()

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