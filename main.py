#!/usr/bin/python3

import re
import os
import mutagen
from mutagen.easyid3 import EasyID3

IN_FILE = "Александр Градский - Романс о влюбленных.wav.utf8.cue"
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


# Transform the string of the form mm:ss:ff (mm - minutes, ss - seconds,
# ff - frames, 75 frames per second) to the float number of seconds
def str2sec(time_index):
    result = 0
    r1 = time_index.split(":")
    if len(r1) == 3:
        result = int(r1[0]) * 60 + int(r1[1]) + (int(r1[2]) + 1)/75
    result = round(result, 2)
    return result


# Transform the float number of seconds to the string of form mm:ss:ff
# mm - minutes, ss - seconds, ff - frames (75 frames per second)
def sec2str(secs):
    minutes = int(secs // 60)
    seconds = int((secs % 60) // 1)
    frames = int((secs % 60) % 1 * 75)
    result = f'{minutes:02}' + ':' + f'{seconds:02}' + ':' + f'{frames:02}'
    return result


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

            # ... total length of the file
            obj_in_file = mutagen.File(file_name)
            result["FILES"][file_index]["LENGTH"] = round(obj_in_file.info.length, 2)

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

    # calculate the length of each track
    disk_track_counter = 0
    for file_id, file in result['FILES'].items():
        for track_id, track in file['TRACKS'].items():
            disk_track_counter = disk_track_counter + 1
            if disk_track_counter + 1 in file['TRACKS']: # the tracks must be numbered consecutively
                track_length = sec2str(str2sec(file['TRACKS'][disk_track_counter + 1]['INDEX']) - str2sec(track['INDEX']))
            else:
                track_length = sec2str(file['LENGTH'] - str2sec(track['INDEX']))
            track["LENGTH"] = track_length

    return result


with open(IN_FILE, 'r') as in_file:
    lines = in_file.readlines()

album = parse_cue(lines)
print(album)

for file_id, file in album['FILES'].items():
    in_file_name = file['FILE']
    for track_id, track in file['TRACKS'].items():
        out_file_name = f'{track_id:02}. ' + track['TITLE'] + '.mp3'

        cmd = 'ffmpeg ' + \
              '-ss ' + str(str2sec(track['INDEX'])) + ' '\
              '-t ' + str(str2sec(track['LENGTH'])) + ' '\
              '-i "' + in_file_name + '" ' + \
              '-codec:a libmp3lame -b:a 320k ' + \
              '"' + out_file_name + '"'
        print(cmd)
        os.system(cmd)
        
        obj_mp3_tags = EasyID3(out_file_name)
        obj_mp3_tags['album'] = album['TITLE']
        obj_mp3_tags['artist'] = track['PERFORMER']
        obj_mp3_tags['title'] = track['TITLE']
        obj_mp3_tags.save()


