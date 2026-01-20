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

### 1. Initial Setup
1.  **Configure Environment**:
    Make sure your `.env` file matches the template (set your API key and Module):
    ```bash
    GEMINI_API_KEY=your_api_key_here
    MODULE=gemini-3-flash-preview
    ```

2.  **Start the System**:
    Run the following command to start the backend and nginx services:
    ```bash
    sudo docker compose up --build
    ```
    *   **Backend API**: Running at `http://localhost:8098`
    *   **Nginx (Content)**: Running at `http://localhost:8090`

### 2. Face Recognition Setup
To recognize family members:
1.  Place photos in the `data/known_faces/` directory (e.g., `alice.jpg`).
2.  Restart the backend to process the new photos:
    ```bash
    sudo docker compose restart backend
    ```

### 3. Usage Examples

**Check System Status:**
Open `http://localhost:8098/` in your browser. You should see:
`{"message": "Horizon Backend is running"}`

**Face Recognition:**
```bash
curl -X POST -F "file=@/path/to/photo.jpg" http://localhost:8098/api/recognize
```

**Daily Content:**
The system generates English learning content at 04:00 daily. You can also trigger it manually by restarting the backend (it runs on startup).
- **JSON Data**: `http://localhost:8090/daily.json`
- **Audio File**: `http://localhost:8090/daily_audio.mp3`