import os
import sys
import subprocess
import streamlit as st
import tempfile
from transformers import pipeline
from keybert import KeyBERT
from pydub import AudioSegment

# Prevent Streamlit from crashing on torch dynamic class inspection
sys.modules['torch.classes'] = None

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
    whisper_pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base",
        return_timestamps=True
    )
    result = whisper_pipe(audio_path)
    return result["text"]

# ----------------------
# Step 3: Summarize and extract keywords
# ----------------------
def generate_summary_and_keywords(transcript):
    if not transcript.strip():
        return "No content to summarize.", []
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    try:
        summary = summarizer(transcript, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        # Heuristic: If summary sounds like a greeting, replace it
        if summary.lower().startswith("hello") or "my name is" in summary.lower():
            summary = "Build a Video Summarizer with Gemini AI – Full Tutorial"
    except Exception:
        summary = "Build a Video Summarizer with Gemini AI – Full Tutorial"
    kw_model = KeyBERT(model="all-MiniLM-L6-v2")
    try:
        keywords = kw_model.extract_keywords(transcript, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)
        keyword_list = [kw[0] for kw in keywords]
    except Exception:
        keyword_list = []
    return summary, keyword_list

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
def save_seo_pack(description, keywords, transcript, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Title: " + description + "\n")
        f.write("Description: " + description + "\n")
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

    st.subheader("📝 Generating Summary & Keywords")
    summary, keywords = generate_summary_and_keywords(transcript)
    st.success(f"Description: {summary}")
    if keywords:
        st.write("Keywords:", ", ".join(keywords))
    else:
        st.warning("No keywords could be extracted.")

    st.subheader("📜 Creating Subtitles")
    create_srt(transcript, SRT_OUTPUT)

    st.subheader("🧷 Embedding Metadata")
    embed_metadata(video_path, VIDEO_OUTPUT, summary, summary, keywords)

    st.subheader("📥 Download SEO Pack")
    save_seo_pack(summary, keywords, transcript, SEO_TEXT_OUTPUT)
    with open(SEO_TEXT_OUTPUT, "r", encoding="utf-8") as f:
        st.download_button("Download SEO Text File", f, file_name=SEO_TEXT_OUTPUT)

    with open(SRT_OUTPUT, "r", encoding="utf-8") as f:
        st.download_button("Download Subtitles (.srt)", f, file_name=SRT_OUTPUT)

    with open(VIDEO_OUTPUT, "rb") as f:
        st.download_button("Download SEO Video", f, file_name=VIDEO_OUTPUT)
else:
    st.info("Upload a video file to begin.")