# FastAPI framework for building APIs
from fastapi import FastAPI

# Used to run shell commands from Python (status.sh, top, free, etc.)
import subprocess

# Used to check if FFmpeg PID file exists on disk
import os

# Create FastAPI application instance
app = FastAPI()

# ------------------------------------------------------------
# PATH CONFIGURATION (SHARED WITH HOST VIA DOCKER VOLUME)
# ------------------------------------------------------------

# Path to the host script that shows system status
BASE = "/home/ubuntu/streaming-demo/scripts/status.sh"

# Path to FFmpeg PID file (created by start_ffmpeg.sh)
PID_FILE = "/home/ubuntu/streaming-demo/logs/ffmpeg.pid"


# ------------------------------------------------------------
# HEALTH CHECK ENDPOINT
# ------------------------------------------------------------
# Simple test endpoint to verify API is running
@app.get("/health")
def health():
    return {"status": "ok"}


# ------------------------------------------------------------
# STATUS ENDPOINT (RUNS HOST SCRIPT)
# ------------------------------------------------------------
@app.get("/status")
def status():

    # Runs the host script using bash
    # This script outputs FFmpeg status, CPU, memory, disk, network
    result = subprocess.run(
        ["bash", BASE],
        capture_output=True,   # capture output instead of printing
        text=True              # return string instead of bytes
    )

    # Return script output inside JSON response
    return {"output": result.stdout}


# ------------------------------------------------------------
# METRICS ENDPOINT (LIGHTWEIGHT SYSTEM + FFmpeg STATUS)
# ------------------------------------------------------------
@app.get("/metrics")
def metrics():

    # --------------------------------------------------------
    # CPU USAGE
    # --------------------------------------------------------
    # top -bn1 = single snapshot of CPU usage
    # grep + awk extracts CPU idle/busy percentage
    cpu = subprocess.getoutput(
        "top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'"
    )

    # --------------------------------------------------------
    # MEMORY USAGE
    # --------------------------------------------------------
    # free -m gives memory in MB
    # awk calculates percentage used
    mem = subprocess.getoutput(
        "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2}'"
    )

    # --------------------------------------------------------
    # FFmpeg STATUS (BASED ON PID FILE)
    # --------------------------------------------------------
    # We do NOT use pgrep because Docker cannot see host processes
    # Instead we use PID file created by start_ffmpeg.sh
    ffmpeg_running = os.path.exists(PID_FILE)

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------
    return {
        "cpu_percent": cpu,
        "memory_percent": mem,
        "ffmpeg": "running" if ffmpeg_running else "stopped"
    }
