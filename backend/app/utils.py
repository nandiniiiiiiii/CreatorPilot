import os
import speech_recognition as sr
import whisper
from moviepy.editor import VideoFileClip

def extract_audio(video_path):
    """Extracts audio from a video and saves it as a WAV file."""
    print(video_path)
    video = VideoFileClip(video_path)
    audio_path = video_path.replace(".mp4", ".wav")
    video.audio.write_audiofile(audio_path)
    return audio_path

def generate_captions(audio_path, model_size="base", fp16=True, task="transcribe"):
    # Normalize and ensure the audio path is absolute
    audio_path = os.path.abspath(audio_path)
    audio_path = os.path.normpath(audio_path)  # Normalize slashes for compatibility
    print(f"Normalized Audio Path: {audio_path}")

    # Check if the file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"The file at {audio_path} does not exist.")

    # Check the model path as well
    model_cache_dir = os.path.expanduser("~/.cache/whisper")  # Default cache path
    print(f"Whisper model cache directory: {model_cache_dir}")
    if not os.path.exists(model_cache_dir):
        print(f"Warning: Whisper model cache directory does not exist: {model_cache_dir}")

    # Load a smaller Whisper model for faster processing
    print(f"Loading Whisper model: {model_size}")
    model = whisper.load_model(model_size)

    # Transcribe the audio file with optimizations
    try:
        result = model.transcribe(audio_path, fp16=fp16, task=task)
    except Exception as e:
        raise RuntimeError(f"Error during transcription: {e}")

    # Extract and return captions
    captions = result.get("text", "")
    print(f"Generated Captions: {captions}")

    return captions