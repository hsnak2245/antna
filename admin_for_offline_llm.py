from flask import Flask, render_template, jsonify, request, url_for
from flask_cors import CORS
import subprocess
import socket
import json
import psutil
import time
import os

app = Flask(__name__)
CORS(app)

# Global variables
connected_devices = set()
ollama_running = False

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return '127.0.0.1'

def get_system_status():
    try:
        battery = psutil.sensors_battery()
        battery_percent = int(battery.percent) if battery else None
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return {
            "battery": battery_percent,
            "cpu": cpu_percent,
            "memory": memory.percent,
            "ollama_status": check_ollama_status()
        }
    except Exception as e:
        print(f"Error getting system status: {e}")
        return {
            "battery": None,
            "cpu": None,
            "memory": None,
            "ollama_status": check_ollama_status()
        }

def check_ollama_status():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def start_ollama():
    global ollama_running
    try:
        if check_ollama_status():
            ollama_running = True
            return True
            
        subprocess.Popen(['ollama', 'run', 'mistral'])
        time.sleep(2)  # Give Ollama some time to start
        ollama_running = True
        return True
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        return False

@app.route('/')
def home():
    """Server (laptop) interface"""
    local_ip = get_local_ip()
    system_status = get_system_status()
    return render_template('index.html', 
                         ip_address=local_ip,
                         connected_devices=list(connected_devices),
                         system_status=system_status)

@app.route('/client')
def client():
    """Client (phone) interface"""
    return render_template('client.html')

@app.route('/status')
def status():
    """Get system status"""
    return jsonify(get_system_status())

@app.route('/start-ollama', methods=['POST'])
def trigger_ollama():
    """Start the Ollama service"""
    success = start_ollama()
    return jsonify({"success": success})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    global ollama_running
    if not ollama_running:
        ollama_running = check_ollama_status()
    
    if not ollama_running:
        return jsonify({"error": "Ollama is not running"}), 400
    
    data = request.json
    message = data.get('message', '')
    
    try:
        import requests
        
        # Send request to Ollama
        response = requests.post('http://localhost:11434/api/generate', 
                               json={
                                   "model": "mistral",
                                   "prompt": message
                               },
                               stream=False)
        
        # Process the response
        if response.status_code == 200:
            full_response = ""
            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        response_data = json.loads(line)
                        if 'response' in response_data:
                            full_response += response_data['response']
                    except json.JSONDecodeError:
                        continue
            
            return jsonify({"response": full_response})
        else:
            return jsonify({"error": "Failed to get response from Ollama"}), 500
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/register-device', methods=['POST'])
def register_device():
    """Register a new client device"""
    device_id = request.json.get('device_id')
    device_name = request.json.get('device_name', 'Unknown Device')
    if device_id:
        device_info = f"{device_name} ({device_id})"
        connected_devices.add(device_info)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/unregister-device', methods=['POST'])
def unregister_device():
    """Unregister a client device"""
    device_id = request.json.get('device_id')
    device_name = request.json.get('device_name', 'Unknown Device')
    device_info = f"{device_name} ({device_id})"
    if device_info in connected_devices:
        connected_devices.remove(device_info)
        return jsonify({"success": True})
    return jsonify({"success": False})

if __name__ == '__main__':
    # Initialize Ollama status
    ollama_running = check_ollama_status()
    
    # Get and display the server IP
    server_ip = get_local_ip()
    print(f"\n{'='*50}")
    print(f"Antna Server starting at: http://{server_ip}:5000")
    print(f"For phone clients, visit: http://{server_ip}:5000/client")
    print(f"{'='*50}\n")
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
