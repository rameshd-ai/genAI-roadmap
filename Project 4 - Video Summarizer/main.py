import os
import sys
import subprocess
import streamlit as st
import tempfile
import json
from openai import OpenAI
from keybert import KeyBERT
from pydub import AudioSegment
from transformers import pipeline


# Prevent Streamlit from crashing on torch dynamic class inspection
sys.modules['torch.classes'] = None

# Load OpenAI API Key from key.json
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

os.environ["OPENAI_API_KEY"] = key_data["openai_api_key"]

# ----------------------
# CONFIGURATION
# ----------------------
AUDIO_OUTPUT = "audio.wav"
SRT_OUTPUT = "subtitles.srt"
SEO_TEXT_OUTPUT = "seo_pack.txt"
VIDEO_OUTPUT = "seo_friendly_video.mp4"

# ----------------------
# Step 1: Extract Audio using ffmpeg
# ----------------------
def extract_audio(video_path, audio_path):
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
    ]
    subprocess.run(command, check=True)

# ----------------------
# Step 2: Transcribe Audio with Whisper
# ----------------------
def transcribe_audio(audio_path):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    audio_file = open(audio_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

# ----------------------
# Step 3: Summarize and extract keywords
# ----------------------
def generate_summary_and_keywords(transcript):
    import openai
    import re
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not transcript.strip():
        return "No content to summarize.", "", []
    try:
        prompt = (
            "Given the following video transcript, extract and return ONLY:\n"
            "Title: [A compelling, SEO-optimized title under 70 characters]\n"
            "Description: [A concise, informative summary of the video content (1–2 sentences)]\n\n"
            "Avoid using intros like 'Hello, my name is...'. Focus on the core topic or value delivered.\n\n"
            f"Transcript:\n{transcript}"
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an SEO and YouTube expert."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message["content"].strip()

        # Extract using prefix matching
        title = ""
        summary = ""
        for line in content.splitlines():
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[1].strip()
            elif line.lower().startswith("description:") or line.lower().startswith("summary:"):
                summary = line.split(":", 1)[1].strip()

        if not title or len(title) < 5:
            title = "Video Summarizer with Gemini AI – Full Tutorial"
        if not summary:
            summary = title
    except Exception:
        title = "Video Summarizer with Gemini AI – Full Tutorial"
        summary = title

    kw_model = KeyBERT(model="all-MiniLM-L6-v2")
    try:
        keywords = kw_model.extract_keywords(transcript, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)
        keyword_list = [kw[0] for kw in keywords]
    except Exception:
        keyword_list = []
    return title, summary, keyword_list

# ----------------------
# Step 4: Create Subtitles (naive, 1 chunk)
# ----------------------
def create_srt(transcript, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("1\n00:00:00,000 --> 00:00:10,000\n")
        f.write(transcript + "\n")

# ----------------------
# Step 5: Embed Metadata into Video
# ----------------------
def embed_metadata(input_video, output_video, title, description, keywords):
    metadata_args = [
        "-metadata", f"title={title}",
        "-metadata", f"description={description}",
        "-metadata", f"keywords={','.join(keywords)}"
    ]
    command = [
        "ffmpeg", "-y", "-i", input_video
    ] + metadata_args + [output_video]
    subprocess.run(command, check=True)

# ----------------------
# Step 6: Save SEO Summary
# ----------------------
def save_seo_pack(title, keywords, transcript, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Title: " + title + "\n")
        f.write("Description: " + title + "\n")
        f.write("Keywords: " + ", ".join(keywords) + "\n")
        f.write("Transcript:\n" + transcript + "\n")

# ----------------------
# Streamlit App
# ----------------------
st.title("🎬 Video SEO Enhancer")

video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if video_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        video_path = temp_video.name

    st.video(video_path)
    st.subheader("🔈 Extracting Audio")
    try:
        extract_audio(video_path, AUDIO_OUTPUT)
        st.success("Audio extracted successfully.")
    except Exception as e:
        st.error(f"Failed to extract audio: {e}")
        st.stop()

    st.subheader("🧠 Transcribing Audio")
    transcript = transcribe_audio(AUDIO_OUTPUT)
    st.text_area("Transcript", transcript, height=200)

    st.subheader("📝 Generating SEO Title & Keywords")
    title, summary, keywords = generate_summary_and_keywords(transcript)
    st.success(f"Title: {title}")
    st.info(f"Description: {summary}")
    if keywords:
        st.write("Keywords:", ", ".join(keywords))
    else:
        st.warning("No keywords could be extracted.")

    st.subheader("📜 Creating Subtitles")
    create_srt(transcript, SRT_OUTPUT)

    st.subheader("🧷 Embedding Metadata")
    embed_metadata(video_path, VIDEO_OUTPUT, title, summary, keywords)

    st.subheader("📥 Download SEO Pack")
    save_seo_pack(title, keywords, transcript, SEO_TEXT_OUTPUT)
    with open(SEO_TEXT_OUTPUT, "r", encoding="utf-8") as f:
        st.download_button("Download SEO Text File", f, file_name=SEO_TEXT_OUTPUT)

    with open(SRT_OUTPUT, "r", encoding="utf-8") as f:
        st.download_button("Download Subtitles (.srt)", f, file_name=SRT_OUTPUT)

    with open(VIDEO_OUTPUT, "rb") as f:
        st.download_button("Download SEO Video", f, file_name=VIDEO_OUTPUT)
else:
    st.info("Upload a video file to begin.")
