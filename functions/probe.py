from pathlib import Path
import subprocess
import json


def ffprobe(media_file):
    print(f"\nRunning ffprobe on {media_file}")

    media_file = Path(media_file)
    media_file_string = str(media_file)
    file_name = f"{media_file.stem}"
    file_ext = media_file.suffix.lstrip(".")
    file_directory = str(media_file.parent) + "/"

    ffmpeg_cmd = ["ffprobe", "-v", "error", 
                  "-show_streams", "-of", "json",
                  f"{media_file_string}"]

    result = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)
    data = json.loads(result.communicate()[0].decode().strip())

    if file_ext.lower() in ["wav", "aac", "mp3", "aiff", "flac", "ogg"]:
        duration = float(data['streams'][0]['duration'])
        codec_type = "audio"
        frame_rate = None
        nb_frames = None
        width = None
        height = None
        creation_time = None

    elif file_ext.lower() in ["mp4", "mov", "avi", "mts"]:
        duration = float(data['streams'][0]['duration'])
        codec_type = "video"
        frame_rate = float(data['streams'][0]['r_frame_rate'].split("/")[0])/float(data['streams'][0]['r_frame_rate'].split("/")[1])
        nb_frames = float(data['streams'][0]['nb_frames'])
        width = data['streams'][0]['width']
        height = data['streams'][0]['height']
        creation_time = None

    elif file_ext.lower() in ['jpg', 'jpeg', 'bmp', 'png', 'tiff', 'raw']:
        codec_type = "still"
        frame_rate = float(data['streams'][0]['r_frame_rate'].split("/")[0])/float(data['streams'][0]['r_frame_rate'].split("/")[1])
        duration = 1 / frame_rate
        nb_frames = 1
        width = data['streams'][0]['width']
        height = data['streams'][0]['height']
        creation_time = None

    else:
        raise Exception("Incompatible media.") 

    clip_data = { 
                "path": media_file,
                "filename" : f"{file_name}.{file_ext}",
                "creation_time": 0,
                "duration": duration,
                "codec_type": codec_type,
                "frame_rate": frame_rate,
                "nb_frames": nb_frames,
                "width": width,
                "height": height
                }

    print("\n\n")
    for key, value in clip_data.items():
        print(f"{key}: {value}")
    print("\n\n")
    
    return clip_data
    
