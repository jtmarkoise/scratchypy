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

class Window:
    FPS=30
    
    def __init__(self):
        self._stage = scratchypy.stage.Stage()
        self._mousePos = (0,0)
        self._mouseDown = False
        self._windowSize = (800,600)
        self._fullScreen = False
        self._backgroundColor = color.WHITE
        self._clock = pygame.time.Clock()
        self._running = False
        
    def set_size(self, width, height):
        """
        """
        if self._running:
            raise RuntimeError("Can only be set before running")
        self._windowSize=(width, height)
        
    def set_fullscreen(self):
        self._fullScreen = True
        
    def set_background_color(self, color:pygame.color.Color):
        self._backgroundColor = color

    def get_stage(self):
        return self._stage
    
    def set_stage(self, newStage):
        #TODO: more to it than this?
        # cleanup old, but some events might still reference
        self._stage = newStage
    
    
    @property
    def fps(self):
        return self.FPS

    @property
    def mouse_x(self):
        return self._mousePos[0]

    @property
    def mouse_y(self):
        return self._mousePos[1]

    @property
    def mouse_pointer(self):
        "@return the position of the mouse pointer as an (x,y) tuple."
        return self._mousePos

    #not a property?
    def mouse_down(self):
        return self._mouseDown

    def key_pressed(self, key=None):
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

    @property
    def random_position(self):
        """
        Pick a random position within the window and return it as an (x,y) pair.
        @return a tuple of an (x,y) coordinate
        """
        x = random.randint(0, self._windowSize[0])
        y = random.randint(0, self._windowSize[1])
        return (x,y)

    @property
    def size(self):
        "@return the (w,h) size of the window as a tuple"
        return self._windowSize

    @property
    def rect(self):
        return pygame.Rect(0,0, *self._windowSize)

    def _make_screen(self, windowSize):
        winstyle = pygame.FULLSCREEN if self._fullScreen else 0
        bestdepth = pygame.display.mode_ok(self._windowSize, winstyle, 32)
        screen = pygame.display.set_mode(self._windowSize, winstyle, bestdepth)
        return screen

    def _handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise StopIteration() #TODO
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouseDown = True
                self._stage._on_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouseDown = False
                self._stage._on_mouse_up(event)
            elif event.type == pygame.MOUSEMOTION:
                self._mousePos = event.pos
                self._stage._on_mouse_motion(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise StopIteration() #TODO
                else:
                    self._stage._on_key_down(event)

    def _async_tick(self, screen):
        
        try:
            #print("tick " + str(clock.get_fps()))
            self._handleEvents()
                
            screen.fill(self._backgroundColor)
            self._stage._update(screen)
            # paint the screen
            pygame.display.flip()
        except StopIteration:
            asyncio.get_running_loop().stop()
            return
        except Exception as ex:
            print("uiOneFrame caught exception: '%s'.  The show must go on." % str(ex))
        self._clock.tick(self.FPS)
        
        # reschedule ourselves
        asyncio.get_running_loop().call_soon(self._async_tick, screen)
        
    def run(self):
        screen = self._make_screen(self._windowSize)
        thread.set_ui_thread()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self._stage._start()
        loop.call_soon(self._async_tick, screen)
        loop.run_forever()
        # drain cancellations
        #print("Cancelling tasks")
        for task in asyncio.Task.all_tasks():
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        except:
            pass #TODO: other try/except may spew on exit
        loop.close()

## Module functions
_window = Window()
def get_window():
    """
    @return the one and only window.  None if start() hasn't been called.
    """
    return _window

def get_stage():
    return get_window().get_stage()

def start(windowSize=None, fullScreen=False, backgroundColor=None):
    global _window
    if windowSize:
        _window.set_size(*windowSize)
    if fullScreen:
        _window.set_fullscreen()
    if backgroundColor:
        _window.set_background_color(backgroundColor)
    _window.run()  #forwever
