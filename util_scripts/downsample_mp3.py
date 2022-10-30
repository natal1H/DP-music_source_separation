# -----------------------------------------------------------
# script to resample songs to 44100Hz
#
# 2022 Natália Holková
# xholko02@stud.fit.vutbr.cz
# -----------------------------------------------------------

# https://stackoverflow.com/questions/3537155/sox-fail-util-unable-to-load-mad-decoder-library-libmad-function-mad-stream
# https://superuser.com/questions/470720/convert-mp3-from-mono-to-stereo-using-lame/1082882#1082882

import os
import sys
import getopt
from mutagen.mp3 import MP3

ORIGINALS_LOC = "originals"
STEMS_LOC = "stems"


def get_arguments():
    # folder where are "originals" and "stems" located
    folder = os.path.abspath(os.getcwd())  # Default folder path is current working directory

    argument_list = sys.argv[1:]  # Remove 1st arg from the list
    options = "f:"  # Options
    long_options = ["Folder="]  # Long options

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)  # Parsing argument
        for currentArgument, currentValue in arguments:  # checking each argument
            if currentArgument in ("-f", "--Folder"):
                folder = currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))

    return folder


def get_mp3_sample_rate(song_loc):
    audio = MP3(song_loc)
    sample_rate = audio.info.sample_rate
    return sample_rate


if __name__ == '__main__':
    directory = get_arguments()  # command line args
    originals_dir = os.path.join(directory, ORIGINALS_LOC)
    stems_dir = os.path.join(directory, STEMS_LOC)

    # go over all files in originals directory
    for filename in os.listdir(originals_dir):
        f = os.path.join(originals_dir, filename)
        f_basename = os.path.basename(f)
        # checking if it is a file
        if os.path.isfile(f) and os.path.splitext(f_basename)[1] == ".mp3":
            rate = get_mp3_sample_rate(f)
            if rate != 44100:
                # convert to stereo
                new_f = os.path.splitext(f)[0] + "_new.mp3"
                print("File", f, "is wrong rate.", end="")
                os.system(f'cmd /c "sox {f} -r 44100 -c 2 -C 320 {new_f}"')
                os.remove(f)
                os.rename(new_f, f)
                print(" Converted.")

    print("ORIGINALS converted.")
    # go over all files in stems directory
    for filename in os.listdir(stems_dir):
        f = os.path.join(stems_dir, filename)
        f_basename = os.path.basename(f)
        # checking if it is a file
        if os.path.isfile(f) and os.path.splitext(f_basename)[1] == ".mp3":
            rate = get_mp3_sample_rate(f)
            if rate != 44100:
                # convert to stereo
                new_f = os.path.splitext(f)[0] + "_new.mp3"
                print("File", f, "is wrong rate.", end="")
                os.system(f'cmd /c "sox {f} -r 44100 -c 2 -C 320 {new_f}"')
                os.remove(f)
                os.rename(new_f, f)
                print(" Converted.")
    print("STEMS converted.")
