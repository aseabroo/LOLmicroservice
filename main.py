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
        except Exception as e:
            print(f"⏳ Waiting for server... (i)/100")
        time.sleep(0.1)
    print("❌ Server failed to start.")
    return False

def main():
    print("🚀 Launching Flask microservice...")
    server = subprocess.Popen(
        ["python", "LOLmicroservice.py"],
        preexec_fn=os.setsid
    )

    print(f"ℹ️  Server PID: {server.pid}")
    if not wait_for_server("http://127.0.0.1:5000"):
        print("❌ Server didn't start.")
        return

    print("✅ Server running at http://127.0.0.1:5000")
    print("🧪 Tests running next. Server will stay running.")
    
    subprocess.run(["python", "testMicroservice.py"], check=True)
    subprocess.run(["pytest", "test_app.py", "-v"], check=True)

    print("\n📝 Flask server is still running. Use CTRL+C to kill it manually.")
    print("🔁 Or press ENTER here to stop it cleanly.")
    input()
    os.killpg(os.getpgid(server.pid), signal.SIGTERM)
    print("✅ Done.")


if __name__ == "__main__":
    main()
