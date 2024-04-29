import math
import random
import sys
sys.path.append("..")
from scratchypy import *

"""
This is a simple example that shows/tests the layering of sprites and the
ability for a sprite to switch layers using the layer related APIs.
"""

# Entry point called from start()
def when_started(stage):
    # Make 10 waves across the screen
    for i in range(10):
        wave = Sprite("assets/waves.png", stage=stage, x=400-20*i+random.randint(-30,30), y=60*i, size=75)
        # run wave action in the background
        stage.run(moveWave(wave))
    # Make Axel for swimming
    axel = Sprite("assets/axolotl1.png", stage=stage, x=350, y=160, size=50)
    # he's way out there.
    axel.go_to_back_layer()
    axel.go_forward_layers(3)
    # start swimming in the background...
    stage.run(moveAxel(axel))
    
async def moveWave(wave):
    """
    Forever async function to move the waves up and down and wavelike.
    Note that the 'await' is super necessary here to not make an infinite
    loop that blocks the main event loop!
    """
    i = random.randint(0,360)
    while True:
        offsety = 2*math.sin(math.radians(i))
        offsetx = math.sin(math.radians(i/10))
        wave.change_y_by(offsety)
        wave.change_x_by(offsetx)
        await wait(.1)
        i+=10
        
async def moveAxel(axel):
    """
    Slowly move Axel forward in layers.
    """
    xdir = 1
    ACCEL = .6
    for y in range(200, 600, 60):
        axel.set_y_to(y-30)
        speed = -10
        lastSpeed = speed
        xdir *= -1
        while axel.y < y:
            axel.change_y_by(speed)
            axel.change_x_by(xdir)
            if lastSpeed < 0 and speed >= 0:
                axel.go_forward_layers(1)
            lastSpeed = speed
            speed += ACCEL
            await wait()
        await wait(.5)
    axel.say("Cowabunga!")

# Note how to set the window title.
start(when_started, windowTitle="`'-.,_,.-'``'-.,_,.-'``'-.,_,.-'``'-.,_, WAVES `'-.,_,.-'``'-.,_,.-'``'-.,_,.-'``'-.,_,.")

