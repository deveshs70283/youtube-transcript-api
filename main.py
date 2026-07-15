from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/transcript")
def get_transcript(video_id: str):

    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)

    result = []

    for line in transcript:
        result.append({
            "start": line.start,
            "duration": line.duration,
            "text": line.text
        })

    return result