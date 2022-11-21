# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
"""Main training loop."""

import logging
from dora import get_xp
from dora.utils import write_and_rename
from dora.log import LogProgress, bold
import torch
import torch.nn.functional as F
from . import augment, distrib, states, pretrained
#from .apply import apply_model
#from .ema import ModelEMA
#from .evaluate import evaluate, new_sdr
#from .svd import svd_penalty
#from .utils import pull_metric, EMA

logger = logging.getLogger(__name__)


class Solver(object):
    def __init__(self, loaders, model, optimizer, args):
        self.args = args
        self.loaders = loaders

        self.model = model
        self.optimizer = optimizer
        self.quantizer = states.get_quantizer(self.model, args.quant, self.optimizer)
        self.dmodel = distrib.wrap(model)
        self.device = next(iter(self.model.parameters())).device