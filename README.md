# VideoTranscriber
This python code can be used to download any video from youtube, rumble etc. using yt-dlp, extract audio from it using ffmpeg, convert it to the required bitrate wav file and transcribe them using whisper model. Then you can use your AI tool to summarize it.
This will help understand any video very quickly. Works only for videos in engnlish. Python code needs to be changed and whisper model needs to be updated in order to consume other language videos.

You will need locally installed yt-dlp, ffmpeg and whisper model. Following folder structure is needed wherever you choose to put the python script.

- audio
- processed
- transcriptions
- video_Transcriber.py
- models
- whisper.cpp
