'''
Created on Mar 25, 2022

@author: markoise
'''
import random
import asyncio
import pygame #todo try
import pygame.key
from pygame.locals import *

import scratchypy.stage
from scratchypy import color, thread


FPS=30
_BLACK = pygame.Color(0,0,0)

pygame.init()
print("ScratchyPy 0.1")
#FIXME: will be a different variable when import * ???
stage = scratchypy.stage.Stage()

_mousePos = (0,0)
_mouseDown = False
_windowSize = (640,480)

def get_stage():
    return stage

def mouse_x():
    return _mousePos[0]

def mouse_y():
    return _mousePos[1]

def mouse_pointer():
    return _mousePos

def mouse_down():
    return _mouseDown

def key_pressed(key=None):
    """
    Return True if the given key is currently pressed.  If no key given, then
    returns True if any key is pressed.
    @param key: Can be the text name of the key.  Some examples are 'a', '3',
           'space', 'up', 'down', 'left', 'right', etc.  The complete list of 
           names is determined by the pygame.key module.
           Key can also be a pygame.K_* integer constant.
    """
    boollist = pygame.key.get_pressed()
    if key is None or key == 'any':
        return any(boollist)
    elif isinstance(key, str):
        intkey = pygame.key.key_code(key) #throw if not found
        return boollist[intkey]
    elif isinstance(key, int) and key >= 0 and key < len(boollist):
        # pygame K_* constant
        return boollist[key]
    else:
        raise TypeError("key_pressed key not recognized: '%s'" % str(key))

def random_position():
    """
    Pick a random position within the window and return it as an (x,y) pair.
    @return a tuple of an (x,y) coordinate
    """
    x = random.randint(0, _windowSize[0])
    y = random.randint(0, _windowSize[1])
    return (x,y)

def window_size():
    return _windowSize

def window_rect():
    return pygame.Rect(0,0, *_windowSize)

async def wait(seconds):
    await asyncio.sleep(seconds)

def _make_screen(windowSize):
    global _windowSize, _uiThreadId
    _windowSize = windowSize
    SCREENRECT = pygame.Rect(0, 0, *windowSize)
    winstyle = 0 # not fullscreen
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
    return screen

def _handleEvents():
    global _mousePos, _mouseDown
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise StopIteration() #TODO
        elif event.type == pygame.MOUSEBUTTONDOWN:
            _mouseDown = True
            stage._on_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            _mouseDown = False
            stage._on_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            _mousePos = event.pos
            stage._on_mouse_motion(event)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise StopIteration() #TODO
            else:
                stage._on_key_down(event)
    
def start(windowSize=(640,480), backgroundColor=color.WHITE):
    screen = _make_screen(windowSize)
    clock = pygame.time.Clock()
    thread.set_ui_thread()
    stage._start()
    
    # The one and only forever loop
    while True:
        """
        get events
        erase the screen
        Calls stage.update
        Calls user tick()
        Redraws the screen
        Reposts the update
        """
        try:
            #print("tick " + str(clock.get_fps()))
            _handleEvents()
                
            screen.fill(backgroundColor)
            stage._update(screen)
            # paint the screen
            pygame.display.flip()
        except StopIteration:
            break
        except Exception as ex:
            print("uiOneFrame caught exception: '%s'.  The show must go on." % str(ex))
        clock.tick(FPS)
        #print("tick time: %dms, frame=%fms" % (clock.get_rawtime(), 1000/FPS))
        
    pygame.quit()

_clock = pygame.time.Clock()

def async_tick(screen, backgroundColor):
    
    try:
        #print("tick " + str(clock.get_fps()))
        _handleEvents()
            
        screen.fill(backgroundColor)
        stage._update(screen)
        # paint the screen
        pygame.display.flip()
    except StopIteration:
        asyncio.get_running_loop().stop()
        return
    except Exception as ex:
        print("uiOneFrame caught exception: '%s'.  The show must go on." % str(ex))
    _clock.tick(FPS)
    
    # reschedule ourselves
    #asyncio.create_task(async_tick(screen, backgroundColor))
    asyncio.get_running_loop().call_soon(async_tick, screen, backgroundColor)
    
def start_async(windowSize=(640,480), backgroundColor=color.WHITE):
    screen = _make_screen(windowSize)
    thread.set_ui_thread()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    stage._start()
    #asyncio.create_task(async_tick(screen, backgroundColor))
    loop.call_soon(async_tick, screen, backgroundColor)
    loop.run_forever()
    # drain cancellations
    #print("Cancelling tasks")
    for task in asyncio.all_tasks():
        task.cancel()
    try:
        loop.run_until_complete(asyncio.gather(*asyncio.all_tasks()))
    except:
        pass #TODO: other try/except may spew on exit
    loop.close()
    
