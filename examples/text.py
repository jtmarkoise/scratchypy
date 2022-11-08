# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import sys
sys.path.append("..")
from scratchypy import *
from pygame.locals import *

#globals
rotatingText = None

async def init(stage):
    global rotatingText
    
    stage.forever(tick)
    
    COL2=200

    value1 = TextSprite("This is some text that is really long and wraps",
                        size=40, topleft=(0, 10), maxWidth=410)
    stage.add(value1)
    

    rotatingText = TextSprite("Rotating text", size=40, topleft=(0, 90))
    stage.add(rotatingText)

def tick(stage):
    #print("tick")
    global rotatingText
    rotatingText.turn(2)


if __name__ == '__main__':
    start(init)
    
    
    