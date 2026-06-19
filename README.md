# Project: The Eye of the Storm Inititave
## Adaptive Video Streaming Pipeline on AWS

## Overview

This project implements an adaptive bitrate (ABR) video streaming pipeline using AWS Media Services and FFmpeg.

The system ingests a local MP4 file from an Amazon EC2 instance, transmits the stream via SRT, performs cloud-based transcoding and packaging, and delivers adaptive MPEG-DASH playback.

---

## Architecture

EC2-FFmpeg(SRT-Caller) -> AWS MediaConnect (SRT Listener) -> AWS MediaLive -> AWS MediaPackage -> DASH Player

---

## Components

### FFmpeg

FFmpeg runs on an Ubuntu EC2 instance and continuously loops a local MP4 file.

Responsibilities:

* Read source video
* Stream via SRT-Caller mode
* Send MPEG-TS transport stream to AWS MediaConnect

### AWS MediaConnect

Acts as the SRT ingest endpoint.

Responsibilities:

* Receive SRT stream via SRT Listener mode
* Forward stream to MediaLive

### AWS MediaLive

Performs cloud transcoding.

Generated renditions:

* 1080p
* 720p
* 480p

### AWS MediaPackage

Packages transcoded outputs into MPEG-DASH format.

### DASH Player

Used to verify adaptive playback.

provided by AWS, might be down in-case if the MediaPipe Line is in off state

Can be selected from the Media Channel DASH endpoint preview, or by directly accessing the following url in any browser, and click "Load"
https://reference.dashif.org/dash.js/nightly/samples/dash-if-reference-player/index.html?mpd=https://ccf3786b925ee51c.mediapackage.us-east-1.amazonaws.com/out/v1/04e44707aa714630842e42bd6f546afe/index.mpd

The player automatically switches between available bitrates based on network conditions.

---

## PROJECT DIRECTORY STRUCTURE

streaming-demo/
├── README.md
├── api/
|   ├── Dockerfile
│   ├── api.py
│   ├── requirements.txt
├── input/
|   ├── tempest_input.mp4
├── logs/
|   ├── ffmpeg.log
|   ├── ffmpeg.pid
└── scripts/
    ├── start_ffmpeg.sh
    ├── stop_ffmpeg.sh
    └── status.sh

## Running the Project

# For seemless execution on a fresh EC2 via ssh
sudo apt update
sudo apt install git ffmpeg tree -y

git clone https://github.com/ihsan314ullah-byte/MPLStableDockerImage

ls-lh

cd MPLStableDockerImage

mv MPLStableDockerImage ~/streaming-demo

cd ~/streaming-demo

tree -L 3

make sure the ~/streaming-demo/logs exist, if not you will get errors in starting/stoping ffmpeg script
and then make 

mkdir -p logs

ensure scripts are executiable via:
chmod +x scripts/*.sh

check via: ls -lh ~/streaming-demo/scripts/


### STARTING Docker Metrics PYTHON API

This project runs a hybrid system:
- FFmpeg runs on the EC2 host
- PYTHON FastAPI runs inside Docker
- Both are connected via shared filesystem (volume mount)

#### 1. Install Docker:

```bash
sudo apt install -y docker.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

IMPORTANT: logout and login again after installing Docker.

---

#### 2. BUILD DOCKER IMAGE

Go to API folder:

```bash
cd ~/streaming-demo/api
docker build -t metrics-api .
```
#### 3. RUN DOCKER CONTAINER 

```bash
docker run -d \
  --name metrics-api \
  -p 8000:8000 \
  -v /home/ubuntu/streaming-demo:/home/ubuntu/streaming-demo \
  metrics-api
```

The volume mount is critical — it connects Docker with host scripts and logs.

#### 4. VERIFY CONTAINER
docker ps

---
Expected: metrics-api   Up

#### 5. API ENDPOINTS

##### Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{"status":"ok"}
```

---

##### System Status

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

##### Metrics (Lightweight JSON)

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

#### Start Streaming

cd ~/streaming-demo/scripts

./start_ffmpeg.sh

#### Check Status

./status.sh

#### Stop Streaming

./stop_ffmpeg.sh

---


## Verification

Successful operation is verified by:

1. AWS MediaConnect status changes to CONNECTED.
2. AWS MediaLive channel receives healthy input.
3. AWS DASH player displays video.
4. Adaptive bitrate switching is available.

---

### FINAL VALIDATION

Run all:

```bash
./scripts/status.sh
curl localhost:8000/status
curl localhost:8000/metrics
```

All outputs should match logically.


## Technical Decisions

### Why SRT?

SRT provides:

* Reliable transport
* Low latency
* Packet loss recovery

### Why AWS Media Services?

AWS Media Services provide managed:

* Ingest
* Transcoding
* Packaging
* Streaming

without requiring self-managed streaming infrastructure.

### Why FFmpeg ?
* Open source
* High performance
* used by major streaming providers like Youtube, NetFlix, TikTok etc.

#### Why FFmpeg Copy Mode?

The EC2 instance uses: -c copy

This minimizes CPU usage by avoiding local transcoding.

Transcoding is delegated to AWS MediaLive.

---

## Scalability

The architecture can scale by:

* Increasing MediaLive output renditions
* Using CloudFront CDN in front of MediaPackage
* Deploying multiple ingest points
* Using Auto Scaling for ingest instances

---

## Cost Considerations

Primary cost drivers:

* MediaLive channel runtime -> main cost driving factor
* MediaConnect flow runtime
* MediaPackage egress traffic
* EC2 instance runtime -> The EC2 ingest instance has minimal compute requirements because transcoding occurs in AWS MediaLive.

---

## Future Improvements

* Dockerized monitoring API
* JWT authentication
* Prometheus metrics
* CI/CD pipeline
* Infrastructure as Code (Terraform)

---

## Demonstration

The project successfully demonstrates:

* Video ingest
* Adaptive bitrate transcoding
* MPEG-DASH delivery
* End-to-end playback through AWS Media Services
