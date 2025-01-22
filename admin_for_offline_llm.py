from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import subprocess
import socket
import json

app = Flask(__name__)
CORS(app)

# Global variables
connected_devices = set()
ollama_running = False

def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        valid_ips = [ip for ip in ip_addresses if not ip.startswith('127.')]
        return valid_ips[0] if valid_ips else '127.0.0.1'
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return '127.0.0.1'

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
        ollama_running = True
        return True
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        return False

@app.route('/')
def home():
    local_ip = get_local_ip()
    global ollama_running
    ollama_running = check_ollama_status()
    
    return render_template('index.html', 
                         ip_address=local_ip,
                         connected_devices=list(connected_devices),
                         ollama_status=ollama_running)

@app.route('/start-ollama', methods=['POST'])
def trigger_ollama():
    success = start_ollama()
    return jsonify({"success": success})

@app.route('/chat', methods=['POST'])
def chat():
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
                               stream=False)  # Disable streaming
        
        # Check if the response is valid
        if response.status_code == 200:
            # Get the last response in case of streaming
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
    device_id = request.json.get('device_id')
    if device_id:
        connected_devices.add(device_id)
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/unregister-device', methods=['POST'])
def unregister_device():
    device_id = request.json.get('device_id')
    if device_id in connected_devices:
        connected_devices.remove(device_id)
        return jsonify({"success": True})
    return jsonify({"success": False})

if __name__ == '__main__':
    ollama_running = check_ollama_status()
    app.run(host='0.0.0.0', port=5000, debug=True)
