import subprocess
import time
import sys
import os
import requests

def start_flask():
    """Start Flask server in a subprocess"""
    # Use DETACHED_PROCESS flag to hide the console window
    flask_process = subprocess.Popen([
        sys.executable, "app.py"
    ], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    return flask_process

def check_server_ready():
    """Check if Flask server is ready to accept connections"""
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://127.0.0.1:5000/api/highscores', timeout=1)
            if response.status_code == 200:
                print(f"Server is ready (attempt {attempt+1}/{max_attempts})")
                return True
        except requests.exceptions.RequestException:
            print(f"Waiting for server to start (attempt {attempt+1}/{max_attempts})...")
            time.sleep(1)
    
    print("Server failed to start in time")
    return False

def start_client():
    """Start PyQt6 client after waiting for Flask"""
    client_process = subprocess.Popen([
        sys.executable, "rpg_client.py"
    ])
    return client_process

if __name__ == "__main__":
    print("Starting Flask server...")
    flask_proc = start_flask()
    
    print("Waiting for server to start...")
    if check_server_ready():
        print("Starting game client...")    
        client_proc = start_client()
        
        try:
            # Wait for client to finish
            client_proc.wait()
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            # Kill Flask server when done
            print("Shutting down server...")
            flask_proc.terminate()
    else:
        print("Failed to start game client: server not responding")
        flask_proc.terminate()