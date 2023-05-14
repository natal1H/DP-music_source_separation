import os
from mutagen.mp3 import MP3
import datetime

dataset_directory = "/home/natali/Desktop/remix_dataset/test"

duration = 0

# go over all song folders in dataset directory
for song_directory in os.listdir(dataset_directory):
    full_song_dir = os.path.join(dataset_directory, song_directory)
    if os.path.isdir(full_song_dir):
        print(song_directory + ": ", end="")
        mixture_loc = os.path.join(full_song_dir, "mixture.mp3")
        mixture = MP3(mixture_loc)
        duration += mixture.info.length
        print(str(datetime.timedelta(seconds=mixture.info.length)))

print("=================================")
print("Total duration of dataset [s]:", str(datetime.timedelta(seconds=duration)))
