'''
Created on Mar 26, 2022

@author: markoise
'''
import random
from scratchypy import *
from pygame.locals import *

sp1 = None
txt = None

@ui_safe
def init(stage):
    global sp1, txt
    frames = image.loadPattern("assets/axolotl*.png")
    # Make the tail wag both ways
    frames.extend(reversed(frames[:-1]))
    sp1 = AnimatedSprite(frames, 5, 
                         x=90,y=90,
                         size=50, 
                         name='ax1')
    stage.add(sp1) # TODO: name here so tick can fetch?
    sp1.when_clicked(onClick)
    sp1.when_i_receive("hello", onHello)
    sp1.when_key_pressed('b', spriteKey)
    txt = scratchypy.sprite.TextSprite("Hello there to all the cool axolotls with sunglasses", x=320, y=220)
    stage.add(txt)
    
@ui_safe
def tick(stage):
    #if random.randint(1,10) > 6:
    #    sp1.turn(random.randint(-40,40))
    #sp1.setRotationStyle(scratchypy.LEFT_RIGHT)
    sp1.point_towards((mouse_x(), mouse_y()))
    #sp1.change_size_by(random.randint(-5, 5))
    sp1.move(3)
    #sp1.if_on_edge_bounce()
    
    txt.move(1)
    txt.turn(2)
    #stage.broadcast("hello", who="worldx")
    #print(pygame.key.name(pygame.K_UP))
    if key_pressed("up"):
        sp1.change_y_by(-30)
    if key_pressed("down"):
        sp1.change_y_by(30)
        
def stageKey():
    sp1.change_x_by(30)

async def spriteKey(src):
    #sp1.change_x_by(-30)
    print("sleep")
    #await asyncio.sleep(3)
    await sp1.think_and_wait("ouch that hurt a lot", 2)
    print("wake")
    #raise Exception()

@to_thread
def onClick(relpos):
    print("HIT ", relpos)
    
def stageClick(pos):
    print("Miss")

def onHello(**kwargs):
    print(kwargs["who"])

if __name__ == '__main__':
    stage.when_started(init)
    stage.forever(tick)
    stage.when_clicked(stageClick)
    stage.when_key_pressed('a', stageKey)
    #start()
    start_async()
    
    
    