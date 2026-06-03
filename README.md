# Smart Camera — Emotion-Based Music Recommendation System

A full-stack web application that captures user images via webcam, performs facial analytics including emotion detection, and recommends music from YouTube based on the detected emotion and the user's preferred music language.

---

## Project Overview

The system follows this end-to-end pipeline:

```
User captures image via webcam
        ↓
Facial analytics are performed
(emotion detection, age, gender, smile score, portrait quality)
        ↓
Emotion is mapped to a smart music mood phrase
        ↓
Preferred music language is read from the user profile
        ↓
YouTube Data API is queried with the combined search phrase
        ↓
Playlist and compilation results are filtered out
Duration-based filtering keeps only real songs (2–8 minutes)
        ↓
Results are shuffled for variety
        ↓
User receives 5 personalized music recommendations
and can like or dislike each song
```

---

## Key Features

- Real-time webcam capture with smile-triggered auto-capture
- Upload mode for analyzing existing photos
- Facial analytics: emotion detection, age prediction, gender detection, smile scoring
- Portrait quality scoring: lighting, sharpness, alignment, final score
- Personalized music recommendations via YouTube search
- Language-based music preference from user profile
- Smart emotion-to-query mapping (avoids generic phrases like "happy songs")
- Filtering of playlist, compilation, and long-duration videos
- Randomized song recommendations for variety
- Like and dislike system — disliked songs never appear again
- Photo gallery with session grouping and best-photo detection
- Collage creator: select 2–5 photos, choose a layout, generate and save
- Live guidance overlay during capture (lighting, alignment, smile prompts)
- Firebase authentication with Google Sign-In support
- User profile with preferred music language and genre settings

---

## Tech Stack

### Frontend
- **React 18** — component-based UI
- **React Router v6** — client-side routing
- **Framer Motion** — page and component animations
- **Axios** — HTTP client for API calls
- **Firebase SDK** — authentication (Google Sign-In)
- **Recharts** — analytics charts

### Backend
- **Python 3.10+**
- **FastAPI** — async REST API framework
- **Uvicorn** — ASGI server
- **SQLAlchemy** — ORM with SQLite
- **WebSockets** — real-time frame streaming for live detection
- **Firebase Admin SDK** — server-side token verification
- **Pillow** — image processing for collage generation
- **python-dotenv** — environment variable management

### Computer Vision & ML
- **OpenCV** — face detection, smile detection, image processing
- **DeepFace** — smile strength computation and emotion analysis
- **Pre-trained Caffe models** — age and gender prediction (`age_net.caffemodel`)

### External APIs
- **YouTube Data API v3** — music search and video metadata
- **Firebase Authentication** — user identity management

---

## System Architecture

```
Camera Capture (WebSocket stream)
        ↓
Frame Analysis — face detection, smile counter, guidance
        ↓
Auto-Capture on smile threshold
        ↓
Image Processing — age, gender, smile strength, portrait quality
        ↓
Emotion Detection — mapped from smile probability
        ↓
Query Generation — emotion phrase + preferred language
        ↓
YouTube Search — videoCategoryId=10, maxResults=20
        ↓
Result Filtering — remove playlists, compilations, out-of-range durations
        ↓
Shuffle + Like/Dislike Exclusion
        ↓
Top 5 Recommendations returned to frontend
```

---

## Music Recommendation Logic

1. **Emotion mapping** — detected emotion is converted to a descriptive phrase rather than a naive keyword:

   | Emotion | Search Phrase |
   |---|---|
   | happy | feel good cheerful |
   | sad | emotional heartfelt |
   | excited | energetic party |
   | calm | peaceful acoustic |
   | neutral | trending popular |

2. **Language preference** — the user's `preferred_music_language` (e.g. `telugu`, `hindi`, `english`) is appended to the query:
   ```
   feel good cheerful telugu songs official audio
   ```

3. **YouTube search** — queries the YouTube Data API with `videoCategoryId=10` (Music) and `maxResults=20` to get a large candidate pool.

4. **Playlist/compilation filtering** — titles matching patterns like `top 10`, `100 songs`, `1 hour`, `playlist`, `compilation`, `mix`, `nonstop` are removed.

5. **Duration filtering** — the YouTube `videos` endpoint is called to fetch durations. Only videos between **2 and 8 minutes** are kept.

6. **Ranking** — videos with a typical `Artist - Title` format are ranked higher.

7. **Shuffle** — remaining results are shuffled for variety.

8. **Like/dislike exclusion** — disliked video IDs are permanently excluded. Liked IDs are soft-excluded to avoid repetition.

9. **Top 5 returned** — final recommendations are sent to the frontend with embed URLs for in-page playback.

> The CSV dataset (`music.csv`) and dataset-based filtering pipeline are preserved in `dataset_service.py` for future use but are not active in the current pipeline.

---

## Project Structure

```
smart-camera/
├── backend/
│   ├── app/
│   │   ├── core/               # Database engine, Firebase auth, security
│   │   ├── models/             # SQLAlchemy models (User, Photo, LikedSong, DislikedSong)
│   │   ├── routes/             # API route handlers
│   │   │   ├── auth_routes.py
│   │   │   ├── camera_routes.py
│   │   │   ├── collage_routes.py
│   │   │   ├── frame_analysis_routes.py
│   │   │   └── music_routes.py
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # Core processing modules
│   │       ├── age_predict.py
│   │       ├── best_image_selector.py
│   │       ├── caption_engine.py
│   │       ├── capture_service.py
│   │       ├── dataset_service.py      # CSV pipeline (kept for future use)
│   │       ├── emotion_engine.py
│   │       ├── face_detect.py
│   │       ├── gender_detect.py
│   │       ├── guidance_engine.py
│   │       ├── mood_recommendation_engine.py
│   │       ├── portrait_analytics_engine.py
│   │       ├── quality_analysis.py
│   │       ├── session_ranking_engine.py
│   │       ├── smile_analytics.py
│   │       ├── smile_detect.py
│   │       └── youtube_service.py
│   ├── models/                 # Pre-trained Caffe model files
│   ├── storage/                # Captured images (gitignored)
│   ├── music.csv               # Spotify track dataset (gitignored, kept for future use)
│   ├── smart_camera.db         # SQLite database (gitignored)
│   ├── requirements.txt
│   └── run_backend.bat         # Windows backend startup script
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/         # Navbar, AuthModal, GoogleSignIn, CompleteProfile
│       ├── pages/              # Camera, Gallery, Home, About, Profile, Analytics
│       ├── App.js
│       ├── firebase.js
│       └── index.js
├── .gitignore
└── README.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A webcam
- A [YouTube Data API v3 key](https://console.cloud.google.com/)
- A Firebase project with Authentication enabled

### 1. Clone the repository

```bash
git clone <repository-url>
cd smart-camera
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
FIREBASE_PROJECT_ID=your-firebase-project-id
DATABASE_URL=sqlite:///./smart_camera.db
YOUTUBE_API_KEY=your_youtube_api_key
```

Place your Firebase service account key at `backend/serviceAccountKey.json`.

Start the backend server:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 3. Frontend setup

```bash
cd frontend
npm install
npm start
```

The frontend will run at `http://localhost:3000`.

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive a token |
| `POST` | `/api/camera/capture` | Capture/upload a photo and run full analysis |
| `GET` | `WS /api/camera/ws/analyze` | WebSocket for live frame analysis |
| `GET` | `/api/photos/user` | Get all photos for the current user |
| `DELETE` | `/api/photos/{id}` | Delete a photo |
| `POST` | `/api/music/like` | Like a song |
| `POST` | `/api/music/dislike` | Dislike a song |
| `POST` | `/api/collage/create` | Generate a collage from selected photos |

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `FIREBASE_PROJECT_ID` | Yes | Firebase project ID for auth verification |
| `DATABASE_URL` | Yes | SQLAlchemy database URL |
| `YOUTUBE_API_KEY` | Yes | YouTube Data API v3 key for music search |

---

## Future Improvements

- Better music recommendation algorithms using audio feature matching
- Support for more regional languages and music genres
- Improved YouTube result filtering using channel metadata
- Enhanced personalization using full user listening history
- Multi-face emotion aggregation for group captures
- Mobile-responsive UI improvements
- Progressive Web App (PWA) support

---

## License

[Specify your license here]
