# youtube-heatmap-api

Extracts and caches the raw YouTube "most replayed" heatmap container HTML using Playwright.

## Setup

```bash
npm install
npx playwright install chromium
```

## Run

```bash
npm run dev    # nodemon, auto-restart
npm start      # plain node
```

Server listens on `PORT` env var or `3000`.

## Usage

`POST /extract-heatmap`

```bash
curl -X POST http://localhost:3000/extract-heatmap \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

Response:

```json
{
  "videoId": "dQw4w9WgXcQ",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "title": "...",
  "duration": 212,
  "heatmapHtml": "<div class=\"ytp-heat-map-container\">...</div>",
  "createdAt": "2026-07-15T00:00:00.000Z",
  "cached": false
}
```

Results are cached in `cache/<videoId>.json`. Repeat requests for the same video are served
straight from the cache file without launching a browser (`"cached": true`).
