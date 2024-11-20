import os
import sys
import subprocess
import yt_dlp

# Set up directories
PROJECT_DIR = '/Users/harshgandhi/future'
AUDIO_DIR = os.path.join(PROJECT_DIR, 'audio')
TRANSCRIPTIONS_DIR = os.path.join(PROJECT_DIR, 'transcriptions')
WHISPER_MODEL = os.path.join(PROJECT_DIR, 'models', 'ggml-base.en.bin')
WHISPER_EXECUTABLE = os.path.join(PROJECT_DIR, 'whisper.cpp', 'main')

# Ensure directories exist
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTIONS_DIR, exist_ok=True)

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()

def convert_to_wav(input_path, output_path):
    command = [
        'ffmpeg', '-y', '-i', input_path, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', output_path
    ]
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return False

def transcribe_audio(audio_path, transcription_output_path):
    command = [
        WHISPER_EXECUTABLE,
        '-f', audio_path,
        '-m', WHISPER_MODEL,
        '-otxt',
        '-of', transcription_output_path
    ]
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Whisper error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python process_video.py <video_url>")
        sys.exit(1)

    video_url = sys.argv[1]
    print(f"Processing video URL: {video_url}")

    # Use yt-dlp to extract video information
    ydl_opts_info = {
        'ignoreerrors': True,
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
        except Exception as e:
            print(f"Error fetching info for {video_url}: {e}")
            sys.exit(1)

    video_id = info_dict.get('id')
    title = info_dict.get('title') or 'untitled'
    ext = info_dict.get('ext') or 'mp4'

    # Sanitize title and video_id for filenames
    sanitized_title = sanitize_filename(title)
    sanitized_video_id = sanitize_filename(video_id)

    # Set paths
    base_filename = f"{sanitized_title}_{sanitized_video_id}"
    download_path_template = os.path.join(AUDIO_DIR, f"{base_filename}.%(ext)s")
    audio_output_path = os.path.join(AUDIO_DIR, f"{base_filename}.wav")
    transcription_output_path = os.path.join(TRANSCRIPTIONS_DIR, f"{base_filename}.txt")

    # Check if WAV file already exists
    if not os.path.isfile(audio_output_path):
        # Try downloading audio
        print("Attempting to download audio...")
        ydl_opts_audio = {
            'format': 'bestaudio/best',
            'outtmpl': download_path_template,
            'ignoreerrors': True,
            'nooverwrites': False,
            'continuedl': True,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        audio_file_found = False
        with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
            try:
                ydl.download([video_url])
                # Get the actual downloaded file path
                info_dict_audio = ydl.extract_info(video_url, download=False)
                ext_audio = info_dict_audio.get('ext')
                audio_downloaded_file = os.path.join(AUDIO_DIR, f"{base_filename}.{ext_audio}")
                if os.path.isfile(audio_downloaded_file):
                    audio_file_found = True
            except Exception as e:
                print(f"Error downloading audio for {video_url}: {e}")
                audio_file_found = False

        if not audio_file_found:
            # Try downloading video
            print("Attempting to download video...")
            ydl_opts_video = {
                'format': 'worst',  # Lowest quality
                'outtmpl': download_path_template,
                'ignoreerrors': True,
                'nooverwrites': False,
                'continuedl': True,
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                try:
                    ydl.download([video_url])
                    # Get the actual downloaded file path
                    info_dict_video = ydl.extract_info(video_url, download=False)
                    ext_video = info_dict_video.get('ext')
                    video_downloaded_file = os.path.join(AUDIO_DIR, f"{base_filename}.{ext_video}")
                    if os.path.isfile(video_downloaded_file):
                        audio_file_found = True
                        input_file = video_downloaded_file
                except Exception as e:
                    print(f"Error downloading video for {video_url}: {e}")
                    sys.exit(1)
        else:
            input_file = audio_downloaded_file

        # Convert to WAV
        if audio_file_found:
            print("Converting to 16kHz WAV...")
            success = convert_to_wav(input_file, audio_output_path)
            if not success:
                print("Failed to convert to WAV.")
                sys.exit(1)
            else:
                print("Conversion successful.")
    else:
        print("WAV file already exists.")

    # Transcribe audio
    print("Starting transcription with whisper.cpp...")
    success = transcribe_audio(audio_output_path, transcription_output_path)
    if success:
        print(f"Transcription completed. Output saved to {transcription_output_path}")
    else:
        print("Transcription failed.")

if __name__ == "__main__":
    main()

