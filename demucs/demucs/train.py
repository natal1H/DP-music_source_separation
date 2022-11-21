# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
"""Main training script entry point"""

from dora import hydra_main
import hydra
from hydra.core.global_hydra import GlobalHydra
import logging
import os
import sys
from pathlib import Path
from .mp3 import get_remixes_dataset, get_medleydb_dataset
from . import distrib
import torch
from torch.utils.data import ConcatDataset
from omegaconf import OmegaConf
from .demucs import Demucs
from .solver import Solver


logger = logging.getLogger(__name__)


def get_model(args):
    extra = {
        'sources': list(args.dset.sources),
        'audio_channels': args.dset.channels,
        'samplerate': args.dset.samplerate,
        'segment': args.model_segment or 5 * args.dset.segment,  # TODO: 5 instead of 4 because of 'guitars' ok?
    }
    # klass = {'demucs': Demucs, 'hdemucs': HDemucs}[args.model]
    klass = {'demucs': Demucs}[args.model]
    kw = OmegaConf.to_container(getattr(args, args.model), resolve=True)
    model = klass(**extra, **kw)
    return model


def get_solver(args, model_only=False):
    distrib.init()

    torch.manual_seed(args.seed)
    model = get_model(args)

    if args.misc.show:
        logger.info(model)
        mb = sum(p.numel() for p in model.parameters()) * 4 / 2**20
        logger.info('Size: %.1f MB', mb)
        if hasattr(model, 'valid_length'):
            field = model.valid_length(1)
            logger.info('Field: %.1f ms', field / args.dset.samplerate * 1000)
        sys.exit(0)

    # torch also initialize cuda seed if available
    if torch.cuda.is_available():
        model.cuda()

    # optimizer
    if args.optim.optim == 'adam':
        optimizer = torch.optim.Adam(
            model.parameters(), lr=args.optim.lr,
            betas=(args.optim.momentum, args.optim.beta2),
            weight_decay=args.optim.weight_decay)
    elif args.optim.optim == 'adamw':
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=args.optim.lr,
            betas=(args.optim.momentum, args.optim.beta2),
            weight_decay=args.optim.weight_decay)

    assert args.batch_size % distrib.world_size == 0
    args.batch_size //= distrib.world_size

    # if model_only:
    #     return Solver(None, model, optimizer, args)

    # TODO load datasets

    train_set, valid_set = get_remixes_dataset(args)
    if args.dset.medleydb:
        extra_train_set = get_medleydb_dataset(args)
        train_set = ConcatDataset([train_set, extra_train_set])

    return None


@hydra_main(config_path="../conf", config_name="config")
def main(args):
    global __file__
    __file__ = hydra.utils.to_absolute_path(__file__)
    for attr in ["remixdset", "metadata"]:
        val = getattr(args.dset, attr)
        if val is not None:
            setattr(args.dset, attr, hydra.utils.to_absolute_path(val))

    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"

    if args.misc.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("For logs, checkpoints and samples check %s", os.getcwd())
    logger.debug(args)
    from dora import get_xp
    logger.debug(get_xp().cfg)

    solver = get_solver(args)


if __name__ == "__main__":
    main()