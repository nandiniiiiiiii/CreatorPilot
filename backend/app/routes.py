from flask import Blueprint, request, jsonify, send_file
from app.utils import extract_audio, generate_captions
import os
import whisper
import subprocess
import json

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

# Load Whisper Model
model = whisper.load_model("large")

video_path = None
json_path = None
output_path = None

@main.route("/", methods=["GET"])
def test():
    return jsonify({"message": "Test route is working!"}), 200


@main.route("/upload", methods=["POST"])
def upload():
    global video_path, json_path, output_path  # Declare them as global

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    video = request.files["file"]
    video_filename = video.filename
    video_path = os.path.join(UPLOAD_FOLDER, video_filename)
    audio_path = os.path.splitext(video_path)[0] + ".mp3"
    json_path = os.path.splitext(video_path)[0] + "_transcription.json"
    output_path = os.path.splitext(video_path)[0] + "_output.mp4"

    try:
        # Save the uploaded video
        video.save(video_path)

        # Extract audio from video
        audio_path = extract_audio(video_path)

        # Transcribe using Whisper with timestamps
        result = model.transcribe(audio_path, language="en", word_timestamps=True)

        # Extract full text from transcription
        full_text = " ".join(segment["text"] for segment in result["segments"])

        # Store captions as a list
        captions = [segment["text"] for segment in result["segments"]]

        # Store transcription data in JSON format
        transcription_data = {
            "video_file": video_filename,
            "language": result.get("language", "unknown"),
            "full_text": full_text,  # ✅ Added full text transcript
            "segments": result["segments"],  # ✅ Keeps detailed segment info
            "captions": captions  # ✅ List of individual caption texts
        }

        # Save JSON file
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(transcription_data, json_file, indent=4)

        return jsonify({
            "message": "Transcription successful",
            "json_file": json_path,
            "full_text": full_text,  # ✅ Returning full text in response
            "captions": captions
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/add_captions", methods=["POST"])
def add_captions():
    print("hello",video_path,json_path,output_path)
    if not os.path.exists(json_path):
        return jsonify({"error": "JSON file not found"})

    if not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"})

    # Read JSON file
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Generate SRT content dynamically
    srt_content = []
    for i, segment in enumerate(data["segments"], start=1):
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]

        def format_time(seconds):
            millis = int((seconds - int(seconds)) * 1000)
            return f"{int(seconds // 3600):02}:{int((seconds % 3600) // 60):02}:{int(seconds % 60):02},{millis:03}"

        srt_content.append(f"{i}\n{format_time(start_time)} --> {format_time(end_time)}\n{text}\n")

    # Create SRT file dynamically
    srt_path = os.path.splitext(video_path)[0] + "_captions.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    print(f"SRT file dynamically created at: {srt_path}")

    # Use FFmpeg to embed subtitles
    command = [
        "ffmpeg", "-i", video_path,
        "-vf", f"subtitles={srt_path}:force_style='Fontsize=24,PrimaryColour=&H00FFFF'",
        "-c:a", "copy", output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video with subtitles saved as {output_path}")
        return jsonify({"message": "Subtitles embedded successfully", "output_video": output_path})
    except subprocess.CalledProcessError as e:
        print("Error embedding subtitles:", e)
        return jsonify({"error": "Failed to embed subtitles"})