# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import subprocess as sp
import json
import numpy as np
import torch
import torchaudio as ta
from .utils import temp_filenames
from pathlib import Path
import julius
import lameenc


def _read_info(path):
    stdout_data = sp.check_output([
        'ffprobe', "-loglevel", "panic",
        str(path), '-print_format', 'json', '-show_format', '-show_streams'
    ])
    return json.loads(stdout_data.decode('utf-8'))


class AudioFile:
    """
    Allows to read audio from any format supported by ffmpeg, as well as resampling or
    converting to mono on the fly. See :method:`read` for more details.
    """
    def __init__(self, path: Path):
        self.path = Path(path)
        self._info = None

    def __repr__(self):
        features = [("path", self.path)]
        features.append(("samplerate", self.samplerate()))
        features.append(("channels", self.channels()))
        features.append(("streams", len(self)))
        features_str = ", ".join(f"{name}={value}" for name, value in features)
        return f"AudioFile({features_str})"

    @property
    def info(self):
        if self._info is None:
            self._info = _read_info(self.path)
        return self._info

    @property
    def duration(self):
        return float(self.info['format']['duration'])

    @property
    def _audio_streams(self):
        return [
            index for index, stream in enumerate(self.info["streams"])
            if stream["codec_type"] == "audio"
        ]

    def __len__(self):
        return len(self._audio_streams)

    def channels(self, stream=0):
        return int(self.info['streams'][self._audio_streams[stream]]['channels'])

    def samplerate(self, stream=0):
        return int(self.info['streams'][self._audio_streams[stream]]['sample_rate'])

    def read(self,
             seek_time=None,
             duration=None,
             streams=slice(None),
             samplerate=None,
             channels=None,
             temp_folder=None):
        streams = np.array(range(len(self)))[streams]
        single = not isinstance(streams, np.ndarray)
        if single:
            streams = [streams]

        if duration is None:
            target_size = None
            query_duration = None
        else:
            target_size = int((samplerate or self.samplerate()) * duration)
            query_duration = float((target_size + 1) / (samplerate or self.samplerate()))

        with temp_filenames(len(streams)) as filenames:
            command = ['ffmpeg', '-y']  # -y = Overwrite output files without asking.
            command += ['-loglevel', 'panic']  # -loglevel = Set logging level and flags used by the library
                                               # panic =  Only show fatal errors which could lead the process to crash
            if seek_time:
                command += ['-ss', str(seek_time)]  # -start_at_zero = shift input timestamps so they start at zero
            command += ['-i', str(self.path)]  # -i = input file url
            for stream, filename in zip(streams, filenames):
                command += ['-map', f'0:{self._audio_streams[stream]}']  # -map = Create one or more streams in the output file.
                if query_duration is not None:
                    command += ['-t', str(query_duration)]  # -t = limit the duration of data read from the input file
                command += ['-threads', '1']
                command += ['-f', 'f32le']  # -f = Force input or output file format
                                            # f32le = 32-bit floating-point little-endian
                if samplerate is not None:
                    command += ['-ar', str(samplerate)]
                command += [filename]

            sp.run(command, check=True)
            wavs = []
            for filename in filenames:
                wav = np.fromfile(filename, dtype=np.float32)
                wav = torch.from_numpy(wav)
                wav = wav.view(-1, self.channels()).t()
                if channels is not None:
                    wav = convert_audio_channels(wav, channels)
                if target_size is not None:
                    wav = wav[..., :target_size]
                wavs.append(wav)
        wav = torch.stack(wavs, dim=0)
        if single:
            wav = wav[0]
        return wav


def convert_audio_channels(mp3, channels=2):
    """Convert audio to the given number of channels."""
    *shape, src_channels, length = mp3.shape
    if src_channels == channels:
        pass
    elif channels == 1:
        # Case 1:
        # The caller asked 1-channel audio, but the stream have multiple
        # channels, downmix all channels.
        mp3 = mp3.mean(dim=-2, keepdim=True)
    elif src_channels == 1:
        # Case 2:
        # The caller asked for multiple channels, but the input file have
        # one single channel, replicate the audio over all channels.
        mp3 = mp3.expand(*shape, channels, length)
    elif src_channels >= channels:
        # Case 3:
        # The caller asked for multiple channels, and the input file have
        # more channels than requested. In that case return the first channels.
        mp3 = mp3[..., :channels, :]
    else:
        # Case 4: What is a reasonable choice here?
        raise ValueError('The audio file has less channels than requested but is not mono.')
    return mp3


def i16_pcm(wav):
    """Convert audio to 16 bits integer PCM format."""
    if wav.dtype.is_floating_point:
        return (wav.clamp_(-1, 1) * (2**15 - 1)).short()
    else:
        return wav

def encode_mp3(wav, path, samplerate=44100, bitrate=320, verbose=False):
    """Save given audio as mp3. This should work on all OSes."""
    C, T = wav.shape
    wav = i16_pcm(wav)
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(bitrate)
    encoder.set_in_sample_rate(samplerate)
    encoder.set_channels(C)
    encoder.set_quality(2)  # 2-highest, 7-fastest
    if not verbose:
        encoder.silence()
    wav = wav.data.cpu()
    wav = wav.transpose(0, 1).numpy()
    mp3_data = encoder.encode(wav.tobytes())
    mp3_data += encoder.flush()
    with open(path, "wb") as f:
        f.write(mp3_data)


def prevent_clip(wav, mode='rescale'):
    """
    different strategies for avoiding raw clipping.
    """
    assert wav.dtype.is_floating_point, "too late for clipping"
    if mode == 'rescale':
        wav = wav / max(1.01 * wav.abs().max(), 1)
    elif mode == 'clamp':
        wav = wav.clamp(-0.99, 0.99)
    elif mode == 'tanh':
        wav = torch.tanh(wav)
    else:
        raise ValueError(f"Invalid mode {mode}")
    return wav


def convert_audio(mp3, from_samplerate, to_samplerate, channels):
    """Convert audio from a given samplerate to a target one and target number of channels."""
    mp3 = convert_audio_channels(mp3, channels)
    return julius.resample_frac(mp3, from_samplerate, to_samplerate)


def save_audio(wav, path, samplerate, bitrate=320, clip='rescale',
               bits_per_sample=16, as_float=False):
    """Save audio file, automatically preventing clipping if necessary
    based on the given `clip` strategy. If the path ends in `.mp3`, this
    will save as mp3 with the given `bitrate`.
    """
    wav = prevent_clip(wav, mode=clip)
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".mp3":
        encode_mp3(wav, path, samplerate, bitrate)
    else:
        raise ValueError(f"Invalid suffix for path: {suffix}")
