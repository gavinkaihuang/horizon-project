# Horizon Project

An AI-assisted family education system that repurposes old iPads as electronic photo frames, displaying personalized content based on facial recognition.

## Features
- **Face Recognition**: Identifies family members.
- **Content Generation**: Uses Gemini AI to generate daily English learning content and TTS audio.
- **SQLite Database**: Validates and logs recognition events.

## Application Structure
- **Backend (Port 8098)**: FastAPI service for recognition and task scheduling.
- **Nginx (Port 8090)**: Static file server for generated content (audio, json) and images.

## How to Run

### Prerequisites
- Docker & Docker Compose
- `GEMINI_API_KEY` set in `.env`

### Start Services
Because dependencies may change, always build on first run or update:
```bash
sudo docker compose up --build
```

## How to Use

### 1. Setup Faces
Place photos of family members in `data/known_faces/`.
- File naming: `name.jpg` (e.g., `alice.jpg`)
- Restart the backend to sync faces to the database:
  ```bash
  sudo docker compose restart backend
  ```

### 2. Recognize Face
Send a POST request to the recognition API:
```bash
curl -X POST -F "file=@/path/to/photo.jpg" http://localhost:8098/api/recognize
```
Response:
```json
{"user": "alice"}
```

### 3. Daily Content
The system automatically generates content at 04:00 daily.
- JSON: `http://localhost:8090/daily.json`
- Audio: `http://localhost:8090/daily_audio.mp3`