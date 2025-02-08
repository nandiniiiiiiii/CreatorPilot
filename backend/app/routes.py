from flask import Blueprint, request, jsonify
from app.utils import extract_audio, generate_captions
import os
import whisper

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Whisper Model
model = whisper.load_model("large")

@main.route("/", methods=["GET"])
def test():
    return jsonify({"message": "Test route is working!"}), 200


@main.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    video = request.files["file"]
    if video:
        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        audio_path = os.path.splitext(video_path)[0] + ".mp3"
        captions_path = os.path.splitext(video_path)[0] + "_captions.srt"

        try:
            # Extract audio
            audio_path = extract_audio(video_path)
            
            # Transcribe using Whisper in English with timestamps
            result = model.transcribe(audio_path, language="en", word_timestamps=True)
            
            # Convert transcript to SRT format
            srt_captions = []
            for i, segment in enumerate(result["segments"]):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                
                start_time = f"{int(start // 3600):02}:{int((start % 3600) // 60):02}:{int(start % 60):02},{int((start % 1) * 1000):03}"
                end_time = f"{int(end // 3600):02}:{int((end % 3600) // 60):02}:{int(end % 60):02},{int((end % 1) * 1000):03}"
                
                srt_captions.append(f"{i+1}\n{start_time} --> {end_time}\n{text}\n")
            
            # Save captions to a file in SRT format
            with open(captions_path, "w", encoding="utf-8") as f:
                f.writelines(srt_captions)
            
            return jsonify({"captions": srt_captions, "file": captions_path})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file"}), 400
