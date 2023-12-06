import pathlib
from pathlib import Path
import sys
import subprocess

# Extracts clip from video file at given time in/out in seconds.
def extract(input_path : str | pathlib.PosixPath,
            time_in : int | float,
            time_out : int | float, 
            output_path : pathlib.PosixPath = None) -> str | pathlib.PosixPath:

    if isinstance(input_path, str):
        string_return = True
        input_path = Path(input_path)
    if not output_path:
        output_path = input_path.with_name(f"{input_path.stem}_{time_in}_{time_out}{input_path.suffix}")
    else:
        output_path = Path(output_path) 

    cmd = ["ffmpeg", "-ss", f"{time_in}", "-i", f"{input_path}",
           "-to", f"{time_out}", f"{output_path}"]

    subprocess.call(cmd)

    return str(output_path) if string_return else output_path


if __name__ == "__main__":
    try:
        input_path = sys.argv[1]
        time_in = sys.argv[2]
        time_out = sys.argv[3]
    except IndexError:
        print("\n\nError. Must have input_path, time_in, and time_out args\n\n")

    extract(input_path, time_in, time_out)