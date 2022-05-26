# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import pygame

pygame.init()
VERSION = (0,1)
print("ScratchyPy 0.01")

from . import sprite, stage, window, color, sound, image, text
from .window import *
from .stage import *
from .sprite import *
from .util import *
