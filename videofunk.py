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

