# Copyright 2022 Mark Malek
# See LICENSE file for full license terms.
"""
Contains functions for loading image files.
The file types it supports are the same as what pygame.image supports.
"""

import glob
import pygame.image

def load(fileName, colorToMakeTransparent:pygame.color.Color=None):
    surface = pygame.image.load(fileName)
    if colorToMakeTransparent:
        surface.convert()
        surface.set_colorkey(colorToMakeTransparent)
    else:
        # support per-pixel alpha
        surface.convert_alpha()
    return surface

def loadAll(listOfFiles, transparentColor:pygame.color.Color=None):
    return [ load(f, transparentColor) for f in listOfFiles ]

def loadPattern(globPattern, transparentColor:pygame.color.Color=None):
    """
    Load a bunch of files that match the given C{globPattern}, which may contain
    stars and other special characters as wildcards, e.g. 'pics/rocket*.png'.
    This is useful for loading many similarly-named files for animations.
    The files will be sorted to keep the animation in order (assuming numbers often
    used as the wildcard, but this is not a fancy sort.  If you have more than 10 images,
    always use two digits e.g. a01.png, rather than a1.png, a10.png, a2.png, a3.png, ...
    """
    listOfFiles = glob.glob(globPattern)
    listOfFiles.sort()
    return [ load(f, transparentColor) for f in listOfFiles ]
    