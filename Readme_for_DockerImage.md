# Streaming Demo — FFmpeg + Docker Metrics API

This project runs a hybrid system:
- FFmpeg runs on the EC2 host
- FastAPI runs inside Docker
- Both are connected via shared filesystem (volume mount)

# SYSTEM OVERVIEW

EC2 HOST
│
├── FFmpeg process (host machine)
├── scripts/
│   ├── start_ffmpeg.sh
│   ├── stop_ffmpeg.sh
│   ├── status.sh
│
├── logs/
│   ├── ffmpeg.pid
│   ├── ffmpeg.log
│
└── Docker Container (metrics-api)
├── FastAPI (uvicorn)
├── /health
├── /status (runs host script)
├── /metrics (reads system stats + PID file)

# 1. EC2 SETUP (FRESH MACHINE)

Update system:
```bash
sudo apt update && sudo apt upgrade -y
````

Install Docker:

```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

IMPORTANT: logout and login again after installing Docker.

---

# 2. PROJECT STRUCTURE

```
streaming-demo/
├── api/
│   ├── api.py
│   ├── requirements.txt
│   ├── Dockerfile
│
├── scripts/
│   ├── start_ffmpeg.sh
│   ├── stop_ffmpeg.sh
│   ├── status.sh
│
├── logs/
└── input/
```

---

# 3. START FFmpeg (HOST)

Go to scripts folder:

```bash
cd scripts
chmod +x *.sh
```

Start FFmpeg:

```bash
./start_ffmpeg.sh
```

Check status:

```bash
./status.sh
```

Stop FFmpeg:

```bash
./stop_ffmpeg.sh
```

---

# 4. BUILD DOCKER IMAGE

Go to API folder:

```bash
cd api
docker build -t metrics-api .
```

---

# 5. RUN DOCKER CONTAINER 

```bash
docker run -d \
  --name metrics-api \
  -p 8000:8000 \
  -v /home/ubuntu/streaming-demo:/home/ubuntu/streaming-demo \
  metrics-api
```

The volume mount is critical — it connects Docker with host scripts and logs.

---

# 6. API ENDPOINTS

## Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{"status":"ok"}
```

---

## System Status

```bash
curl http://localhost:8000/status
```

Shows:

* FFmpeg status
* CPU usage
* Memory usage
* Disk usage
* Internet connectivity

---

## Metrics (Lightweight JSON)

```bash
curl http://localhost:8000/metrics
```

Response:

```json
{
  "cpu_percent": "...",
  "memory_percent": "...",
  "ffmpeg": "running"
}
```

---

# 7. DESIGN RULES (VERY IMPORTANT)

* FFmpeg runs ONLY on the EC2 host
* Docker does NOT run FFmpeg
* Communication is done via shared files (`logs/ffmpeg.pid`)
* Never use `pgrep` inside Docker (it cannot see host processes)
* PID file is the single source of truth for FFmpeg state

---

# 8. DEBUGGING GUIDE

## Container not running

```bash
docker ps -a
docker logs metrics-api
```

---

## Restart container

```bash
docker restart metrics-api
```

---

## FFmpeg status mismatch

Check:

```bash
cat logs/ffmpeg.pid
./scripts/status.sh
```

---

## Python crash inside container

Validate before build:

```bash
python3 -m py_compile api/api.py
```

---

## Metrics not working

Ensure Dockerfile includes:

* procps
* curl
* iputils-ping

---

## Status mismatch between host and API

Ensure correct run command includes:

```bash
-v /home/ubuntu/streaming-demo:/home/ubuntu/streaming-demo
```

---

# 9. FINAL VALIDATION

Run all:

```bash
./scripts/status.sh
curl localhost:8000/status
curl localhost:8000/metrics
```

All outputs should match logically.

---

# DONE

If everything works:
✔ FFmpeg running on host
✔ Docker API running
✔ Metrics correct
✔ Status consistent across system

```

---
