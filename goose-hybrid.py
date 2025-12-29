#!/usr/bin/env python3
"""
Goose Hybrid Mode - Run TUI and Web UI simultaneously
"""

import subprocess
import sys
import time
import threading
import signal
from pathlib import Path

web_process = None
tui_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Shutting down Goose Dashboard...")
    
    if web_process:
        web_process.terminate()
        web_process.wait()
    
    if tui_process:
        tui_process.terminate()
        tui_process.wait()
    
    sys.exit(0)

def start_web_ui(port=8080):
    """Start web UI in background"""
    global web_process
    
    print(f"🌐 Starting Web UI on port {port}...")
    
    web_process = subprocess.Popen(
        [sys.executable, 'goose-web.py', '--port', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)  # Wait for server to start
    print(f"✅ Web UI running at http://localhost:{port}")

def start_tui():
    """Start TUI in foreground"""
    global tui_process
    
    print("🖥️ Launching Terminal UI...")
    time.sleep(1)
    
    # Run TUI directly (will take over terminal)
    try:
        subprocess.run([sys.executable, 'goose-tui.py'])
    except KeyboardInterrupt:
        pass

def main():
    """
    Hybrid Mode Launcher
    
    Starts both:
    - Web UI (background, port 8080)
    - TUI (foreground terminal)
    """
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("""
╭────────────────────────────────────────────╮
│                                            │
│      🪿  GOOSE DASHBOARD - HYBRID MODE      │
│                                            │
│  Terminal TUI + Web UI running together   │
│                                            │
╰────────────────────────────────────────────╯
""")
    
    # Check if required files exist
    if not Path('goose-web.py').exists():
        print("❌ Error: goose-web.py not found")
        sys.exit(1)
    
    if not Path('goose-tui.py').exists():
        print("❌ Error: goose-tui.py not found")
        sys.exit(1)
    
    # Start web UI in background thread
    web_thread = threading.Thread(target=start_web_ui, args=(8080,))
    web_thread.daemon = True
    web_thread.start()
    
    # Wait for web UI to initialize
    time.sleep(3)
    
    print("""
┌──────────────────────────────────────────┐
│  INTERFACE OPTIONS:                      │
│                                          │
│  • TUI: Use terminal interface below     │
│  • Web: Open http://localhost:8080       │
│                                          │
│  Press Ctrl+C to quit both               │
└──────────────────────────────────────────┘
""")
    
    # Start TUI in foreground (takes over terminal)
    start_tui()
    
    # Cleanup when TUI exits
    signal_handler(None, None)

if __name__ == '__main__':
    main()
