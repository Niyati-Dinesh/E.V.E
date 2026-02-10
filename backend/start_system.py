"""
Start E.V.E. System - Master and All Workers
"""
import subprocess
import time
import sys
import os

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("🚀 STARTING E.V.E. SYSTEM")
print("="*70)


# Start Master Controller
print("\n1️⃣  Starting Master Controller...")
master_process = subprocess.Popen(
    [sys.executable, "master_controller/master_controller.py"],
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
)

# Wait for master to be healthy
import requests
import socket

def wait_for_master(host, port, timeout=60):
    url = f"http://{host}:{port}/health"
    start = time.time()
    print(f"   Checking: {url}")
    last_error = None
    while time.time() - start < timeout:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "ok":
                    print("\n✅ Master Controller is healthy!")
                    return True
                else:
                    print(f"   ⚠️  Unexpected status: {data.get('status')}")
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {str(e)[:50]}"
        except Exception as e:
            last_error = f"Error: {str(e)[:100]}"
        
        print(f"   Waiting for master... ({int(time.time() - start)}s)")
        time.sleep(2)
    
    print(f"\n❌ Master Controller did not become healthy after {timeout} seconds.")
    if last_error:
        print(f"   Last error: {last_error}")
    print("\n⚠️  Check the Master Controller window for error messages.")
    return False

# Get host/port from .env or default
import dotenv
# Load .env from master_controller folder where it exists
env_path = os.path.join(os.path.dirname(__file__), 'master_controller', '.env')
dotenv.load_dotenv(env_path)
master_host = os.getenv("MASTER_HOST", "localhost")
master_port = int(os.getenv("MASTER_PORT", "8000"))

if not wait_for_master(master_host, master_port, timeout=60):
    print("\n🔍 Troubleshooting steps:")
    print("   1. Check the Master Controller console window for errors")
    print("   2. Verify PostgreSQL database is accessible")
    print("   3. Ensure GROQ_API_KEY is set in master_controller/.env")
    print("   4. Check if port 8000 is already in use")
    print("\nExiting due to master startup failure.")
    master_process.terminate()
    sys.exit(1)

# Give master extra time to fully initialize
print("   Giving master additional time to initialize...")
time.sleep(5)

# Start Workers
print("\n2️⃣  Starting Workers...")

workers = [
    ("Coding Worker", "workers/coding_worker.py"),
    ("Documentation Worker", "workers/doc_worker.py"),
    ("Analysis Worker", "workers/analysis_worker.py")
]

worker_processes = []
for name, path in workers:
    print(f"   Starting {name}...")
    process = subprocess.Popen(
        [sys.executable, path],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    worker_processes.append(process)
    time.sleep(4)  # Increased delay between workers to prevent overwhelming master

# Wait for workers to register with master
print("\n3️⃣  Verifying worker registration...")
time.sleep(6)  # Give workers time to complete registration and send first heartbeat

try:
    check_url = f"http://{master_host}:{master_port}/health"
    resp = requests.get(check_url, timeout=5)
    print("   ✅ All systems ready!")
except:
    print("   ⚠️  Workers may still be registering...")

print("\n" + "="*70)
print("✅ E.V.E. SYSTEM RUNNING")
print("="*70)
print("\n📱 Open your browser to: http://localhost:8000/user_interface.html")
print("\n🔧 Master Controller: http://localhost:8000")
print("   - Coding Worker: http://localhost:5001")
print("   - Documentation Worker: http://localhost:5002")
print("   - Analysis Worker: http://localhost:5003")
print("\n💡 Press Ctrl+C to stop all services")
print("="*70 + "\n")

try:
    # Keep running
    master_process.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Stopping all services...")
    master_process.terminate()
    for process in worker_processes:
        process.terminate()
    print("✅ All services stopped")
