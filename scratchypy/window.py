# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 
"""
Contains the top-level Window and global execution environment.
"""
import random
import asyncio
import time
import pygame #todo try
import pygame.key
from pygame.locals import *

import scratchypy.stage
from scratchypy import color, util

class _RollingAverage:
    """
    Simple class to keep a circular buffer of the last N values and
    calculate a rolling average on them.
    The buffer starts out as zeros so that will skew the results at the 
    beginning.
    """
    def __init__(self, numValues=10):
        if numValues <= 0:
            raise ValueError("must be positive")
        self._values = [0 for _ in range(numValues)]
        self._numValues = numValues
        self._index = 0
        
    def append(self, value):
        self._values[self._index] = value
        self._index = (self._index + 1) % self._numValues
        
    def average(self):
        return sum(self._values) / self._numValues
    

class Window:
    FPS=30
    FRAME_SEC = 1 / FPS
    
    def __init__(self):
        self._stage = scratchypy.stage.Stage()
        self._mousePos = (0,0)
        self._mouseDown = False
        self._windowSize = (800,600)
        self._fullScreen = False
        self._backgroundColor = color.WHITE
        self._running = False
        self._rollingFrameSec = _RollingAverage()
        self._lastDraw = time.perf_counter() # high resolution timer
        self._debug = False
        self._epoch = time.monotonic()
        
    def set_debug(self, val=True):
        self._debug = val
        
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

    @property
    def stage(self):
        return self._stage
    
    def set_stage(self, newStage):
        #TODO: more to it than this?
        # cleanup old, but some events might still reference
        self._stage = newStage
        self._stage._start()
    
    @property
    def fps(self) -> int:
        """
        The target Frames Per Second used for calculations.
        """
        return self.FPS
    
    @property
    def actual_fps(self) -> float:
        """
        @return the actual calculated FPS as a float.  This is usually slightly
        less than the configured fps() due to overhead.  But if you see it drop,
        you may be having a performance problem or taking too much time in the
        event callbacks.
        """
        return 1 / self._rollingFrameSec.average()

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
    
    @property
    def timer(self):
        """
        Like the Scratch 'timer' pseudo-variable, this will return the number
        of seconds (and fractional seconds) since the program was started.
        """
        return time.monotonic() - self._epoch
    
    def reset_timer(self):
        self._epoch = time.monotonic()

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
        # paint the screen
        pygame.display.flip()
        # stamp when the screen was last painted and add to rolling average
        now = time.perf_counter()  # high resolution timer
        elapsed = now - self._lastDraw
        self._rollingFrameSec.append(elapsed)
        self._lastDraw = now
        fudge = max(0, elapsed - self.FRAME_SEC) # overhead time
        # Reschedule a draw for later.
        # This limits the framerate, like tick(FPS), but also gives async
        # callbacks triggered by below events a chance to run within the same
        # frame.
        againHandle = asyncio.get_running_loop().call_later(self.FRAME_SEC - fudge, self._async_tick, screen)
        
        try:
            self._handleEvents()
            screen.fill(self._backgroundColor)
            self._stage._update(screen)
        except StopIteration:
            againHandle.cancel()
            asyncio.get_running_loop().stop()
            return
        except Exception as ex:
            print("Exception from events: '%s'." % str(ex))
            #TODO: stop and show dialog?
        
    def run(self):
        screen = self._make_screen(self._windowSize)
        util.set_ui_thread()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(self._debug)
        loop.slow_callback_duration = 1 / self.fps
        loop.call_soon(self._stage._start)
        loop.call_soon(self._async_tick, screen)
        loop.run_forever()
        # drain cancellations
        #print("Cancelling tasks")
        #for task in asyncio.all_tasks():
            #task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
        except:
            pass #TODO: other try/except may spew on exit
        loop.close()
        
    async def next_frame(self):
        """ 
        Yields control until the next frame is drawn.  This is done by a 
        calculated sleep so isn't 100% guaranteed. TODO
        """
        await asyncio.sleep(self.FRAME_SEC)

## Module functions
_window = Window()
def get_window():
    """
    @return the one and only window.  None if start() hasn't been called.
    """
    return _window

def get_stage():
    return get_window().stage

def set_stage(newStage):
    """
    Convenience to set the current stage on the window.
    """
    get_window().set_stage(newStage)

def start(whenStarted=None, stage=None, windowSize=None, fullScreen=False, backgroundColor=None, asyncioDebug=False):
    """
    Shows the window and starts the event loop.  Never returns.
    There are many options that are all optional.  It is best to
    always set these using the keyword parameters.
    @param whenStarted A function to call to perform initialization.
           This is usually only used if you are doing a simple
           functional program.  If you're organizing using custom
           stages, then you'd probably make your sprites in 
           stage.on_init().
    @param stage If you make a custom stage, you can supply it here
           and it will be set as the window's stage.
    @param windowSize A tuple of (width, height) for how big to make the window.
           Default (800, 600).
    @param fullScreen If true, use the full screen and windowSize is ignored.
    @param backgroundColor A scratchypy.color or pygame.color to use as the 
           window background, default WHITE.
    @param asyncioDebug Advanced logging of Python asyncio calls.
    """
    global _window
    if windowSize:
        _window.set_size(*windowSize)
    if fullScreen:
        _window.set_fullscreen()
    if backgroundColor:
        _window.set_background_color(backgroundColor)
    if stage is not None:
        _window._stage = stage # don't start it yet until loop is made
    if whenStarted:
        _window.stage.when_started(whenStarted)
    if asyncioDebug:
        _window.set_debug(True)
    _window.run()  #forever
