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


# 05:15:22.623489 style times to absolute float.
def timecode_with_decimal_to_float(_time):
    _time = _time.split(":")
    if len(_time) == 4:
        hours = _time[0]
        minutes = _time[1]
        seconds = _time[2]
        remainder = _time[3]
    if len(_time) == 3:
        hours = _time[0]
        minutes = _time[1]
        seconds = _time[2]
        remainder = 0
    elif len(_time) == 2:
        hours = "00"
        minutes = _time[0]
        seconds = _time[1]
        remainder = 0
    elif len(_time) == 1:
        hours = "00"
        minutes = "00"
        seconds = _time[0]
        remainder = 0
    absolute_time_whole = float(hours) * 60 * 60 + float(minutes) * 60 + float(seconds)
    absolute_time_remainder = float("." + f"{remainder}")
    absolute_time = float(absolute_time_whole + absolute_time_remainder)
    return absolute_time


# Converts "1:15" style times to absolute number of seconds. 
def timecode_to_absolute(_time, frame_rate=23.976):
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