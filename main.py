import re
import mutagen
from mutagen import StreamInfo

IN_FILE = "Александр Градский - Романс о влюбленных.utf8.cue"
DEBUG = True

KEYWORDS = [
    'PERFORMER',
    'TITLE',
    'FILE',
    'TRACK'
    'INDEX'
]

FILE_TYPES = [
    'WAVE'
]

TRACK_TYPE = [
    'AUDIO'
]


def parse_cue(cue_lines):

    i = 0
    result = {}
    length = len(cue_lines)

    while i < length:

        line = cue_lines[i].strip()
        i = i + 1

        # if the line contains a comment, starts with REM, just skip it
        if line.upper().startswith("REM"):
            continue

        # if the line contains FILE declaration...
        elif line.upper().startswith("FILE"):

            # ... get the file name and type...
            file_name = re.findall(r'\"(.+?)\"', line)[0]
            file_type = line.split()[-1]

            if "FILES" not in result:
                result["FILES"] = dict()
            file_index = len(result["FILES"])
            result["FILES"][file_index] = dict()
            result["FILES"][file_index]["FILE"] = file_name
            result["FILES"][file_index]["TYPE"] = file_type
            result["FILES"][file_index]["TRACKS"] = dict()
            #result["FILES"][file_index]["LENGTH"] = file_audio_length

            # ... and proceed to collect the tracks
            while i < length and not cue_lines[i].strip().upper().startswith("FILE"):
                line = cue_lines[i].strip()
                i = i + 1

                # if the line contains the track definition...
                if line.upper().startswith("TRACK"):

                    track_title = ""
                    track_performer = ""
                    track_index = ""

                    # ... get the track id and type...
                    track_id = int(line.split()[1])
                    track_type = line.split()[2]

                    # ... then proceed to collect track properties.
                    while i < length and not \
                            (cue_lines[i].strip().upper().startswith("TRACK") or
                             cue_lines[i].strip().upper().startswith("FILE")):

                        line = cue_lines[i].strip()
                        i = i + 1

                        if line.upper().startswith("TITLE"):
                            track_title = re.findall(r'\"(.+?)\"', line)[0]

                        elif line.upper().startswith("PERFORMER"):
                            track_performer = re.findall(r'\"(.+?)\"', line)[0]

                        elif line.upper().startswith("INDEX"):
                            track_index = line.split()[2]

                result["FILES"][file_index]["TRACKS"][track_id] = dict()
                result["FILES"][file_index]["TRACKS"][track_id]["TITLE"] = track_title
                result["FILES"][file_index]["TRACKS"][track_id]["PERFORMER"] = track_performer
                result["FILES"][file_index]["TRACKS"][track_id]["INDEX"] = track_index
                result["FILES"][file_index]["TRACKS"][track_id]["TYPE"] = track_type

        else:
            result[line[:line.find(" ")]] = re.findall(r'\"(.+?)\"', line[line.find(" ") + 1:])[0]





            # if key in KEYWORDS:
            #
            #     if key == "FILE":
            #
            #         if "FILES" not in al:
            #             al["FILES"] = {}
            #         cur_file_index = len(al["FILES"])
            #         al["FILES"][cur_file_index] = {}
            #         al["FILES"][cur_file_index]["FILE"] = re.findall(r'\"(.+?)\"', value)[0]
            #         file_type = value.split()[-1]
            #         if file_type in FILE_TYPES:
            #             al["FILES"][cur_file_index]["TYPE"] = file_type
            #         else:
            #             al["FILES"][cur_file_index]["TYPE"] = "Unknown file type"
            #         al["FILES"][cur_file_index]["TRACKS"] = {}
            #
            #     elif key == "TRACK":
            #         track_values = value.split()
            #         cur_track_index = int(track_values[1])
            #
            #     elif key == "PERFORMER":
            #         al[key] = re.findall(r'\"(.+?)\"', value)[0]
            #
            #     else:
            #         al[key] = re.findall(r'\"(.+?)\"', value)[0]
    return result


with open(IN_FILE, 'r') as in_file:
    lines = in_file.readlines()

album = parse_cue(lines)

print(album)


