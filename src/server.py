#!/usr/bin/env python3
"""
Python wrapper to start Node.js server
This maintains compatibility with the existing supervisor configuration
"""
import subprocess
import sys
import os
import signal

def signal_handler(signum, frame):
    print(f"Received signal {signum}, shutting down...")
    if 'server_process' in globals():
        server_process.terminate()
    sys.exit(0)

# Set up signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

try:
    # Change to the backend directory
    os.chdir('/app/backend')
    
    # Start Node.js server  
    print("🚀 Starting Node.js backend server...")
    server_process = subprocess.Popen([
        'node', 'app.js'
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Forward output
    for line in server_process.stdout:
        print(line.rstrip())
        
except KeyboardInterrupt:
    print("\n🛑 Keyboard interrupt received")
    if 'server_process' in locals():
        server_process.terminate()
except Exception as e:
    print(f"❌ Error starting Node.js server: {e}")
    sys.exit(1)
finally:
    if 'server_process' in locals():
        server_process.wait()
        sys.exit(server_process.returncode)