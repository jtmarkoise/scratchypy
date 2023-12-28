# Copyright 2023 Mark Malek
# See LICENSE file for full license terms.
"""
This is the documentation for the ScratchyPy library.  I suggest looking at
the `sprite` and `stage` modules first! 
""" 

import pygame

pygame.init()

from .version import __version__
print("ScratchyPy " + __version__)

from . import sprite, stage, window, color, sound, image, text
from .window import *
from .stage import *
from .sprite import *
from .util import *
