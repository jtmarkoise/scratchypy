# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import sys
sys.path.append("..")
from scratchypy import *
from pygame.locals import *
import pygame.font

#globals
rotatingText = None
changingTextLeft = None
changingTextRight = None
counter = 0

async def init(stage):
    global rotatingText, changingTextLeft, changingTextRight
    
    stage.forever(tick)

    wrapText = TextSprite("This is some text that is really long and wraps",
                        size=40, topleft=(0, 10), maxWidth=410)
    stage.add(wrapText)
    
    rotatingText = TextSprite("Rotating text", size=40, topleft=(0, 90))
    stage.add(rotatingText)
    
    changingTextLeft = TextSprite("Text changing left:", size=40, maxWidth=500, topleft=(0, 180))
    stage.add(changingTextLeft)
    changingTextRight = TextSprite("Text changing right:", size=40, maxWidth=500, topright=(400, 220))
    stage.add(changingTextRight)
    
    blueText = TextSprite("Blue text", size=40, color=color.BLUE, topleft=(0,260))
    stage.add(blueText)
    
    smallText = TextSprite("Small text", size=12, color=color.RED, topleft=(0,300))
    stage.add(smallText)
    
    font = pygame.font.SysFont("serif", 40, italic=True)
    fontText = TextSprite("Different font", font=font, topleft=(0, 320))
    stage.add(fontText)
    
    highlightText = TextSprite("highlight", size=40, bgcolor=color.YELLOW, topleft=(0,360))
    stage.add(highlightText)
    
    highlightText2 = TextSprite("highlight with wrap " * 6, size=30, bgcolor=color.GREEN, topleft=(0,400))
    stage.add(highlightText2)
    
    multiLine = TextSprite("multiline1 with some wrapping stuff center justified\nline2\nline3", size=30, maxWidth=320, topleft=(0,460), justification='center')
    stage.add(multiLine)

def tick(stage):
    #print("tick")
    global rotatingText, changingTextLeft, changingTextRight, counter
    rotatingText.turn(2)
    if counter % 30 == 0:
        changingTextLeft.set_text("Text changing left: %d" % (counter//30))
        changingTextRight.set_text("Text changing right: %d" % (counter//30))
    counter += 1


if __name__ == '__main__':
    start(whenStarted=init)
    
    
    