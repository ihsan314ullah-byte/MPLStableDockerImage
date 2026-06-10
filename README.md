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
* Stream via SRT
* Send MPEG-TS transport stream to AWS MediaConnect

### AWS MediaConnect

Acts as the SRT ingest endpoint.

Responsibilities:

* Receive SRT stream
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

## Directory Structure
└── streaming-demo
    ├── api
    │   ├── Dockerfile
    │   ├── api.py
    │   └── requirements.txt
    ├── input
    │   └── tempest_input.mp4
    ├── logs
    │   └── ffmpeg.log
    └── scripts
        ├── start_ffmpeg.sh
        ├── status.sh
        └── stop_ffmpeg.sh

6 directories, 8 files

streaming-demo/
├── input/
│ └── tempest_input.mp4
├── logs/
│ ├── ffmpeg.log
│ └── ffmpeg.pid
├── scripts/
│ ├── start_ffmpeg.sh
│ ├── stop_ffmpeg.sh
│ └── status.sh
└── README.md

---

## Running the Project

# For seemless execution on a fresh EC2 via ssh
sudo apt update
sudo apt install git ffmpeg tree -y

git clone https://github.com/ihsan314ullah-byte/Live-Streaming-Media-Pipeline

cd Live-Streaming-Media-Pipeline

mv Live-Streaming-Media-Pipeline ~/streaming-demo

cd ~/streaming-demo

tree -L 3

make sure the ~/streaming-demo/logs exist, if not you will get errors in starting/stoping ffmpeg script
and then make 
mkdir -p logs

ensure scripts are executiable via chmod +x scripts/*.sh

### Start Streaming

cd ~/streaming-demo/scripts

./start_ffmpeg.sh

### Check Status

./status.sh

### Stop Streaming

./stop_ffmpeg.sh

---

## Verification

Successful operation is verified by:

1. AWS MediaConnect status changes to CONNECTED.
2. AWS MediaLive channel receives healthy input.
3. AWS DASH player displays video.
4. Adaptive bitrate switching is available.

---

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
