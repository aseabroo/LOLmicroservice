import subprocess
import time
import requests
import signal
import os

def wait_for_server(url, timeout=10):
    """Ping server until it responds or timeout."""
    for _ in range(timeout * 10):
        try:
            res = requests.get(url)
            if res.status_code == 200:
                print("✅ Flask server is up.")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(0.1)
    print("❌ Server failed to start.")
    return False

def main():
    print("🚀 Launching Flask microservice...")
    server = subprocess.Popen(
        ["python", "LOLmicroservice.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # Allow group termination
    )

    try:
        # Wait until server is ready
        if not wait_for_server("http://127.0.0.1:5000"):
            raise Exception("Server did not respond in time")

        print("\n🧪 Running testMicroservice.py (image preview)...")
        subprocess.run(["python", "testMicroservice.py"], check=True)

        print("\n🧪 Running test_app.py (pytest)...")
        subprocess.run(["pytest", "test_app.py", "-v"], check=True)

    finally:
        print("\n🛑 Terminating Flask server...")
        os.killpg(os.getpgid(server.pid), signal.SIGTERM)
        print("✅ Done.")

if __name__ == "__main__":
    main()
