from fastapi import FastAPI, HTTPException
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/transcript")
def get_transcript(video_id: str):

    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)
    except (TranscriptsDisabled, VideoUnavailable, CouldNotRetrieveTranscript):
        raise HTTPException(status_code=404, detail="Transcript not available for this video")

    # Prefer English if it exists, otherwise fall back to whatever language YouTube has.
    try:
        transcript = transcript_list.find_transcript(["en"])
    except NoTranscriptFound:
        transcript = next(iter(transcript_list), None)
        if transcript is None:
            raise HTTPException(status_code=404, detail="Transcript not available for this video")

    try:
        fetched = transcript.fetch()
    except CouldNotRetrieveTranscript:
        raise HTTPException(status_code=404, detail="Transcript not available for this video")

    result = []

    for line in fetched:
        result.append({
            "start": line.start,
            "duration": line.duration,
            "text": line.text
        })

    return result