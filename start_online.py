import subprocess
import re
import sys
import os
import time
import threading
import socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_PATH = os.path.join(BASE_DIR, "cloudflared.exe")
LINK_FILE = os.path.join(BASE_DIR, "Online_Link.txt")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def free_port(port):
    if is_port_in_use(port):
        print(f"Notice: Port {port} is busy. Freeing previous instance...")
        try:
            out = subprocess.check_output(f'netstat -ano -p tcp | findstr :{port}', shell=True, text=True)
            for line in out.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5 and 'LISTENING' in parts:
                    pid = parts[4]
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except Exception:
            pass

if not os.path.exists(CLOUDFLARED_PATH):
    print(f"Error: cloudflared.exe not found in {BASE_DIR}")
    sys.exit(1)

print("=" * 65)
print("  Future Life Investments - Legal & Recovery Dashboard")
print("  Online Hosting Launcher (Cloudflare Tunnel)")
print("=" * 65)

# Free port 8501 if previously occupied
free_port(8501)

print("[1/2] Starting Streamlit server...")

# Start Streamlit process
streamlit_proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py"],
    cwd=BASE_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE
)

time.sleep(2)
print("[2/2] Connecting Cloudflare Tunnel to the internet...")

# Start Cloudflare Tunnel process
cloudflared_proc = subprocess.Popen(
    [CLOUDFLARED_PATH, "tunnel", "--url", "http://127.0.0.1:8501"],
    cwd=BASE_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

online_url = None
url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

def drain_pipe(pipe):
    try:
        for _ in pipe:
            pass
    except Exception:
        pass

def cleanup():
    print("\nShutting down servers...")
    try:
        cloudflared_proc.kill()
    except Exception:
        pass
    try:
        streamlit_proc.kill()
    except Exception:
        pass
    print("Closed successfully.")

try:
    for line in cloudflared_proc.stderr:
        match = url_pattern.search(line)
        if match:
            online_url = match.group(0)
            break
        if cloudflared_proc.poll() is not None:
            break

    if online_url:
        # Start background thread to keep draining pipe so it never buffers or hangs
        threading.Thread(target=drain_pipe, args=(cloudflared_proc.stderr,), daemon=True).start()
        threading.Thread(target=drain_pipe, args=(cloudflared_proc.stdout,), daemon=True).start()

        # Save URL to text file
        with open(LINK_FILE, "w", encoding="utf-8") as f:
            f.write(f"Future Life Investments - Online Dashboard Link\n")
            f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"ONLINE URL: {online_url}\n")
            f.write(f"LOCAL WI-FI URL: http://192.168.8.196:8501\n")

        print("\n" + "=" * 65)
        print("  SUCCESSFULLY CONNECTED TO THE INTERNET!")
        print("=" * 65)
        print(f"\n  >> ONLINE LINK (Use this from ANY PC or Phone anywhere):")
        print(f"     {online_url}\n")
        print(f"  >> LOCAL WI-FI LINK (For PCs on the same Wi-Fi):")
        print(f"     http://192.168.8.196:8501\n")
        print("=" * 65)
        print(f"  * This link has also been saved to '{os.path.basename(LINK_FILE)}'.")
        print("  * Keep this window OPEN while you want the dashboard to be active.")
        print("  * Press Ctrl + C or close this window when you want to stop.")
        print("=" * 65 + "\n")
        
        # Keep running
        while True:
            time.sleep(1)
            if streamlit_proc.poll() is not None:
                print(f"Streamlit stopped (code {streamlit_proc.poll()}).")
                break
            if cloudflared_proc.poll() is not None:
                print(f"Cloudflared stopped (code {cloudflared_proc.poll()}).")
                break
    else:
        print("Could not retrieve Cloudflare Tunnel URL. Please check your internet connection.")
except KeyboardInterrupt:
    pass
finally:
    cleanup()

