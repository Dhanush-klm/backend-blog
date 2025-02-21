import streamlit as st
from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
import re
from pydantic import BaseModel

# Initialize FastAPI
app = FastAPI()

class VideoURL(BaseModel):
    url: str

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript using YouTubeTranscriptApi."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ""
        for entry in transcript_list:
            transcript_text += f"{entry['text']}\n"
        return transcript_text, None
    except Exception as e:
        return None, str(e)

@app.post("/get-transcript")
async def get_video_transcript(video: VideoURL):
    video_id = extract_video_id(video.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    transcript, error = get_transcript(video_id)
    
    if error:
        raise HTTPException(status_code=400, detail=f"Error fetching transcript: {error}")
    
    return {"transcript": transcript}

# Minimal Streamlit UI just to show it's working
st.title("YouTube Transcript API")
st.write("API is running! Use the /get-transcript endpoint for transcript extraction.")
st.markdown("""
### API Usage Example:
```bash
POST /get-transcript
{
    "url": "https://www.youtube.com/watch?v=your_video_id"
}
```
""")

# Optional: Add a simple test interface
if st.checkbox("Show Test Interface"):
    url = st.text_input("Test a YouTube URL:")
    if url:
        video_id = extract_video_id(url)
        if video_id:
            transcript, error = get_transcript(video_id)
            if transcript:
                st.text_area("Transcript:", transcript, height=200)
            else:
                st.error(f"Error: {error}")
