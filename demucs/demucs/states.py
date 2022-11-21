# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
"""
Utilities to save and load models.
"""

import functools
from diffq import DiffQuantizer, UniformQuantizer, restore_quantized_state


def get_quantizer(model, args, optimizer=None):
    """Return the quantizer given the XP quantization args."""
    quantizer = None
    if args.diffq:
        quantizer = DiffQuantizer(
            model, min_size=args.min_size, group_size=args.group_size)
        if optimizer is not None:
            quantizer.setup_optimizer(optimizer)
    elif args.qat:
        quantizer = UniformQuantizer(
                model, bits=args.qat, min_size=args.min_size)
    return quantizer


def capture_init(init):
    @functools.wraps(init)
    def __init__(self, *args, **kwargs):
        self._init_args_kwargs = (args, kwargs)
        init(self, *args, **kwargs)

    return __init__