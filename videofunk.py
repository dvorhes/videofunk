import subprocess
import pickle
import json
import os
import shutil
# import general_app_functions as gaf
import pathlib
from pathlib import Path
import sys




def h264compress(input_path : pathlib.PosixPath,
                 output_path : pathlib.PosixPath = None) -> pathlib.PosixPath:

    if not output_path:
        output_path = Path.cwd()

    cmd = ["ffmpeg", "-ss", f"{time_in}", "-i", f"{input_path}",
           "-to", f"{time_out}", f"{output_path}"]
    subprocess.call(cmd)

    return output_path    

# Takes list of Video [0], and Audio [1]
def get_output_codec_cmd(reference_list):
    cmd = []
    # Get video:
    if reference_list[0] in ["prores_4444", "pro_res_4444", "prores4444"]:
        cmd.extend(["-c:v", "prores_ks", "-profile:v", "4"])
    # Get audio:
    if reference_list[1] in ['wav', 'WAV']:
        cmd.extend(["-c:a", "pcm_s16be"])
    return cmd


# Converts media file to google-speech-friendly WAV and puts it into the output directory.
def ffmpeg_convert(media_file, output_directory, conversion_profile):

    media_path = Path(media_file)
    # Available FFmpeg settings profiles.
    ffmpeg_profiles = {
                        "google_translate_wav": ["wav", ["ffmpeg", "-i", "media_file", "-y", "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000", "output_file_path"]],
                        "make_proxies_mov": ["mov", ["ffmpeg",  "-y", "-i", "media_file", "-vf", "scale=1280:720", "-c:v", "prores_ks", "-profile:v", f"{0}", "-c:a", "copy", "output_file_path"]],
                        "lt1080":  ["mov", ["ffmpeg",  "-y", "-i", "media_file", "-vf", "scale=1920:1080", "-c:v", "prores_ks", "-profile:v", f"{1}", "-c:a", "copy", "output_file_path"]]
                        }         

    for key, value in ffmpeg_profiles.items():
        if key == conversion_profile:
            output_ext = value[0]
            output_cmd_raw = value[1]

    if conversion_profile == "google_translate_wav":   
        output_filename = f"{media_path.stem}_for_transcription_wav.{output_ext}"
    elif conversion_profile == "make_proxies_mov":
        output_filename = f"{media_path.stem}.{output_ext}"
    elif conversion_profile == "lt1080":
        output_filename = f"{media_path.stem}.{output_ext}"

    output_file_path = Path(output_directory, output_filename)
    
    # # Debugging
    # print(f"media_file: {media_file}")
    # print(f"media_path.stem: {media_path.stem}")

    # print(f"output_directory: {output_directory}")
    # print(f"output_filename: {output_filename}")
    # print(f"output_file_path: {output_file_path}")


    # Swap the ffmpeg placeholder arguments for the real thing.
    cmd = [media_file if i=="media_file" else i for i in output_cmd_raw]
    cmd = [output_file_path if i=="output_file_path" else i for i in cmd]
    
    subprocess.call(cmd)
    return output_file_path


def get_settings(last_project_settings_uri, default_settings_uri):
    try:
        with open(last_project_settings_uri, "r") as settings:
            ps = json.load(settings)
        if len(ps['last_project_settings_file_uri']) > 0:
            print(f"Previous project settings detected. \nImporting settigns from {ps['last_project_settings_file_uri']}")
            with open(ps['last_project_settings_file_uri'], "r") as settings:
                this_project_settings = json.load(settings)
        else:
            print(
                f"No previous project settings detected. \nImporting default settigns from {default_settings_uri}")

            with open(default_settings_uri, "r") as default_settings:
                this_project_settings = json.load(default_settings)
    except (KeyError, FileNotFoundError) as e:
        print(f"Error detected. {e}")
        print(f"No previous project settings detected. \nImporting default settigns from {default_settings_uri}")

        with open(default_settings_uri, "r") as default_settings:
            this_project_settings = json.load(default_settings)
    return this_project_settings


def convert_seconds_to_timecode(_total_seconds, _frame_rate):
    frame_rate = _frame_rate
    total_seconds = int(_total_seconds)
    fraction_of_second = round(_total_seconds - total_seconds, 2)
    hours = total_seconds // 3600
    if hours == 0.0:
        hours = "00"
    elif 0 < hours < 10:
        hours = "0" + str(int(hours))
    else:
        pass
    minutes = total_seconds % 3600 // 60
    if minutes == 0:
        minutes = "00"
    elif 0 < minutes < 10:
        minutes = "0" + str(int(minutes))
    elif 10 <= minutes < 60:
        minutes = str(int(minutes))
    else:
        pass
    seconds = total_seconds % 3600 % 60
    if seconds == 0:
        seconds = "00"
    elif 0 < seconds < 10:
        seconds = "0" + str(int(seconds))
    elif 10 <= seconds < 60:
        seconds = str(int(seconds))
    else:
        pass
    frames = round(frame_rate * fraction_of_second)
    if frames == 0:
        frames = "00"
    elif 0 < frames < 10:
        frames = "0" + str(int(frames))
    elif 10 <= frames < round(frame_rate):
        frames = str(int(frames))
    else:
        pass
    timecode = f"{hours}:{minutes}:{seconds}:{frames}"
    return timecode


def absolute_frames_to_timecode(absolute_frames, _frame_rate):
    total_seconds = absolute_frames / _frame_rate
    timecode = convert_seconds_to_timecode(total_seconds, _frame_rate)
    return timecode

def ndf_timecode_to_absolute_frames(timecode, frame_rate):
    frames_hours = int(timecode[0:2]) * 60 * 60 * frame_rate
    frames_minutes = int(timecode[3:5]) * 60 * frame_rate
    frames_seconds = int(timecode[6:8]) * frame_rate
    frames_frames = int(timecode[9:11])
    total_frames = frames_hours + frames_minutes + frames_seconds + frames_frames
    return total_frames

def ndf_timecode_to_seconds_mmm_string(timecode, _frame_rate):
    total_frames = ndf_timecode_to_absolute_frames(timecode, _frame_rate)
    seconds = total_frames / _frame_rate
    return str(round(seconds,3))

def get_framerate(source_uri):
    cmd = f"ffprobe {source_uri} -v 0 -select_streams v -print_format flat -show_entries stream=r_frame_rate"
    data = str(subprocess.check_output(cmd, shell=True))
    data2 = data.split('_frame_rate="')[-1].split('"')[0]
    data3 = data2.split("/")
    data4 = float(data3[0]) / float(data3[1])
    if str(data4).split(".")[-1] == 0:
        frame_rate = int(str(data4).split(".")[0])
    else:
        frame_rate = data4
    print(f"Frame rate: {frame_rate}")
    return frame_rate


# Converts "1:15" style times to absolute number of seconds. 
def time_to_absolute(_time, frame_rate=23.976):
    _time = _time.split(":")
    if len(_time) == 4:
        hours = _time[0]
        minutes = _time[1]
        seconds = _time[2]
        frames = _time[3]
    if len(_time) == 3:
        hours = _time[0]
        minutes = _time[1]
        seconds = _time[2]
        frames = 0
    elif len(_time) == 2:
        hours = "00"
        minutes = _time[0]
        seconds = _time[1]
        frames = 0
    elif len(_time) == 1:
        hours = "00"
        minutes = "00"
        seconds = _time[0]
        frames = 0
    millieseconds = milliesecond_calc(frame_rate, frames)
    absolute_time = float(hours) * 60 * 60 + float(minutes) * 60 + float(seconds) + float(millieseconds)/1000
    return absolute_time

def milliesecond_calc(frame_rate_, remainder_frames):
    _millieseconds = 1000 * float(remainder_frames) / float(frame_rate_)
    if _millieseconds < 10:
        _millieseconds = str(0) + str(0) + str(round(_millieseconds))
    elif _millieseconds < 100:
        _millieseconds = str(0) + str(round(_millieseconds))
    elif _millieseconds < 1000:
        _millieseconds = str(round(_millieseconds))


    millieseconds_rounded = _millieseconds

    return millieseconds_rounded


def pickle_to_text(pickle_path):
    with open(pickle_path, 'rb') as ts:
        transcription_text = pickle.load(ts)
    name = f"{pickle_path.split('.')[0]}.txt"

    with open(name, 'w') as text:
        for line in transcription_text:
            text.write(str(line))

def convert_framerate_for_ffmpeg(frame_rate):
    if type(frame_rate) == int:
        return frame_rate
    else:
        frame_rate_rounded = round(frame_rate) * 1000
        safe_frame_rate = str(f"{frame_rate_rounded}/1001")
        return safe_frame_rate

# Generates thumbnail at time integer (seconds) or timecode string
def generate_thumbnail_at_time(video_path, time=6, milliesecond_ouput=True):

    video_path = Path(video_path)
    clip_data, raw_clip_data = ffprobe(video_path)

    if type(time) == int:
        timecode = convert_seconds_to_timecode(time, clip_data['frame_rate'])
        abs_frame = int(ndf_timecode_to_absolute_frames(timecode, clip_data['frame_rate']))
        if milliesecond_ouput:
            remainder_frames = int(timecode.split(":")[-1])
            millieseconds = milliesecond_calc(clip_data['frame_rate'], remainder_frames)
            timecode = f"{timecode[:8]}.{millieseconds}"

    elif type(time) == str:
        # TODO: Code for timecode. required format for -ss is HH:MM:SS.MILLISECONDS
        pass


    output_path = Path(f"{video_path.parent}/{video_path.stem}_frame{abs_frame}.png")

    ff_cmd = ['ffmpeg', "-y", '-i', f"{video_path}", "-ss", f"{timecode}",
           '-frames:v', "1", f"{output_path}"]

    subprocess.call(ff_cmd)

    return output_path


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
    # breakpoint()
    if file_ext.lower() in ["wav", "aac", "mp3", "aiff", "flac", "ogg"]:
        duration = float(data['streams'][0]['duration'])
        codec_type = "audio"
        frame_rate = None
        nb_frames = None
        width = None
        height = None
        creation_time = None
        # timecode_start = None
    elif file_ext.lower() in ["mp4", "mov", "avi", "mts"]:
        duration = float(data['streams'][0]['duration'])
        codec_type = "video"
        frame_rate = float(data['streams'][0]['r_frame_rate'].split("/")[0])/float(data['streams'][0]['r_frame_rate'].split("/")[1])
        nb_frames = float(data['streams'][0]['nb_frames'])
        width = data['streams'][0]['width']
        height = data['streams'][0]['height']
        creation_time = data['streams'][0]['tags']['creation_time']
        # timecode_start = data['streams'][0]['tags']['timecode']
    elif file_ext.lower() in ['jpg', 'jpeg', 'bmp', 'png', 'tiff', 'raw']:
        codec_type = "still"
        frame_rate = float(data['streams'][0]['r_frame_rate'].split("/")[0])/float(data['streams'][0]['r_frame_rate'].split("/")[1])
        duration = 1 / frame_rate
        nb_frames = 1
        width = data['streams'][0]['width']
        height = data['streams'][0]['height']
        creation_time = None
        # timecode_start = None
    
    clip_data = { 
                "path": media_file,
                "filename" : f"{file_name}.{file_ext}",
                "creation_time": 0,
                # "timecode_start": 0,
                "duration": duration,
                "codec_type": codec_type,
                "frame_rate": frame_rate,
                "nb_frames": nb_frames,
                "width": width,
                "height": height
                }
    return clip_data
    

# Makes proxies of all footage in Footage folder.
def proxify(project_root_folder, output_resolution=(1280,720), pro_res_preset=0, delete_proxies=False):
    if delete_proxies:
        for directory, sub, file in os.walk(project_root_folder):
            if directory.split("/")[-1] == "Proxies":
                shutil.rmtree(directory)
    else: 
        footage_folders = []
        for directory, subs, files in os.walk(project_root_folder):
            for file in files:
                if ".mp4" in file.lower() or ".mov" in file.lower() or ".mts" in file.lower():
                    # Make proxy folder in the original footage folder.
                    proxy_folder = gaf.make_folders(directory, "Proxies")
                    footage_path = os.path.join(directory, file)
                    ffmpeg_convert(footage_path, proxy_folder, "make_proxies_mov")


def timecode_arithmatic(tc1, tc2, frame_rate, operator="+", return_value="timecode"):
    tc1_frames = ndf_timecode_to_absolute_frames(tc1, frame_rate)
    tc2_frames = ndf_timecode_to_absolute_frames(tc2, frame_rate)
    if operator == "+":
        seconds = (tc1_frames + tc2_frames) / frame_rate
    elif operator == "-":
        seconds = (tc1_frames - tc2_frames) / frame_rate
    if return_value == "timecode":
        return convert_seconds_to_timecode(seconds, frame_rate)
    elif return_value == "seconds":
        return seconds

def join_audio(audio1, audio2, fade_duration, working_dir, output_filename=None):
    if output_filename == None:
        output_filename = "joined_audio.wav"

    output_path = os.path.join(working_dir, output_filename)
    ff_cmd = ["ffmpeg", "-y",
              "-i", f"{audio1}", "-i", f"{audio2}",
              "-filter_complex", f"acrossfade=d={fade_duration}",
              f"{output_path}"
              ]
    subprocess.call(ff_cmd)

    return output_path



def print_fn():
    print("Hi")

def sum_fn(a, b):
    print(a + b)

if __name__ == "__main__":
    args = sys.argv
    # args[0] = current file
    # args[1] = function name
    # args[2:] = function args : (*unpacked)
    globals()[args[1]](*args[2:])


# python demo.py print_fn
# python demo.py sum_fn 5 8

