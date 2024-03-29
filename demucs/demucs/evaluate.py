# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

"""Test time evaluation, either using the original SDR from [Vincent et al. 2006]
or the newest SDR definition from the MDX 2021 competition (this one will
be reported as `nsdr` for `new sdr`).
"""

import logging
import torch as th
import torchaudio as ta
from .mp3 import get_test_dataset
from dora.log import LogProgress
import numpy as np
from . import distrib
from .apply import apply_model
from .audio import convert_audio, save_audio, AudioFile
from .utils import DummyPoolExecutor
from concurrent import futures
import museval
from pathlib import Path
import os

logger = logging.getLogger(__name__)


def new_sdr(references, estimates):
    """
    Compute the SDR according to the MDX challenge definition.
    Adapted from AIcrowd/music-demixing-challenge-starter-kit (MIT license)
    """
    assert references.dim() == 4
    assert estimates.dim() == 4
    delta = 1e-7  # avoid numerical errors
    num = th.sum(th.square(references), dim=(2, 3))
    den = th.sum(th.square(references - estimates), dim=(2, 3)) # Tu to padne
    num += delta
    den += delta
    scores = 10 * th.log10(num / den)
    return scores


def eval_track(references, estimates, win, hop, compute_sdr=True):
    references = references.transpose(1, 2).double()
    estimates = estimates.transpose(1, 2).double()

    new_scores = new_sdr(references.cpu()[None], estimates.cpu()[None])[0]  # Tu to padne

    if not compute_sdr:
        return None, new_scores
    else:
        references = references.numpy()
        estimates = estimates.numpy()
        scores = museval.metrics.bss_eval(
            references, estimates,
            compute_permutation=False,
            window=win,
            hop=hop,
            framewise_filters=False,
            bsseval_sources_version=False)[:-1]
        return scores, new_scores

    return scores, new_scores

def evaluate(solver, compute_sdr=False, test_location="../datasets/remix_dataset/test"):
    args = solver.args

    output_dir = solver.folder / "results"
    output_dir.mkdir(exist_ok=True, parents=True)
    test_dir = Path(test_location)
    segment_len = 30  # seconds
    src_rate = args.dset.samplerate

    eval_device = 'cpu'
    pendings = []
    model = solver.model
    win = int(1. * src_rate)
    hop = int(1. * src_rate)

    for root, folders, files in os.walk(test_dir, followlinks=True):
        root = Path(root)
        if root.name.startswith('.') or folders or root == test_dir:
            continue
        name = str(root.relative_to(test_dir))
        print(name)
        mixtureMp3 = root / "mixture.mp3"
        drumsMp3 = root / "drums.mp3"
        bassMp3 = root / "bass.mp3"
        otherMp3 = root / "other.mp3"
        vocalsMp3 = root / "vocals.mp3"
        guitarsMp3 = root / "guitars.mp3"

        mix, _ = ta.load(str(mixtureMp3))
        drums, _ = ta.load(str(drumsMp3))
        bass, _ = ta.load(str(bassMp3))
        other, _ = ta.load(str(otherMp3))
        vocals, _ = ta.load(str(vocalsMp3))
        guitars, _ = ta.load(str(guitarsMp3))
        ref = mix.mean(dim=0)  # mono mixture
        mix = (mix - ref.mean()) / ref.std()
        mix = convert_audio(mix, src_rate, model.samplerate, model.audio_channels)
        estimates = apply_model(model, mix[None],
                                shifts=args.test.shifts, split=args.test.split,
                                overlap=args.test.overlap)[0]
        estimates = estimates * ref.std() + ref.mean()
        estimates = estimates.to(eval_device)

        references = th.stack(
            [track for track in [drums, bass, other, vocals, guitars]])
        if references.dim() == 2:
            references = references[:, None]
        references = references.to(eval_device)
        references = convert_audio(references, src_rate,
                                   model.samplerate, model.audio_channels)
        total_length = references.shape[2]
        num_segments = int(total_length / src_rate / segment_len) + 1

        for segment_index in range(num_segments):
            start = segment_index * segment_len * src_rate
            end = start + segment_len * src_rate
            segment_references = references[:, :, start:end]
            segment_estimates = estimates[:, :, start:end]
            segment_scores, segment_new_scores = eval_track(segment_references, segment_estimates, win, hop, compute_sdr)
            pendings.append((name + "-segment" + str(segment_index), segment_scores, segment_new_scores))

    tracks = {}
    for track_name, scores, nsdrs in pendings:
        tracks[track_name] = {}
        for idx, target in enumerate(model.sources):
            tracks[track_name][target] = {'nsdr': [float(nsdrs[idx])]}
        if scores is not None:
            (sdr, isr, sir, sar) = scores
            for idx, target in enumerate(model.sources):
                values = {
                    "SDR": sdr[idx].tolist(),
                    "SIR": sir[idx].tolist(),
                    "ISR": isr[idx].tolist(),
                    "SAR": sar[idx].tolist()
                }
                tracks[track_name][target].update(values)

    result = {}
    metric_names = next(iter(tracks.values()))[model.sources[0]]
    for metric_name in metric_names:
        avg = 0
        avg_of_medians = 0
        for source in model.sources:
            medians = [
                np.nanmedian(tracks[track][source][metric_name])
                for track in tracks.keys()]
            mean = np.mean(medians)
            median = np.median(medians)
            result[metric_name.lower() + "_" + source] = mean
            result[metric_name.lower() + "_med" + "_" + source] = median
            avg += mean / len(model.sources)
            avg_of_medians += median / len(model.sources)
        result[metric_name.lower()] = avg
        result[metric_name.lower() + "_med"] = avg_of_medians
    return result
