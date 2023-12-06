from pathlib import Path
from .timecode import timecode_arithmatic, absolute_frames_to_timecode

class EDL:
    def __init__(self, edl_name, export_directory):
        self.edl_path = Path(export_directory, edl_name).with_suffix(".edl")
        
        self.decision_number = 0
        self.playhead = "00:00:00:00" 
        self.frame_rate = None

        edl = open(self.edl_path, "w")
        edl.write(f"TITLE: {self.edl_path.stem}\n")
        edl.write("FCM: NON-DROP FRAME\n\n")
        edl.close()

    def write_to_edl(self,
                     clip_data,
                     source_in="00:00:00:00",
                     source_out=None,
                     timeline_in=None,
                     timeline_out=None):
        if not source_out:
            source_out = absolute_frames_to_timecode(clip_data['nb_frames'], clip_data['frame_rate'])
        if clip_data['codec_type'] == "still":
            source_out = "00:00:00:01"

        if not timeline_in:
            timeline_in = self.playhead

        if not timeline_out:
            timeline_out = timecode_arithmatic(self.playhead, source_out, clip_data['frame_rate'])
        
        decision_line_main = f"{str(self.decision_number + 1)}  AX       V     C        {source_in} {source_out} {timeline_in} {timeline_out}\n"
        decision_line_speed_event = f"M2 AX             000.0                00:00:00:00\n"
        decision_line_comment = f"* FROM clip_data NAME: {clip_data['filename']}\n\n"
        print("writing to EDL. ")
        with open(self.edl_path, "a") as edl:
            edl.write(decision_line_main)
            if clip_data['codec_type'] == "still":
                edl.write(decision_line_speed_event)
            edl.write(decision_line_comment)
        self.playhead = timeline_out

