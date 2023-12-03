# Copyright 2022 Mark Malek
# See LICENSE file for full license terms.
# You are free to use this example in your own code.


# This line tells Python that we can use everything (*) in ScratchyPy directly
# in this file.
from scratchypy import *

# This is how to define a function in Python.  The name can be anything you'd
# like (subject to the Python naming rules, of course).
# This function will receive a `stage` that we can use to draw on.
def startItUp(stage):
    # This creates a new Sprite called 'sprite1'.  The costume for the sprite
    # is loaded from the given image file.  Use your favorite paint program to
    # make your image, and see the documentation for tips on how to save.
    # The sprite will be centered in the window by default.
    sprite1 = Sprite("assets/axolotl1.png")
    # Sprites are not automatically added to the stage.  Do so like this.
    stage.add(sprite1)
    # Rotate the sprite 45 degrees clockwise.
    sprite1.turn(45)
    # Make the sprite travel 50 steps (pixels) in the direction it is facing.
    # Like Scratch, the sprite by default faces to the right so this will move 
    # it diagonally down-right 50 pixels.
    sprite1.move(50)
    
# This is like the "when flag clicked" block, except there is no flag button
# in ScratchyPy to start the program - it starts automatically.  This tells
# the program to run the 'startItUp() function above when the program starts.
start(startItUp)