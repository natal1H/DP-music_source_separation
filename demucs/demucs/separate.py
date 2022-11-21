# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import sys
from pathlib import Path
import subprocess

import torch as th
import torchaudio as ta

from audio import AudioFile
from pretrained import add_model_flags


def load_track(track, audio_channels, samplerate):
    errors = {}
    wav = None

    try:
        wav = AudioFile(track).read(
            streams=0,
            samplerate=samplerate,
            channels=audio_channels)
    except FileNotFoundError:
        errors['ffmpeg'] = 'FFmpeg is not installed.'
    except subprocess.CalledProcessError:
        errors['ffmpeg'] = 'FFmpeg could not read the file.'

    # if wav is None:
    #     try:
    #         wav, sr = ta.load(str(track))
    #     except RuntimeError as err:
    #         errors['torchaudio'] = err.args[0]
    #     else:
    #         wav = convert_audio(wav, sr, samplerate, audio_channels)
    #
    # if wav is None:
    #     print(f"Could not load file {track}. "
    #           "Maybe it is not a supported file format? ")
    #     for backend, error in errors.items():
    #         print(f"When trying to load using {backend}, got the following error: {error}")
    #     sys.exit(1)
    # return wav


def main():
    print("MAIN")

    parser = argparse.ArgumentParser("demucs.separate",
                                     description="Separate the sources for the given tracks")
    parser.add_argument("tracks", nargs='+', type=Path, default=[], help='Path to tracks')
    add_model_flags(parser)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-o",
                        "--out",
                        type=Path,
                        default=Path("separated"),
                        help="Folder where to put extracted tracks. A subfolder "
                        "with the model name will be created.")
    parser.add_argument("--filename",
                        default="{track}/{stem}.{ext}",
                        help="Set the name of output file. \n"
                        'Use "{track}", "{trackext}", "{stem}", "{ext}" to use '
                        "variables of track name without extension, track extension, "
                        "stem name and default output file extension. \n"
                        'Default is "{track}/{stem}.{ext}".')
    parser.add_argument("-d",
                        "--device",
                        default="cuda" if th.cuda.is_available() else "cpu",
                        help="Device to use, default is cuda if available else cpu")
    parser.add_argument("--mp3", action="store_true",
                        help="Convert the output wavs to mp3.")
    parser.add_argument("--mp3-bitrate",
                        default=320,
                        type=int,
                        help="Bitrate of converted mp3.")

    args = parser.parse_args()

    for track in args.tracks:
        if not track.exists():
            print(
                f"File {track} does not exist. If the path contains spaces, "
                "please try again after surrounding the entire path with quotes \"\".",
                file=sys.stderr)
            continue
        print(f"Separating track {track}")
        #wav = load_track(track, model.audio_channels, model.samplerate)


if __name__ == "__main__":
    main()
