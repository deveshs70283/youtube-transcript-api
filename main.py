import os

from fastapi import FastAPI, HTTPException
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
    IpBlocked,
    RequestBlocked,
)
from youtube_transcript_api.proxies import WebshareProxyConfig

app = FastAPI()

BLOCKED_DETAIL = (
    "YouTube is blocking transcript requests from this server's IP address. "
    "This is a known limitation on cloud hosts and requires routing requests "
    "through a proxy to fix."
)

# Proxy is optional: only used if both env vars are set on the host (e.g. Render).
# Locally, or if unset, requests go out directly with no proxy.
_proxy_username = os.environ.get("WEBSHARE_PROXY_USERNAME")
_proxy_password = os.environ.get("WEBSHARE_PROXY_PASSWORD")
_proxy_config = (
    WebshareProxyConfig(proxy_username=_proxy_username, proxy_password=_proxy_password)
    if _proxy_username and _proxy_password
    else None
)

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/transcript")
def get_transcript(video_id: str):

    api = YouTubeTranscriptApi(proxy_config=_proxy_config)

    # IpBlocked/RequestBlocked are subclasses of CouldNotRetrieveTranscript, so
    # they must be checked first or they'd be swallowed by the generic case below.
    try:
        transcript_list = api.list(video_id)
    except (IpBlocked, RequestBlocked):
        raise HTTPException(status_code=503, detail=BLOCKED_DETAIL)
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
    except (IpBlocked, RequestBlocked):
        raise HTTPException(status_code=503, detail=BLOCKED_DETAIL)
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