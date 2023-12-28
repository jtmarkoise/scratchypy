# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 
"""
Contains the Stage class used as a canvas to draw Sprites upon.
"""

import inspect
import random
from typing import Union
import pygame
from scratchypy.eventcallback import EventCallback
import scratchypy.window 
from scratchypy.text import AskDialog

#TODO prefer composition
#FIXME: "The Group does not keep sprites in any order"; we want ordering for layers
class Stage(pygame.sprite.Group):
    '''
    A Stage is the main element that contains all the Sprites and dispatches
    events to the Sprites.  It also contains a backdrop image.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pygame.sprite.Group.__init__(self)
        self._on_start = EventCallback(self, None, name="Stage.when_started")
        self._on_tick = EventCallback(self, None, name="Stage.each_tick")
        # list of (name, surface) tuples
        self._backdrops = []
        self._backdropId = -1 #TODO: gotta be one default
        self._name_lookup = {}
        self._on_click = EventCallback(self, None, name="Stage.when_clicked")
        self._allClickEvents = False
        # Dict of key->handler
        self._keyHandlers = {}
        self._dialog = None
        self._draw_raw = EventCallback(self, None, name="Stage.when_drawing")
        # call subclass init
        self.on_init()
        
    def on_init(self):
        """
        If you inherit from Stage to group your scenes and sprites, override
        this to create and add your sprites.
        This is slightly easier than having to make your own __init__() and
        needing to call super().__init__(), although that is still valid.
        TODO: init vs start is confusing.  Make it work for both 'when_started'
        and subclassing, and for both sync and async...
        """
        pass
        
    def _start(self):
        self._on_start()
        
    def _update(self, screen):
        if self._backdropId >= 0:
            screen.blit(self._backdrops[self._backdropId][1], (0,0))
        self._on_tick()
        #pygame.sprite.Group.update(self)  XXX
        for sprite in self.sprites():
            sprite.update()
            sprite._render(screen)
        self._draw_raw(screen)
        if self._dialog:
            self._dialog._render(screen)
            
            
    def _on_mouse_down(self, event):
        #TODO: distinguish click vs. drag
        pass
            
    def _on_mouse_motion(self, event):
        for sp in self.sprites():
            if sp._draggable:
                sp._on_mouse_motion(event)
                
    def _on_mouse_up(self, event):
        "A click happens on mouse up"
        # Event will contain fields pos, button, touch
        if event.button != 1:
            return # Don't handle right clicks now
        # Find the sprite(s) that has the position
        handled = False
        for sp in self.sprites():
            spPos = (int(event.pos[0] - sp._rect.left), int(event.pos[1] - sp._rect.top))
            #TODO: check for mask hit or is rect enough?
            if sp._rect.collidepoint(event.pos) and sp._mask.get_at(spPos) == 1:
                handled=True
                # Hit - call the sprite's handler
                sp._on_click(spPos) # Todo: what params to pass?
        # send event to the stage if registered
        if self._on_click and (self._allClickEvents or not handled):
            self._on_click(event.pos)
            
    def _on_key_down(self, event):
        if self._dialog:
            self._dialog._on_key_down(event)
            return # make it modal
        
        handler = self._keyHandlers.get(event.key)
        if handler:
            handler(self)
        # Pass to sprites too
        for sp in self.sprites():
            sp._on_key_down(event)
            
    def add_backdrop(self, image:Union[str,pygame.Surface], name:str=None):
        """
        Add a background image to the stage.  If this is the first
        one added, it will be automatically switched to.
        @param image Either a filename or an already converted Surface
        @param name (optional) A name to use for this backdrop.  If omitted,
               then a name is generated from its 0-based index.
        """
        if isinstance(image, str):
            im = pygame.image.load(image)
            im.convert()
            #TODO: scale image to window
        elif isinstance(image, pygame.Surface):
            im = image
        else:
            raise TypeError("I don't know what this backdrop is")
        # Resize to screen.  TODO: may warp
        im = pygame.transform.smoothscale(im, scratchypy.window.get_window().size)
        
        name = name if name else "backdrop" + str(len(self._backdrops))
        self._backdrops.append((name, im))
        if self._backdropId < 0:
            self.switch_backdrop_to(0)
        
    def add_backdrops(self, *backdrops, **kwBackdrops):
        """
        Adds several backdrops at once.
        @param backdrops Positional arguments adding an arbitrary number of
               backdrops in order, of things compatible with add_backdrop()
        @param kwBackdrops Keyword arguments adding backdrops with the name as 
               the key, and a value compatible with add_backdrop().
        """
        for b in backdrops:
            self.add_backdrop(b)
        for k,v in kwBackdrops.items():
            self.add_backdrop(v, name=k)
    
    def add(self, *sprites):
        # overrides Group impl to also track names
        # TODO: handle collisions?
        for sp in sprites:
            self._name_lookup[sp.name] = sp
        pygame.sprite.Group.add(self, *sprites)
        
    #################################################
    ##                  LOOKS
    #################################################
    @property
    def backdrop_name(self) -> str:
        if self._backdropId < 0:
            return "(default)"
        
    
    @property
    def backdrop_number(self) -> int:
        """
        Note: starts at 0.  May be -1 if there are no backdrops at all.
        """
        return self._backdropId
    
    def switch_backdrop_to(self, nameOrIndex:Union[str,int]):
        if isinstance(nameOrIndex, str):
            for idx, bdTup in enumerate(self._backdrops):
                if bdTup[0] == nameOrIndex:
                    self._backdropId = idx
            else:
                raise KeyError("No backdrop named " + nameOrIndex)
        elif isinstance(nameOrIndex, int):
            if nameOrIndex < 0 or nameOrIndex >= len(self._backdrops):
                raise IndexError("No backdrop at (0-based) index %d" % nameOrIndex)
            self._backdropId = nameOrIndex
        else:
            raise TypeError("Unknown backdrop id")
        
    async def switch_backdrop_and_wait(self):
        # TODO: should switch, call any callbacks for when switched, and return
        # that callback's future.
        raise NotImplementedError()
        
    def next_backdrop(self):
        if self._backdrops:
            self._backdropId = (self._backdropId + 1) % len(self._backdrops)
            
    def previous_backdrop(self):
        if self._backdrops:
            if self._backdropId < 0:
                self._backdropId = 0 # so it will roll to last image below
            self._backdropId = (self._backdropId - 1) % len(self._backdrops)
            
    def random_backdrop(self):
        if self._backdrops:
            self._backdropId = random.randint(0, len(self._backdrops))
    
    #################################################
    ##                  EVENTS
    #################################################
            
    def when_started(self, functionToCall):
        self._on_start.set(functionToCall)
        
    def when_key_pressed(self, key, functionToCall):
        #TODO cancel previous
        if not inspect.isfunction(functionToCall):
            raise TypeError("callback is not a function")
        
        if isinstance(key, str):
            intkey = pygame.key.key_code(key) #throw if not found
        elif isinstance(key, int):
            intkey = key
        else:
            raise TypeError("unknown key")
        self._keyHandlers[intkey] = EventCallback(self, functionToCall)
        
    def forever(self, functionToCall):
        self._on_tick.set(functionToCall)
    each_tick = forever
        
    def when_clicked(self, handler, allClicks=False):
        """
        When a any part of the stage is clicked, call the given handler
        If allClicks=True, this will be called even if there are sprites at this point too.
        """
        if not inspect.isfunction(handler):
            raise TypeError("callback is not a function")
        
        self._on_click = EventCallback(self, handler)
        self._allClickEvents = allClicks
        
    def broadcast(self, messageName, argDictionary={}, excludeOriginator=None):
        for sp in [sp for sp in self.sprites() if sp is not excludeOriginator]:
            sp.message(messageName, argDictionary)
            
            
    #################################################
    ##                  SENSING
    #################################################
    # TODO keypress - should go to sprites too??
    
    async def _ask_prompt(self):
        """
        Draws the text box on the string and asynchronously waits until 
        the user has entered the value.
        @return answer as a string
        """
        self._dialog = AskDialog(scratchypy.window.get_window().rect)
        try:
            answer = await self._dialog.done()
        finally:
            self._dialog = None
        return answer
    
    #################################################
    ##                  VARIABLES
    #################################################
    # TODO: show variable?  or leave it to a debugger?
            
    #################################################
    ##                  BONUS
    #################################################
    def when_drawing(self, callback):
        """
        Register an event handler to be called when the screen
        and all sprites are done drawing.  This gives a chance
        to manually draw more stuff with raw pygame commands
        on the raw pygame Surface.
        The callback should look like this:
        def drawExtraStuff(stage, surface):
            pygame.draw.rect(...)  # e.g.
        """
        self._draw_raw.set(callback)