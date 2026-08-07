# 🎬 ZEDFLIX — Movie Streaming Platform

A Netflix-style movie streaming web app with a custom video player. No iframes — all movies play directly in our own HLS.js player.

## Features

- 🎬 **Custom Video Player** — HLS.js powered, no iframes
- 🔍 **Search** — Find any movie instantly
- 🔥 **Trending** — See what's hot this week
- 🎭 **Genres** — Browse by genre
- 🎥 **Movie Details** — Cast, ratings, similar movies
- 📱 **Responsive** — Works on desktop & mobile
- 🌙 **Dark Mode** — Premium Netflix-style UI

## Tech Stack

- **Backend:** Python / Flask
- **Frontend:** Vanilla HTML/CSS/JS
- **Video:** HLS.js (no iframes)
- **Data:** TMDB API (metadata + posters)
- **Streams:** vidsrc.hair extraction chain

## Project Structure

```
zedflix/
├── app.py                 # Flask backend (API + extraction)
├── templates/
│   └── index.html         # Frontend UI
├── requirements.txt       # Python dependencies
├── Procfile              # Production server config
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python app.py

# Open browser
# http://localhost:5000
```

## Deploy

### Render.com (Free)
1. Push to GitHub
2. Connect repo on render.com
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### Railway.app
1. Push to GitHub
2. Connect repo on railway.app
3. Auto-detects Python + Procfile

### Heroku
```bash
heroku create zedflix
git push heroku main
```

## How It Works

1. **TMDB API** provides movie metadata (titles, posters, ratings)
2. When user clicks Play:
   - Backend fetches embed page from vidsrc.hair
   - Extracts signed token (Q object)
   - Calls `api.php?a=sources` to get server list
   - Calls `api.php?a=play` to get direct m3u8 URL
   - Returns stream URL to frontend
3. **HLS.js** plays the m3u8 stream in our custom player

---
Built with ❤️
