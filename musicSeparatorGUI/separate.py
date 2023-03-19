# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import argparse
import sys
from pathlib import Path
import subprocess
import json

import torch as th
import torchaudio as ta
from dora.log import fatal
from demucs.audio import AudioFile, convert_audio, save_audio
from demucs.pretrained import get_model_from_args, add_model_flags, ModelLoadingError
from demucs.apply import apply_model


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

    if wav is None:
        try:
            wav, sr = ta.load(str(track))
        except RuntimeError as err:
            errors['torchaudio'] = err.args[0]
        else:
            wav = convert_audio(wav, sr, samplerate, audio_channels)

    if wav is None:
        print(f"Could not load file {track}. "
              "Maybe it is not a supported file format? ")
        for backend, error in errors.items():
            print(f"When trying to load using {backend}, got the following error: {error}")
        sys.exit(1)
    return wav


def separate_track(track_location, save_folder):
    parser = argparse.ArgumentParser("demucs.separate",
                                     description="Separate the sources for the given tracks")
    add_model_flags(parser)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-o",
                        "--out",
                        type=Path,
                        default=Path("separated"),
                        help="Folder where to put extracted tracks. A subfolder "
                        "with the model name will be created.")
    parser.add_argument("--filename",
                        #default="{track}/{stem}.{ext}",
                        default="{stem}.{ext}",
                        help="Set the name of output file. \n"
                        'Use "{track}", "{trackext}", "{stem}", "{ext}" to use '
                        "variables of track name without extension, track extension, "
                        "stem name and default output file extension. \n"
                        'Default is "{stem}.{ext}".')
    parser.add_argument("-d",
                        "--device",
                        default="cuda" if th.cuda.is_available() else "cpu",
                        help="Device to use, default is cuda if available else cpu")
    parser.add_argument("--mp3", action="store_true", default=True,
                        help="Convert the output wavs to mp3.")
    parser.add_argument("--mp3-bitrate",
                        default=320,
                        type=int,
                        help="Bitrate of converted mp3.")
    parser.add_argument("--shifts",
                        default=1,
                        type=int,
                        help="Number of random shifts for equivariant stabilization."
                             "Increase separation time but improves quality for Demucs. 10 was used "
                             "in the original paper.")
    parser.add_argument("--overlap",
                        default=0.25,
                        type=float,
                        help="Overlap between the splits.")
    split_group = parser.add_mutually_exclusive_group()
    split_group.add_argument("--no-split",
                             action="store_false",
                             dest="split",
                             default=True,
                             help="Doesn't split audio in chunks. "
                                  "This can use large amounts of memory.")
    split_group.add_argument("--segment", type=int,
                             help="Set split size of each chunk. "
                                  "This can help save memory of graphic card. ")
    parser.add_argument("--two-stems",
                        dest="stem", metavar="STEM",
                        help="Only separate audio into {STEM} and no_{STEM}. ")
    parser.add_argument("-j", "--jobs",
                        default=0,
                        type=int,
                        help="Number of jobs. This can increase memory usage but will "
                             "be much faster when multiple cores are available.")
    parser.add_argument("--clip-mode", default="rescale", choices=["rescale", "clamp"],
                        help="Strategy for avoiding clipping: rescaling entire signal "
                             "if necessary  (rescale) or hard clipping (clamp).")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--int24", action="store_true",
                       help="Save wav output as 24 bits wav.")
    group.add_argument("--float32", action="store_true",
                       help="Save wav output as float32 (2x bigger).")
    args = parser.parse_args()
    with open('conf/separation_config.json', 'r') as f:
        user_settings_dict = json.load(f)
    track = Path(track_location)
    args.__dict__["out"] = Path(save_folder)
    args.__dict__["repo"] = Path(user_settings_dict["repo"])
    args.__dict__["name"] = user_settings_dict["name"]
    args.__dict__["device"] = user_settings_dict["device"]
    print(args)

    try:
        model = get_model_from_args(args)
    except ModelLoadingError as error:
        fatal(error.args[0])

    model.cpu()
    model.eval()

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    print(f"Separated tracks will be stored in {out.resolve()}")

    wav = load_track(track, model.audio_channels, model.samplerate)

    ref = wav.mean(0)
    wav = (wav - ref.mean()) / ref.std()
    sources = apply_model(model, wav[None], device=args.device, shifts=args.shifts,
                          split=args.split, overlap=args.overlap, progress=True,
                          num_workers=args.jobs)[0]
    sources = sources * ref.std() + ref.mean()

    ext = "mp3"

    kwargs = {
        'samplerate': model.samplerate,
        'bitrate': args.mp3_bitrate,
        'clip': args.clip_mode,
        'as_float': args.float32,
        'bits_per_sample': 24 if args.int24 else 16,
    }

    for source, name in zip(sources, model.sources):
        stem = out / args.filename.format(track=track.name.rsplit(".", 1)[0],
                                          trackext=track.name.rsplit(".", 1)[-1],
                                          stem=name, ext=ext)
        stem.parent.mkdir(parents=True, exist_ok=True)
        save_audio(source, str(stem), **kwargs)
