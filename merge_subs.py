# This script is used to merge all the individual subtitles files
# from all the chapters into one subtitles file.

# All parameters should be changed directly in this file

# LICENSE: GNU General Public License v3.0

########################
#  PARAMETERS SECTION  #
########################

# This list contains lists of names of the subtitles files
# Those nested lists should be sorted already.
# The file names must be exactly the same as defined in the lists.
SUB_ORDERS = [
    # Original Order
    [
        "Intro",
        "Prologue",
        "Broken",
        "The Experiment",
        "The Embassy",
        "The Party",
        "First Interview",
        "Welcome to the CIA",
        "Hunted",
        "My Imaginary Friend",
        "The Condenser",
        "Homeless",
        "First Night",
        "Like Other Girls",
        "Alone",
        "Navajo",
        "Separation",
        "The Dinner",
        "Night Session",
        "The Mission",
        "Old Friends - Norah",
        "Briefing - Dragons Hideout",
        "Hauntings",
        "Black Sun",
        "Epilogue"
    ],

    # Chronological Order
    [
        "Intro",
        "Prologue",
        "My Imaginary Friend",
        "First Interview",
        "First Night",
        "Alone",
        "The Experiment",
        "Night Session",
        "Hauntings",
        "The Party",
        "Like Other Girls",
        "The Condenser",
        "Separation",
        "Welcome to the CIA",
        "The Embassy",
        "The Dinner",
        "The Mission",
        "Hunted",
        "Homeless",
        "Broken",
        "Navajo",
        "Old Friends - Norah",
        "Briefing - Dragons Hideout",
        "Black Sun",
        "Epilogue"
    ],

    # Remixed Order
    [
        "Intro",
        "Prologue",
        "Broken",
        "The Experiment",
        "My Imaginary Friend",
        "First Interview",
        "First Night",
        "Alone",
        "The Party",
        "Like Other Girls",
        "The Condenser",
        "Separation",
        "Welcome to the CIA",
        "The Embassy",
        "The Dinner",
        "The Mission",
        "Hunted",
        "Homeless",
        "Navajo",
        "Old Friends - Norah",
        "Night Session",
        "Briefing - Dragons Hideout",
        "Hauntings",
        "Black Sun",
        "Epilogue"
    ]
]

# Path to directory that contains all videos.
# All videos must have their names the same as their subtitles files.
VIDEOS_PATH = ""

# Path to directory that contains all subtitles files.
SUBS_PATH = "en-GB/Chapters/"

##################
#  CODE SECTION  #
##################

import os
import shutil

def print_err(time):
    """
    Print an error message for wrong time format.
    """
    print(
        f"\n'{time}' is a wrong time format, please check again.\n"
        f"The time format is HH:MM:SS.mmm (H is hour, M is minute, S is second, and m is milisecond)\n"
        f"All values should be numeric values"
    )

def get_video_duration(path):
    """
    Returns a video's duration (in milisecond)
    """
    import cv2
    video = cv2.VideoCapture(path)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = video.get(cv2.CAP_PROP_FPS)

    return frame_count / fps * 1000 - 50 # -50 is the offset, can be changed

def load_subs(path):
    """
    Load all lines and timing from subtitles file
    """
    file = open(path, "r")
    lines = file.read().splitlines()

    LINES = []

    new_line = False
    start_time = 0
    end_time = 0
    the_lines = ""
    position = ""

    for line in lines:
        if line == "":
            if (the_lines != "") and (start_time != 0) and (end_time != 0):
                new_line = False
                LINES.append((start_time, end_time, the_lines, position))
                start_time = 0
                end_time = 0
                the_lines = ""
                position = ""
        if " --> " in line:
            time = line.split(" --> ")
            start_time = time_to_millisec(time[0])
            end_time = time[1].split(" ")               # Split again to avoid the position markup that comes after the end time, i.e. position:80% line:20%
            if len(end_time) > 1:
                position = " ".join(end_time[1:])       # Save position markup, i.e. position:80% line:20%
            end_time = time_to_millisec(end_time[0])    # Get the real end time
            new_line = True
            continue
        if new_line:
            the_lines += line + "\n"

    return LINES

def shift_subs(base, lines):
    """
    Shift all timings of all lines.
    base is a number (millisecond)
    lines is a list of tuples (start_time, end_time, lines, position)
    """

    RET_LINES = []
    for line in lines:
        start_time, end_time, lines, position = line
        RET_LINES.append((start_time + base, end_time + base, lines, position))
    
    return RET_LINES

def time_to_millisec(time):
    """
    Convert a time string (HH:MM:SS.mmm format) into milisecond (integer)
    Each section can have more than two/three digits.
    """

    milisec = str(time).split(".")

    if len(milisec) == 1:
        if milisec[0].isnumeric():
            return milisec[0]
        else:
            print_err(time)
            return -1
    elif len(milisec) == 2:
        h_m_s = milisec[0]
        milisec = milisec[1]
    else:
        print_err(time)
        return -1

    if not milisec.isnumeric():
        print_err(time)
        return -1

    t = h_m_s.split(":")
    hour = "0"
    min = "0"
    sec = "0"

    if len(t) > 3:
        print_err(time)
        return -1

    if len(t) == 3:
        hour = t[0]
        min = t[1]
        sec = t[2]
    elif len(t) == 2:
        min = t[0]
        sec = t[1]
    else:
        sec = t[0]

    if not hour.isnumeric():
        print_err(time)
        return -1

    if not min.isnumeric():
        print_err(time)
        return -1

    if not sec.isnumeric():
        print_err(time)
        return -1

    # Make sure that the fraction is interpreted correctly
    # For instance in the number 1.23, it means "1 second and 230 miliseconds"
    # So basically this "if" statement will prevent the script
    # from interpreting .23 as only 23, when in fact it should be 230.
    if int(milisec) < 100:
        milisec = int(milisec) * 10

    return int(hour) * 3600000 + int(min) * 60000 + int(sec) * 1000 + int(milisec)

def millisec_to_time(millisec):
    """
    Returns a string with time format HH:MM:SS.mmm from an integer (in millisecond)
    """
    hour = int(millisec / 3600000)
    millisec -= hour * 3600000
    min = int(millisec / 60000)
    millisec -= min * 60000
    sec = int(millisec / 1000)
    millisec -= sec * 1000
    millisec = int(millisec)

    # Pad millisec to fit three digits
    if millisec <= 0:
        millisec = "000"
    elif millisec < 10:
        millisec *= 100
    elif millisec < 100:
        millisec *= 10
    elif millisec >= 1000:
        millisec = str(millisec)[:3]

    hour = str(hour).zfill(2)
    min = str(min).zfill(2)
    sec = str(sec).zfill(2)

    return f"{hour}:{min}:{sec}.{millisec}"

def main():
    answer = ""
    if os.path.isdir("output"):
        print(
            "WARNING: the 'ouput' directory is already existed.\n"
            "Running this script will DELETE ALL of its existing content.\n"
            "Do you want to proceed? (Y/N)"
        )
        while 1:
            answer = input("Your Answer: ")
            if answer.lower() == "n":
                return 0
            if answer.lower() == "y":
                break
        try:
            shutil.rmtree("output")
            print("'output' directory deleted.")
        except:
            print("Something's wrong. Cannot remove directory 'output'. Exiting...")
            return -1
    try:
        os.mkdir("output")
        print("'output'directory created.")
    except:
        print("Something's wrong. Cannot create directory 'output'. Exiting...")
        return -1

    # Get videos' durations
    print("Getting all videos duration...")
    DURATION = {}
    for root, _, files in os.walk(VIDEOS_PATH):
        for file in files:
            if file.endswith(".mkv"):   # Change this to appropriate video extension
                path = os.path.join(root, file)
                file_name, _ = os.path.splitext(file)
                DURATION[file_name] = get_video_duration(path) 
    
    # Get all subtitles
    print("Loading all subtitles files...")
    SUBS = {}
    for root, _, files in os.walk(SUBS_PATH):
        for file in files:
            if file.endswith("vtt"):    # Change this to appropriate subtitles extension
                path = os.path.join(root, file)
                file_name, _ = os.path.splitext(file)
                SUBS[file_name] = load_subs(path)
    
    print("Merging...")
    for count, SUB in enumerate(SUB_ORDERS):
        shift_amount = 0
        output_file_path = f"output/{count}.vtt"
        f = open(output_file_path, "w")
        f.write("WEBVTT\n\n")
        for sub in SUB:
            shifted_subs = shift_subs(shift_amount, SUBS[sub])
            for line in shifted_subs:
                start_time, end_time, lines, position = line
                start_time = millisec_to_time(start_time)
                end_time = millisec_to_time(end_time)
                f.write(f"{start_time} --> {end_time} {position}\n{lines}\n")
            shift_amount += DURATION[sub]
        f.close()
    
    print("DONE!")

if __name__ == "__main__":
    main()
