import machine
import socket
import json
import time
import network
import gc
import _thread

# WiFi credentials
SSID = "SSID"
PASSWORD = "PASSWORD"

# Set up the LED with PWM for smooth fading
led_pin = machine.Pin(2, machine.Pin.OUT)
led_pwm = machine.PWM(led_pin, freq=1000)  # 1kHz PWM frequency
led_pwm.duty(0)  # Start with LED off
led_state = False

def pulse_led(speed=20, min_duty=0, max_duty=1023, times=1):
    """Pulse the LED with a smooth breathing effect.
    
    Args:
        speed: Controls the speed of the pulse (lower is faster)
        min_duty: Minimum brightness (0-1023)
        max_duty: Maximum brightness (0-1023)
        times: Number of times to repeat the pulse (0 = infinite)
    """
    global led_state
    count = 0
    while times == 0 or count < times:
        # Fade in
        for i in range(min_duty, max_duty, speed):
            led_pwm.duty(i)
            time.sleep_ms(10)
        # Fade out
        for i in range(max_duty, min_duty, -speed):
            led_pwm.duty(i)
            time.sleep_ms(10)
        count += 1
    # Ensure LED returns to previous state
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
            timeout += 1
            time.sleep(0.5)
            print('Waiting for connection...')
    
    if wlan.isconnected():
        print('Network config:', wlan.ifconfig())
        return wlan.ifconfig()[0]
    else:
        print('Could not connect to WiFi')
        return None

def parse_query_params(request):
    # Extract query string from request
    query = ''
    if '?' in request:
        query = request.split('?', 1)[1].split(' ', 1)[0]
    
    # Parse query parameters
    params = {}
    for pair in query.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key] = value
        elif pair:  # Handle parameters without values
            params[pair] = ''
    
    return params

def handle_request(conn):
    global led_state
    request = conn.recv(1024).decode('utf-8')
    
    # Simple request parsing
    if 'GET / HTTP' in request:
        # Serve a simple web interface with inline status
        # Get current status
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        total_mem = free_mem + alloc_mem
        
        status = {
            'led_state': 'ON' if led_state else 'OFF',
            'uptime_seconds': time.time(),
            'ip_address': get_ip_address() or 'Not connected'
        }
        
        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 LED Controller</title>
    <style>
        /* Tailwind-inspired styles - Dark Mode */
        :root {{
            --primary: #3b82f6;
            --primary-dark: #2563eb;
            --primary-light: #60a5fa;
            --success: #10b981;
            --success-dark: #059669;
            --success-light: #34d399;
            --danger: #ef4444;
            --danger-dark: #dc2626;
            --danger-light: #f87171;
            --warning: #f59e0b;
            --warning-dark: #d97706;
            --warning-light: #fbbf24;
            --dark-50: #18181b;
            --dark-100: #27272a;
            --dark-200: #3f3f46;
            --dark-300: #52525b;
            --dark-400: #71717a;
            --dark-500: #a1a1aa;
            --dark-600: #d4d4d8;
            --dark-700: #e4e4e7;
            --dark-800: #f4f4f5;
            --dark-900: #fafafa;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--dark-50);
            color: var(--dark-700);
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 640px;
            margin: 0 auto;
            padding: 1.5rem;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .title {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark-800);
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            font-size: 1rem;
            color: var(--dark-500);
        }}
        
        .card {{
            background-color: var(--dark-100);
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--dark-200);
        }}
        
        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--dark-700);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--dark-300);
        }}
        
        .button-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}
        
        .button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: white;
            background-color: var(--primary);
            border-radius: 0.375rem;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            min-width: 100px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }}
        
        .button:hover {{
            background-color: var(--primary-light);
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
        }}
        
        .button:active {{
            transform: translateY(0);
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }}
        
        .button.success {{
            background-color: var(--success);
        }}
        
        .button.success:hover {{
            background-color: var(--success-light);
        }}
        
        .button.danger {{
            background-color: var(--danger);
        }}
        
        .button.danger:hover {{
            background-color: var(--danger-light);
        }}
        
        .button.warning {{
            background-color: var(--warning);
        }}
        
        .button.warning:hover {{
            background-color: var(--warning-light);
        }}
        
        .status-item {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--dark-200);
        }}
        
        .status-item:last-child {{
            border-bottom: none;
        }}
        
        .status-label {{
            font-weight: 500;
            color: var(--dark-500);
        }}
        
        .status-value {{
            font-weight: 400;
            color: var(--dark-700);
        }}
        
        .status-value.on {{
            color: var(--success-light);
            font-weight: 600;
        }}
        
        .status-value.off {{
            color: var(--danger-light);
            font-weight: 600;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 2rem;
            color: var(--dark-400);
            font-size: 0.875rem;
        }}
        
        .footer a {{
            color: var(--primary-light);
            text-decoration: none;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
            color: var(--primary);
        }}
        
        /* Responsive adjustments */
        @media (max-width: 640px) {{
            .button-group {{
                flex-direction: column;
            }}
            
            .button {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">ESP32 LED Controller</h1>
            <p class="subtitle">Control the onboard LED remotely</p>
        </div>
        
        <div class="card">
            <h2 class="card-title">LED Controls</h2>
            <div class="button-group">
                <a href="/led/on" class="button success">Turn ON</a>
                <a href="/led/off" class="button danger">Turn OFF</a>
            </div>
            <div class="button-group">
                <a href="/led/pulse" class="button">Pulse LED</a>
                <a href="/led/blink" class="button warning">Blink LED</a>
            </div>
        </div>
        
        <div class="card">
            <h2 class="card-title">System Status</h2>
            <div class="status-item">
                <span class="status-label">LED State:</span>
                <span class="status-value {status['led_state'].lower()}">{status['led_state']}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Uptime:</span>
                <span class="status-value">{status['uptime_seconds']} seconds</span>
            </div>
            <div class="status-item">
                <span class="status-label">IP Address:</span>
                <span class="status-value">{status['ip_address']}</span>
            </div>
            <div class="status-item">
                <span class="status-label">Free Memory:</span>
                <span class="status-value">{free_mem:,} bytes</span>
            </div>
        </div>
        
        <div class="footer">
            <p>ESP32 MicroPython Web Interface | <a href="/">Refresh</a> | <a href="/restart">Restart Device</a></p>
        </div>
    </div>
</body>
</html>
'''
        response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + html
    elif 'GET /led/on' in request:
        led_pwm.duty(1023)  # Full brightness
        led_state = True
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED ON'
    elif 'GET /led/off' in request:
        led_pwm.duty(0)  # Turn off
        led_state = False
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED OFF'
    elif 'GET /led/pulse' in request:
        # Parse optional parameters
        params = parse_query_params(request)
        speed = int(params.get('speed', '20'))
        min_duty = int(params.get('min', '0'))
        max_duty = int(params.get('max', '1023'))
        times = int(params.get('times', '1'))  # Default to 1 pulse
        
        # Start a new thread for pulsing so it doesn't block the server
        _thread.start_new_thread(pulse_led, (speed, min_duty, max_duty, times))
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED PULSING'
    elif 'GET /led/blink' in request:
        params = parse_query_params(request)
        count = int(params.get('count', '3'))
        interval = int(params.get('interval', '200'))
        
        # Define the blink function
        def blink_led(count, interval_ms):
            global led_state
            for _ in range(count):
                led_pwm.duty(1023)  # On
                time.sleep_ms(interval_ms)
                led_pwm.duty(0)  # Off
                time.sleep_ms(interval_ms)
            # Restore previous state
            if led_state:
                led_pwm.duty(1023)
            else:
                led_pwm.duty(0)
        
        # Start blinking in a new thread to avoid blocking
        _thread.start_new_thread(blink_led, (count, interval))
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED BLINKING'
    elif 'GET /status' in request:
        # Get system status
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        total_mem = free_mem + alloc_mem
        
        status = {
            'led_state': 'ON' if led_state else 'OFF',
            'uptime_seconds': time.time(),
            'ip_address': get_ip_address() or 'Not connected'
        }
        
        response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(status)
    elif 'GET /memory' in request:
        # Get memory usage
        gc.collect()  # Run garbage collection before reporting
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        total_mem = free_mem + alloc_mem
        
        memory_info = {
            'free': free_mem,
            'allocated': alloc_mem,
            'total': total_mem,
            'free_percent': f"{free_mem * 100 / total_mem:.1f}",
            'fragmentation': "0"  # Removed gc.mem_maxfree() as it's not available
        }
        
        response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(memory_info)
    elif 'GET /storage' in request:
        # Get storage information
        import os
        try:
            fs_stat = os.statvfs('/')
            block_size = fs_stat[0]
            total_blocks = fs_stat[2]
            free_blocks = fs_stat[3]
            
            total_size = block_size * total_blocks
            free_size = block_size * free_blocks
            used_size = total_size - free_size
            
            storage_info = {
                'total_bytes': total_size,
                'used_bytes': used_size,
                'free_bytes': free_size,
                'used_percent': f"{used_size * 100 / total_size:.1f}",
                'block_size': block_size,
                'total_blocks': total_blocks,
                'free_blocks': free_blocks
            }
            
            response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(storage_info)
        except Exception as e:
            response = f'HTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\n\nError: {str(e)}'
    elif 'GET /restart' in request:
        # Restart the ESP32
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nRestarting ESP32...'
        conn.send(response.encode('utf-8'))
        conn.close()
        # Import machine module for reset
        import machine
        # Wait a moment before restarting
        time.sleep(1)
        # Reset the device
        machine.reset()
    else:
        response = 'HTTP/1.1 404 Not Found\nContent-Type: text/plain\n\nEndpoint not found'
    
    conn.send(response.encode('utf-8'))
    conn.close()

def start_web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(5)
    
    ip = get_ip_address()
    if ip:
        print('Web server started on http://' + ip)
    else:
        print('Web server started but not connected to WiFi')
    
    while True:
        try:
            conn, addr = s.accept()
            handle_request(conn)
        except Exception as e:
            print('Error:', e)

def get_ip_address():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return wlan.ifconfig()[0]
    return None


# Main execution
print("Starting ESP32...")
ip = connect_wifi()
start_web_server()