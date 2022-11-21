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
from pathlib import Path
from .mp3 import get_remix_mp3_datasets

logger = logging.getLogger(__name__)


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

    train_set, valid_set = get_remix_mp3_datasets(args) # test


if __name__ == "__main__":
    main()