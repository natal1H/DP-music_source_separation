"""Loading mp3 based datasets, including MedleyDB."""

# https://stackoverflow.com/questions/62543843/cannot-import-torch-audio-no-audio-backend-is-available
import os.path
from pathlib import Path
from collections import OrderedDict
import math
import torchaudio as ta


MIXTURE = "mixture"
EXT = ".mp3"

def _track_metadata(track, sources, normalize=True, ext=EXT):
    track_length = None
    track_samplerate = None
    mean = 0
    std = 1
    for source in sources + [MIXTURE]:
        file = track / f"{source}{ext}"
        try:
            info = ta.info(str(file))
        except RuntimeError:
            print(file)
            raise
        length = info.num_frames
        if track_length is None:
            track_length = length
            track_samplerate = info.sample_rate
        elif track_length != length:
            raise ValueError(
                f"Invalid length for file {file}: "
                f"expecting {track_length} but got {length}.")
        elif info.sample_rate != track_samplerate:
            raise ValueError(
                f"Invalid sample rate for file {file}: "
                f"expecting {track_samplerate} but got {info.sample_rate}.")
        if source == MIXTURE and normalize:
            try:
                wav, _ = ta.load(str(file))
            except RuntimeError:
                print(file)
                raise
            wav = wav.mean(0)
            mean = wav.mean().item()
            std = wav.std().item()

    return {"length": length, "mean": mean, "std": std, "samplerate": track_samplerate}


class Mp3set:
    def __init__(
            self,
            root, metadata, sources,
            segment=None, shift=None, normalize=True,
            samplerate=44100, channels=2, ext=EXT):
        """
        Mp3set. Can be used to train
        with arbitrary sources. Each track should be one folder inside of `path`.
        The folder should contain files named `{source}.{ext}`.
        Args:
            root (Path or str): root folder for the dataset.
            metadata (dict): output from `build_metadata`.
            sources (list[str]): list of source names.
            segment (None or float): segment length in seconds. If `None`, returns entire tracks.
            shift (None or float): stride in seconds bewteen samples.
            normalize (bool): normalizes input audio, **based on the metadata content**,
                i.e. the entire track is normalized, not individual extracts.
            samplerate (int): target sample rate. if the file sample rate
                is different, it will be resampled on the fly.
            channels (int): target nb of channels. if different, will be
                changed onthe fly.
            ext (str): extension for audio files (default is .wav).
        samplerate and channels are converted on the fly.
        """
        self.root = Path(root)
        self.metadata = OrderedDict(metadata)
        self.segment = segment
        self.shift = shift or segment
        self.normalize = normalize
        self.sources = sources
        self.channels = channels
        self.samplerate = samplerate
        self.ext = ext
        self.num_examples = []
        for name, meta in self.metadata.items():
            track_duration = meta['length'] / meta['samplerate']
            if segment is None or track_duration < segment:
                examples = 1
            else:
                examples = int(math.ceil((track_duration - self.segment) / self.shift) + 1)
            self.num_examples.append(examples)


if __name__ == "__main__":
    print("mp3.py")
    print(ta.__version__)
    print(ta.backend.get_audio_backend())

    test_track_path = "/home/nati/PycharmProjects/DP-music_source_separation/3_doors_down-when_youre_young"
    # test_track_path = Path(test_track_path)
    # meta = _track_metadata(test_track_path, ["bass", "vocals", "drums", "guitars", "other"], True, EXT)
    # print(meta)

    print(os.path.isfile(test_track_path + "/mixture.mp3"))
    print(ta.info(test_track_path + "/mixture.mp3", format="mp3"))
    mp3, _ = ta.load(test_track_path + "/mixture.mp3", format="mp3")
    print(mp3.shape)

    # test_wav_path = "C:\\Users\\Natali\\PycharmProjects\\DP-music_source_separation\\test.wav"
    # print(os.path.isfile(test_wav_path))
    # wav, _ = ta.load(test_wav_path)
    # print(wav.shape)
