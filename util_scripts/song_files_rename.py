# -----------------------------------------------------------
# script to rename downloaded songs into format {artist}-{song_name}
#
# 2022 Natália Holková
# xholko02@stud.fit.vutbr.cz
# -----------------------------------------------------------

import getopt
import os
import sys


def get_arguments():
    folder = os.path.abspath(os.getcwd())  # Default folder path is current working directory
    artist = "unknown"
    num_at_start = False

    argument_list = sys.argv[1:]  # Remove 1st arg from the list
    options = "f:a:n"  # Options
    long_options = ["Folder=", "Artist=", "Numbers_at_start"]  # Long options

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)  # Parsing argument
        for currentArgument, currentValue in arguments:  # checking each argument
            if currentArgument in ("-n", "--Numbers_at_start"):
                print("Filenames start with numbers")
                num_at_start = True
            elif currentArgument in ("-a", "--Artist"):
                print("Artist is % s" % currentValue)
                artist = currentValue
            elif currentArgument in ("-f", "--Folder"):
                print("Folder is % s" % currentValue)
                folder = currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))

    return folder, artist, num_at_start


def get_new_name(old_file, artist, num_at_start):
    words = old_file.split(" ")

    if num_at_start:  # remove track number
        words = words[1:]
        if words[0] == "-":  # sometimes track number is followed by '-'
            words = words[1:]

    new_file = artist + "-" + "_".join(words)
    new_file = new_file.lower().replace(".", "")
    return new_file


def rename_file(folder, old_name, new_name):
    full_old_name = os.path.join(folder, old_name)
    full_new_name = os.path.join(folder, new_name)
    os.rename(full_old_name, full_new_name)
    print(f"- renamed {old_name} to {new_name}")


if __name__ == '__main__':
    directory, artist_name, num_start = get_arguments()
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            old_filename = os.path.basename(f)  # full filename
            old_basename = os.path.splitext(old_filename)[0]  # basename
            extension = os.path.splitext(old_filename)[1]  # extension
            new_filename = get_new_name(old_basename, artist_name, num_start) + extension
            rename_file(os.path.dirname(f), old_filename, new_filename)  # rename the file
