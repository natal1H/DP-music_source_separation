# -----------------------------------------------------------
# script to create csv for songs dataset
#
# 2022 Natália Holková
# xholko02@stud.fit.vutbr.cz
# -----------------------------------------------------------

import os
import sys
import getopt
import pandas as pd
from mutagen.mp3 import MP3

ORIGINALS_LOC = "originals"
STEMS_LOC = "stems"


def get_arguments():
    # folder where are "originals" and "stems" located
    folder = os.path.abspath(os.getcwd())  # Default folder path is current working directory
    csv = os.path.join(os.path.abspath(os.getcwd()), "dataset_info.csv")

    argument_list = sys.argv[1:]  # Remove 1st arg from the list
    options = "f:c:"  # Options
    long_options = ["Folder=", "CSV="]  # Long options

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)  # Parsing argument
        for currentArgument, currentValue in arguments:  # checking each argument
            if currentArgument in ("-f", "--Folder"):
                folder = currentValue
            elif currentArgument in ("-c", "--CSV"):
                csv = currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))

    return folder, csv


def create_empty_df():
    empty_df = pd.DataFrame({'original': pd.Series(dtype='str'),
                             'artist': pd.Series(dtype='str'),
                             'title': pd.Series(dtype='str'),
                             'length': pd.Series(dtype='float'),  # in seconds
                             'bitrate': pd.Series(dtype='int'),
                             'sample_rate': pd.Series(dtype='int'),
                             'bass': pd.Series(dtype='str'),
                             'drums': pd.Series(dtype='str'),
                             'vocals': pd.Series(dtype='str'),
                             'guitars': pd.Series(dtype='str'),
                             'other': pd.Series(dtype='str')})
    return empty_df


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


def get_mp3_length(song_loc):
    audio = MP3(song_loc)
    return audio.info.length


def get_mp3_bitrate(song_loc):
    audio = MP3(song_loc)
    bitrate = audio.info.bitrate // 1000
    return bitrate


def get_mp3_sample_rate(song_loc):
    audio = MP3(song_loc).info
    return audio.sample_rate


if __name__ == '__main__':
    directory, csv_loc = get_arguments()  # command line args
    originals_dir = os.path.join(directory, ORIGINALS_LOC)
    stems_dir = os.path.join(directory, STEMS_LOC)

    df = create_empty_df()  # empty dataframe where will be dataset info

    i = 0

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

            # add entry to dataframe
            new_row = pd.DataFrame({'original': f,
                                    'artist': f_basename.split("-")[0],
                                    'title': f_basename.split("-")[1][:-4],  # [:-4] to remove extension
                                    'length': round(get_mp3_length(f), 2),
                                    'bitrate': get_mp3_bitrate(f),
                                    'sample_rate': get_mp3_sample_rate(f),
                                    'bass': bass,
                                    'drums': drums,
                                    'vocals': vocals,
                                    'guitars': guitars,
                                    'other': other}, index=[0])
            df = pd.concat([new_row, df.loc[:]]).reset_index(drop=True)

    # Save dataframe to csv
    df.to_csv(csv_loc, sep=',', encoding='utf-8', index=False)
