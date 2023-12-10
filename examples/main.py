# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import sys, random
sys.path.append("..")
from scratchypy import *
from pygame.locals import *

sp1 = None
txt = None

async def init(stage):
    global sp1, sp2, txt
    print("init")
    
    stage.add_backdrops(main="assets/background1.jpg")
    stage.forever(tick)
    stage.when_clicked(stageClick)
    stage.when_key_pressed('a', stageKey)
    stage.when_key_pressed('x', changeBg)
    stage.when_drawing(drawExtra)
    
    
    frames = image.loadPattern("assets/axolotl*.png")
    # Make the tail wag both ways
    frames.extend(reversed(frames[:-1]))
    sp1 = AnimatedSprite(frames, 5, 
                         x=90,y=90,
                         size=50, 
                         name='ax1')
    stage.add(sp1) 
    sp1.when_clicked(onClick)
    sp1.when_i_receive("hello", onHello)
    sp1.when_key_pressed('b', spriteKey)
    
    txt = scratchypy.sprite.TextSprite("Hello there to all the cool axolotls with sunglasses", x=320, y=220)
    stage.add(txt)
    
    sp2 = AnimatedSprite(frames, 1, 
                         x=30,y=550,
                         size=20, 
                         name='ax2')
    stage.add(sp2)
    #Story mode
    sp2.glide_to(30, 450, 1) #background
    await sp2.say_and_wait("swimmin along", 1)
    await sp2.glide_to_position_and_wait((700, 550), 5)
    print("init done")

def tick(stage):
    global sp1
    #print("tick")
    #if random.randint(1,10) > 6:
    #    sp1.turn(random.randint(-40,40))
    #sp1.setRotationStyle(scratchypy.LEFT_RIGHT)
    w = get_window()
    sp1.point_towards((w.mouse_x, w.mouse_y))
    #sp1.change_size_by(random.randint(-5, 5))
    sp1.move(3)
    #sp1.if_on_edge_bounce()
    
    txt.move(1)
    txt.turn(2)
    #stage.broadcast("hello", who="worldx")
    #print(pygame.key.name(pygame.K_UP))
    if w.key_pressed("up"):
        sp1.change_y_by(-30)
    if w.key_pressed("down"):
        sp1.change_y_by(30)
    if w.key_pressed("c"):
        print(sp1.y_position)
        sp2 = sp1.clone("sp2", stage)
        sp2.glide_to(0,0,5)
        
async def stageKey(stage):
    #sp1.change_x_by(30)
    print("stageKey")
    answer = await sp1.ask_and_wait("what you want?")
    print(answer)

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
    print("FPS: %f" % get_window().actual_fps)
    print(sp1.direction_to((200,200)))
    
def changeBg(stage):
    stage.next_backdrop()
    
def drawExtra(stage, surface):
    pygame.draw.rect(surface, color.BLUE, pygame.Rect(200,200,2,2), width=1)
    

def onHello(**kwargs):
    print(kwargs["who"])

if __name__ == '__main__':
    start(init)
    
    
    