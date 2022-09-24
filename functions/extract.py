from pathlib import Path


def extract(input_path : str | pathlib.PosixPath,
                 time_in : int | float,
                 time_out : int | float, 
                 output_path : pathlib.PosixPath = None) -> str | pathlib.PosixPath:

    if isinstance(input_path, str):
        string_return = True
        input_path = Path(input_path)
    if not output_path:
        output_path = Path.cwd()
    else:
        output_path = Path(output_path)

    cmd = ["ffmpeg", "-ss", f"{time_in}", "-i", f"{input_path}",
           "-to", f"{time_out}", f"{output_path}"]
    subprocess.call(cmd)

    return str(output_path) if string_return else output_path