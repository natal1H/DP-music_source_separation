# -----------------------------------------------------------
# script to change originals/stems structure for
# structure like MUSDB18-HQ has
#
# 2022 Natália Holková
# xholko02@stud.fit.vutbr.cz
# -----------------------------------------------------------

import os
import sys
import getopt
import shutil

ORIGINALS_LOC = "originals"
STEMS_LOC = "stems"


def get_arguments():
    # folder where are "originals" and "stems" located
    folder = os.path.abspath(os.getcwd())  # Default folder path is current working directory
    new_folder = os.path.abspath(os.getcwd())  # Default folder path is current working directory

    argument_list = sys.argv[1:]  # Remove 1st arg from the list
    options = "f:n:"  # Options
    long_options = ["Folder=", "NewFolder="]  # Long options

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)  # Parsing argument
        for currentArgument, currentValue in arguments:  # checking each argument
            if currentArgument in ("-f", "--Folder"):
                folder = currentValue
            elif currentArgument in ("-n", "--NewFolder"):
                new_folder = currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))

    return folder, new_folder


def all_stems_exist(original_basename, stems_folder):
    without_ext = os.path.splitext(original_basename)[0]  # filename without extension
    if not os.path.isfile(os.path.join(stems_folder, without_ext + "-bass.mp3")):  # BASS
        print("No bass stem for file %s" % original_basename)
        return False
    if not os.path.isfile(os.path.join(stems_folder, without_ext + "-drums.mp3")):  # DRUMS
        print("No drums stem for file %s" % original_basename)
        return False
    if not os.path.isfile(os.path.join(stems_folder, without_ext + "-vocals.mp3")):  # VOCALS
        print("No vocals stem for file %s" % original_basename)
        return False
    if not os.path.isfile(os.path.join(stems_folder, without_ext + "-guitars.mp3")):  # GUITARS
        print("No guitars stem for file %s" % original_basename)
        return False
    if not os.path.isfile(os.path.join(stems_folder, without_ext + "-other.mp3")):  # OTHER
        print("No other stem for file %s" % original_basename)
        return False

    return True


def get_stem_locations(original_basename, stems_folder):
    """
    Make sure to call after verify with all_stems_exist() that stems really exist
    :param original_basename: Original song basename
    :param stems_folder: Folder where stems are located
    :return:
    """
    without_ext = os.path.splitext(original_basename)[0]  # filename without extension
    bass_loc = os.path.join(stems_folder, without_ext + "-bass.mp3")
    drums_loc = os.path.join(stems_folder, without_ext + "-drums.mp3")
    vocals_loc = os.path.join(stems_folder, without_ext + "-vocals.mp3")
    guitars_loc = os.path.join(stems_folder, without_ext + "-guitars.mp3")
    other_loc = os.path.join(stems_folder, without_ext + "-other.mp3")
    return bass_loc, drums_loc, vocals_loc, guitars_loc, other_loc


if __name__ == '__main__':
    directory, new_directory = get_arguments()  # command line args
    originals_dir = os.path.join(directory, ORIGINALS_LOC)
    stems_dir = os.path.join(directory, STEMS_LOC)

    for filename in os.listdir(originals_dir):
        f = os.path.join(originals_dir, filename)
        f_basename = os.path.basename(f)
        # checking if it is a file
        if os.path.isfile(f) and os.path.splitext(f_basename)[1] == ".mp3":
            # verify is all stems present
            if not all_stems_exist(f_basename, stems_dir):
                continue

            # get stems locations
            bass, drums, vocals, guitars, other = get_stem_locations(f_basename, stems_dir)

            # Create directory in new_directory
            basename_no_ext = os.path.splitext(f_basename)[0]
            new_song_dir = os.path.join(new_directory, basename_no_ext)
            os.mkdir(new_song_dir)
            # copy master file and rename
            shutil.copy(f, os.path.join(new_song_dir, "mixture.mp3"))
            # copy stems and rename
            shutil.copy(bass, os.path.join(new_song_dir, "bass.mp3"))  # bass
            shutil.copy(drums, os.path.join(new_song_dir, "drums.mp3"))  # drums
            shutil.copy(vocals, os.path.join(new_song_dir, "vocals.mp3"))  # vocals
            shutil.copy(guitars, os.path.join(new_song_dir, "guitars.mp3"))  # guitars
            shutil.copy(other, os.path.join(new_song_dir, "other.mp3"))  # other
