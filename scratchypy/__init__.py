'''
Created on Mar 25, 2022

@author: markoise
'''
import pygame

pygame.init()
VERSION = (0,1)
print("ScratchyPy 0.01")

from . import sprite, stage, window, color, sound, image, thread, text
from .window import *
from .stage import *
from .sprite import *
from .decorator import *
from .util import *
