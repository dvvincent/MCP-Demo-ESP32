import machine
import socket
import json
import time
import network
import ure  # For query parsing

# Custom help function that returns help text as a string
def web_help():
    help_text = """
MicroPython Web REPL Help
-------------------------

Basic Commands:
  2+2                        - Simple arithmetic
  x = 10                     - Variable assignment
  print('hello')             - Print to output
  
Hardware Control:
  import machine             - Import hardware module
  led = machine.Pin(2, machine.Pin.OUT)  - Set up LED pin
  led.value(1)               - Turn LED on
  led.value(0)               - Turn LED off
  
System Information:
  import gc; gc.collect(); gc.mem_free()  - Show free memory
  import os; os.listdir()    - List files
  
Network:
  import network             - Import network module
  wlan = network.WLAN(network.STA_IF)  - Get WiFi interface
  wlan.ifconfig()            - Show network config
  
Type 'modules()' to see available modules.
"""
    return help_text

# Function to list available modules
def modules():
    modules_list = [
        'gc', 'machine', 'micropython', 'network', 'os', 'time', 
        'json', 'math', 'random', 'socket', 'struct', 'sys', 'ure'
    ]
    return "Available modules:\n" + ", ".join(sorted(modules_list))

# WiFi credentials
SSID = "SSID"
PASSWORD = "PASSWORD"

# Set up the LED pin (built-in LED on most ESP32 boards)
led_pin = machine.Pin(2, machine.Pin.OUT)
led_state = False

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(SSID, PASSWORD)
        
        # Wait for connection with timeout
        max_wait = 20
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)
        
    if wlan.isconnected():
        print('Connected to WiFi')
        print('Network config:', wlan.ifconfig())
        return wlan.ifconfig()[0]
    else:
        print('Could not connect to WiFi')
        return None

import ure  # For query parsing

def parse_query_params(request):
    params = {}
    try:
        # Find the query string between GET /path? and HTTP
        parts = request.split(' ')
        if len(parts) > 1:
            path_with_query = parts[1]
            if '?' in path_with_query:
                query = path_with_query.split('?')[1]
                for pair in query.split('&'):
                    if '=' in pair:
                        k, v = pair.split('=', 1)
                        params[k] = v
    except Exception as e:
        print("Query parse error:", e)
    return params

# Simple function to execute a command and return the result
def execute_command(command):
    try:
        # Handle special commands
        command = command.strip()
        if command == 'help()':
            return web_help()
        if command == 'modules()':
            return modules()
            
        result = None
        try:
            # Try to evaluate as an expression first
            result = eval(command)
        except SyntaxError:
            # If it's not an expression, execute as a statement
            try:
                exec(command)
            except Exception as e:
                return "Error: " + str(e)
        except Exception as e:
            return "Error: " + str(e)
            
        # Safely convert result to string to avoid recursion issues
        if result is not None:
            try:
                # For complex objects, just show their type
                if isinstance(result, (dict, list, tuple)) and len(str(result)) > 1000:
                    return f"{type(result).__name__} with {len(result)} items"
                # For other objects, use a simple string representation
                return str(result)
            except Exception:
                return f"<{type(result).__name__} object>"
        return "Command executed successfully"
    except Exception as e:
        return "Error: " + str(e)

def handle_request(conn):
    global led_state
    request = conn.recv(1024).decode('utf-8')
    
    # Execute REPL command
    if 'GET /execute' in request:
        params = parse_query_params(request)
        command = params.get('cmd', '')
        
        # URL decode the command
        try:
            import ure
            # Simple URL decoding
            command = command.replace('+', ' ')
            # Handle percent encoding
            parts = command.split('%')
            if len(parts) > 1:
                result = parts[0]
                for part in parts[1:]:
                    if len(part) >= 2:
                        try:
                            char_code = int(part[:2], 16)
                            result += chr(char_code) + part[2:]
                        except:
                            result += '%' + part
                    else:
                        result += '%' + part
                command = result
        except:
            pass
            
        if command:
            # Execute the command directly without using the execute_command function
            try:
                # Try to evaluate as expression first
                try:
                    result = eval(command)
                    if result is not None:
                        if isinstance(result, (list, dict, tuple)) and len(str(result)) > 500:
                            response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n{type(result).__name__} with {len(result)} items'
                        else:
                            response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\n{str(result)}'
                    else:
                        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nCommand executed (no output)'
                except SyntaxError:
                    # If not an expression, try as a statement
                    try:
                        exec(command)
                        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nCommand executed successfully'
                    except Exception as e:
                        response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nError: {str(e)}'
                except Exception as e:
                    response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nError: {str(e)}'
            except Exception as e:
                response = f'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nInternal error: {str(e)}'
        else:
            response = 'HTTP/1.1 400 Bad Request\nContent-Type: text/plain\n\nMissing command parameter'
    
    # Simple request parsing
    elif 'GET /led/on' in request:
        led_pin.value(1)
        led_state = True
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED ON'
    elif 'GET /led/off' in request:
        led_pin.value(0)
        led_state = False
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nLED OFF'
    elif request.startswith('GET /led/blink'):
        params = parse_query_params(request)
        count = int(params.get('count', 3))
        interval = int(params.get('interval', 200))
        for _ in range(count):
            led_pin.value(1)
            time.sleep_ms(interval)
            led_pin.value(0)
            time.sleep_ms(interval)
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nBlinked {} times with {}ms interval'.format(count, interval)
    elif 'GET /restart' in request:
        response = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nRestarting device...'
        conn.send(response.encode('utf-8'))
        conn.close()
        machine.reset()
        return
    elif 'GET /status' in request:
        status = {
            'led_state': 'ON' if led_state else 'OFF',
            'uptime_seconds': time.time(),
            'ip_address': get_ip_address()
        }
        response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(status)
    elif 'GET /memory' in request:
        import gc
        import micropython
        gc.collect()  # Run garbage collection before measuring
        mem_info = {
            'free': gc.mem_free(),
            'allocated': gc.mem_alloc(),
            'total': gc.mem_free() + gc.mem_alloc(),
            'free_percent': round(gc.mem_free() / (gc.mem_free() + gc.mem_alloc()) * 100, 1),
            'fragmentation': 100 - (gc.mem_free() * 100 // (gc.mem_free() + gc.mem_alloc()))
        }
        response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(mem_info)
    elif 'GET /storage' in request:
        import os
        try:
            fs_stat = os.statvfs('/')
            block_size = fs_stat[0]  # Filesystem block size
            total_blocks = fs_stat[2]  # Total blocks
            free_blocks = fs_stat[3]  # Free blocks
            
            total_bytes = block_size * total_blocks
            free_bytes = block_size * free_blocks
            used_bytes = total_bytes - free_bytes
            
            storage_info = {
                'total_bytes': total_bytes,
                'free_bytes': free_bytes,
                'used_bytes': used_bytes,
                'used_percent': round((used_bytes / total_bytes) * 100, 1) if total_bytes > 0 else 0,
                'block_size': block_size,
                'total_blocks': total_blocks,
                'free_blocks': free_blocks
            }
            response = 'HTTP/1.1 200 OK\nContent-Type: application/json\n\n' + json.dumps(storage_info)
        except Exception as e:
            response = 'HTTP/1.1 500 Internal Server Error\nContent-Type: application/json\n\n' + json.dumps({'error': str(e)})
    elif 'GET /repl' in request:
        # Serve the REPL terminal page with AJAX instead of WebSockets
        html = """<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 REPL Terminal</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        #terminal {
            font-family: monospace;
            background-color: #1e1e1e;
            color: #f0f0f0;
            padding: 10px;
            overflow-y: auto;
            height: 400px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        #input {
            font-family: monospace;
            background-color: #1e1e1e;
            color: #f0f0f0;
            border: none;
            outline: none;
            width: 100%;
            padding: 10px;
        }
        .prompt {
            color: #5af78e;
        }
        .error {
            color: #ff5c57;
        }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="mb-8">
            <div class="flex justify-between items-center">
                <h1 class="text-3xl font-bold">ESP32 REPL Terminal</h1>
                <a href="/" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">Back to Dashboard</a>
            </div>
            <p class="text-gray-600 dark:text-gray-400">Interact with MicroPython directly</p>
        </header>

        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <div id="terminal">
                <div><span class="prompt">>>></span> Welcome to MicroPython REPL on ESP32</div>
                <div>Type commands below and press Enter or click Send</div>
            </div>
            <div class="flex mt-2 border-t border-gray-200 dark:border-gray-700 pt-2">
                <input id="input" type="text" placeholder="Type MicroPython commands here..." autofocus>
                <button id="send" class="ml-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition">Send</button>
            </div>
            <div class="mt-4 text-sm text-gray-600 dark:text-gray-400">
                <p>Type <code class="bg-gray-200 dark:bg-gray-700 px-1 rounded">help()</code> for MicroPython help.</p>
            </div>
        </div>

        <div class="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Common Commands</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <button class="cmd-btn px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition text-left">
                    import machine
                </button>
                <button class="cmd-btn px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition text-left">
                    dir()
                </button>
                <button class="cmd-btn px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition text-left">
                    import gc; gc.collect(); gc.mem_free()
                </button>
                <button class="cmd-btn px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition text-left">
                    import os; os.listdir()
                </button>
            </div>
        </div>

        <footer class="mt-12 text-center text-sm text-gray-500 dark:text-gray-400">
            <p>ESP32 REPL Terminal &copy; 2025</p>
        </footer>
    </div>

    <script>
        const terminal = document.getElementById('terminal');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('send');
        
        // Execute command via AJAX
        function executeCommand(command) {
            // Add command to terminal
            terminal.innerHTML += `<div><span class="prompt">>>></span> ${command}</div>`;
            terminal.scrollTop = terminal.scrollHeight;
            
            // Send command to server
            fetch(`/execute?cmd=${encodeURIComponent(command)}`)
                .then(response => response.text())
                .then(result => {
                    // Format result with error highlighting
                    if (result.includes('Error:')) {
                        result = result.replace(/Error:/g, '<span class="error">Error:</span>');
                    }
                    
                    // Add result to terminal
                    terminal.innerHTML += `<div>${result}</div>`;
                    terminal.scrollTop = terminal.scrollHeight;
                })
                .catch(error => {
                    terminal.innerHTML += `<div class="error">Connection error: ${error.message}</div>`;
                    terminal.scrollTop = terminal.scrollHeight;
                });
        }
        
        // Send command
        function sendCommand() {
            const command = input.value.trim();
            if (command) {
                executeCommand(command);
                input.value = '';
            }
        }
        
        // Event listeners
        sendBtn.addEventListener('click', sendCommand);
        input.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                sendCommand();
            }
        });
        
        // Command buttons
        document.querySelectorAll('.cmd-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                input.value = this.innerText.trim();
                input.focus();
            });
        });
    </script>
</body>
</html>"""
        response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + html
    else:
        # Modern HTML page with Tailwind CSS
        html = """<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 LED Controller</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .card { transition: all 0.3s ease; }
        .card:hover { transform: translateY(-5px); }
        button { transition: all 0.2s ease; }
        button:active { transform: scale(0.95); }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold">ESP32 LED Controller</h1>
            <p class="text-gray-600 dark:text-gray-400">Control your ESP32's LED remotely</p>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- LED Control Card -->
            <div class="card bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">LED Control</h2>
                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <span>Status: <span id="ledState" class="font-mono">""" + ('ON' if led_state else 'OFF') + """</span></span>
                        <button id="ledToggle" onclick="toggleLed()" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                            """ + ('Turn Off' if led_state else 'Turn On') + """
                        </button>
                    </div>
                    <div class="pt-4">
                        <h3 class="font-medium mb-2">Blink Settings</h3>
                        <div class="grid grid-cols-2 gap-2">
                            <input type="number" id="blinkCount" placeholder="Count" value="3" 
                                   class="p-2 border rounded dark:bg-gray-700 dark:border-gray-600">
                            <input type="number" id="blinkInterval" placeholder="Interval (ms)" value="200" 
                                   class="p-2 border rounded dark:bg-gray-700 dark:border-gray-600">
                        </div>
                        <button onclick="blinkLed()" 
                                class="w-full mt-2 px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition">
                            Blink LED
                        </button>
                    </div>
                </div>
            </div>

            <!-- System Status Card -->
            <div class="card bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">System Status</h2>
                <div class="space-y-2">
                    <div class="flex justify-between">
                        <span>IP Address:</span>
                        <span id="ipAddress" class="font-mono">""" + (get_ip_address() or "Not connected") + """</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Uptime:</span>
                        <span id="uptime" class="font-mono">--</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Memory Free:</span>
                        <span id="memoryFree" class="font-mono">--</span>
                    </div>
                    <div class="flex justify-between">
                        <span>Memory Used:</span>
                        <span id="memoryUsed" class="font-mono">--</span>
                    </div>
                </div>
                <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button onclick="refreshStatus()" 
                            class="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                        Refresh Status
                    </button>
                </div>
            </div>

            <!-- Quick Actions Card -->
            <div class="card bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
                <div class="space-y-2">
                    <button onclick="restartDevice()"
                            class="w-full px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 transition">
                        Restart Device
                    </button>
                    <button onclick="checkStorage()"
                            class="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition">
                        Check Storage
                    </button>
                    <button onclick="checkMemory()"
                            class="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                        Check Memory
                    </button>
                    <a href="/repl" 
                       class="block w-full px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 transition text-center">
                        REPL Terminal
                    </a>
                </div>
            </div>
        </div>

        <footer class="mt-12 text-center text-sm text-gray-500 dark:text-gray-400">
            <p>ESP32 LED Controller &copy; 2025</p>
        </footer>
    </div>

    <script>
        // Toggle light/dark mode based on system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.documentElement.classList.add('dark');
        }
        
        // Functions for controlling the LED
        function toggleLed() {
            const currentState = document.getElementById('ledState').textContent;
            const endpoint = currentState === 'ON' ? '/led/off' : '/led/on';
            
            fetch(endpoint)
                .then(response => response.text())
                .then(text => {
                    document.getElementById('ledState').textContent = text.includes('ON') ? 'ON' : 'OFF';
                    document.getElementById('ledToggle').textContent = text.includes('ON') ? 'Turn Off' : 'Turn On';
                });
        }
        
        function blinkLed() {
            const count = document.getElementById('blinkCount').value || 3;
            const interval = document.getElementById('blinkInterval').value || 200;
            
            fetch(`/led/blink?count=${count}&interval=${interval}`)
                .then(response => response.text())
                .then(text => {
                    console.log(text);
                });
        }
        
        // Functions for system information
        function refreshStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('ledState').textContent = data.led_state;
                    document.getElementById('ledToggle').textContent = data.led_state === 'ON' ? 'Turn Off' : 'Turn On';
                    document.getElementById('ipAddress').textContent = data.ip_address || 'Not connected';
                    document.getElementById('uptime').textContent = Math.floor(data.uptime_seconds / 3600) + 'h ' + 
                        Math.floor((data.uptime_seconds % 3600) / 60) + 'm';
                });
        }
        
        function checkStorage() {
            fetch('/storage')
                .then(response => response.json())
                .then(data => {
                    alert(`Storage Info:\\nTotal: ${data.total_bytes} bytes\\nUsed: ${data.used_bytes} bytes\\nFree: ${data.free_bytes} bytes\\nUsed: ${data.used_percent}%`);
                });
        }
        
        function checkMemory() {
            fetch('/memory')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('memoryFree').textContent = data.free + ' bytes';
                    document.getElementById('memoryUsed').textContent = data.allocated + ' bytes';
                    alert(`Memory Info:\\nFree: ${data.free} bytes\\nAllocated: ${data.allocated} bytes\\nTotal: ${data.total} bytes\\nFragmentation: ${data.fragmentation}%`);
                });
        }
        
        function restartDevice() {
            if (confirm('Are you sure you want to restart the ESP32?')) {
                fetch('/restart')
                    .then(() => {
                        alert('Device is restarting. Please wait a moment before refreshing the page.');
                    });
            }
        }
        
        // Refresh status every 5 seconds
        setInterval(refreshStatus, 5000);
        
        // Initial status update
        refreshStatus();
    </script>
</body>
</html>"""
        response = 'HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + html
    
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