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

# FastAPI endpoint (can be used separately as an API)
@app.post("/get-transcript")
async def get_video_transcript(video: VideoURL):
    video_id = extract_video_id(video.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    transcript, error = get_transcript(video_id)
    
    if error:
        raise HTTPException(status_code=400, detail=f"Error fetching transcript: {error}")
    
    return {"transcript": transcript}

# Streamlit UI
def main():
    st.title("YouTube Video Transcript Extractor")
    
    # Input field for YouTube URL
    youtube_url = st.text_input("Enter YouTube Video URL:")
    
    if youtube_url:
        video_id = extract_video_id(youtube_url)
        
        if video_id:
            # Get transcript
            with st.spinner("Fetching transcript..."):
                transcript, error = get_transcript(video_id)
                
                if transcript:
                    st.success("Transcript fetched successfully!")
                    
                    # Display transcript in an expandable box
                    with st.expander("View Transcript", expanded=True):
                        st.text_area("", value=transcript, height=400)
                    
                    # Add download button
                    st.download_button(
                        label="Download Transcript",
                        data=transcript,
                        file_name="transcript.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"Error fetching transcript: {error}")
        else:
            st.error("Invalid YouTube URL. Please check the URL and try again.")
    
    # Add API documentation
    st.markdown("""
    ---
    ### API Usage
    This app also provides an API endpoint that you can use:
    
    **Endpoint:** `/get-transcript`
    
    **Method:** POST
    
    **Request Body:**
    ```json
    {
        "url": "https://www.youtube.com/watch?v=your_video_id"
    }
    ```
    
    **Response:**
    ```json
    {
        "transcript": "... transcript text ..."
    }
    ```
    
    ### Instructions:
    1. Paste a YouTube video URL in the input field above
    2. The app will fetch available transcript
    3. You can view and download the transcript
    
    ### Note:
    - Only videos with available transcripts/subtitles can be processed
    - Some videos may have transcripts disabled by the creator
    """)

if __name__ == "__main__":
    main()
