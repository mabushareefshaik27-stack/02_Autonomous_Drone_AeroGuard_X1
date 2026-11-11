#!/usr/bin/env python3
"""
AeroGuard-X1 One-Click Launcher.
Launches the GCS Server and opens the interactive Power Presentation and Flight Simulator.
"""

import sys
import os
import webbrowser
import threading
import time

# Add project root directory to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from gcs.server import run_gcs_server
from pptx_generator import create_pptx

def open_browser_delayed(url: str):
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    url = f"http://localhost:{port}"

    # Ensure PowerPoint PPTX is generated
    pptx_path = os.path.join(os.path.dirname(__file__), "AeroGuard_X1_Presentation.pptx")
    if not os.path.exists(pptx_path):
        create_pptx(pptx_path)

    print("=" * 68)
    print("   🚁 AEROGUARD-X1: AUTONOMOUS DRONE CAPSTONE PROJECT 🚁")
    print("=" * 68)
    print(f" -> Portal Dashboard:              {url}")
    print(f" -> AI Blueprint & Image Studio:    {url}/blueprint.html")
    print(f" -> Interactive Power Presentation: {url}/presentation.html")
    print(f" -> Tactical Ground Station (GCS):  {url}/gcs.html")
    print(f" -> Direct PowerPoint PPTX:        {url}/api/drone/download-pptx")
    print("-" * 68)
    print(" Press Ctrl+C in terminal to stop.")
    print("=" * 68 + "\n")

    threading.Thread(target=open_browser_delayed, args=(f"{url}/presentation.html",), daemon=True).start()
    run_gcs_server(port)

if __name__ == "__main__":
    main()

