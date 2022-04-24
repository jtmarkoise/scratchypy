'''
Created on Mar 25, 2022

@author: markoise
'''
import inspect
from typing import Union
import pygame
from scratchypy.eventcallback import EventCallback

#TODO prefer composition
class Stage(pygame.sprite.Group):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pygame.sprite.Group.__init__(self)
        self._on_start = EventCallback(self)
        self._on_tick = EventCallback(self)
        self._backdrops = []
        self._name_lookup = {}
        self._onClick = EventCallback(self)
        self._allClickEvents = False
        # Dict of key->handler
        self._keyHandlers = {}
        
    def _start(self):
        self._on_start(self)
        
    def _update(self, screen):
        if self._on_tick:
            self._on_tick(self)
        pygame.sprite.Group.update(self)
        for sprite in self.sprites():
            sprite._render(screen)
            
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
            spPos = (int(event.pos[0] - sp.rect.left), int(event.pos[1] - sp.rect.top))
            #TODO: check for mask hit or is rect enough?
            if sp.rect.collidepoint(event.pos) and sp.mask.get_at(spPos) == 1:
                handled=True
                # Hit - call the sprite's handler
                if sp._onClick:
                    sp._onClick(spPos) # Todo: what params to pass?
        # send event to the stage if registered
        if self._onClick and (self._allClickEvents or not handled):
            self._onClick(event.pos)
            
    def _on_key_down(self, event):
        handler = self._keyHandlers.get(event.key)
        if handler:
            handler()
        # Pass to sprites too
        for sp in self.sprites():
            sp._on_key_down(event)
            
    def add_backdrop(self, image:Union[str,pygame.Surface]):
        if isinstance(image, str):
            im = pygame.image.load(image)
            im.convert()
        elif isinstance(image, pygame.Surface):
            im = image
        else:
            raise TypeError("I don't know what this backdrop is")
        self._backdrops.append(im)
    
    def add(self, *sprites):
        # overrides Group impl to also track names
        # TODO: handle collisions?
        for sp in sprites:
            self._name_lookup[sp.name] = sp
        pygame.sprite.Group.add(self, *sprites)
        
    #################################################
    ##                  EVENTS
    #################################################
            
    def when_started(self, functionToCall):
        self._on_start = EventCallback(self, functionToCall)
        
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
        self._keyHandlers[intkey] = functionToCall
        
    def forever(self, functionToCall):
        #self._on_tick = functionToCall
        self._on_tick = EventCallback(self, functionToCall)
    each_tick = forever
        
    def when_clicked(self, handler, allClicks=False):
        """
        When a any part of the stage is clicked, call the given handler
        If allClicks=True, this will be called even if there are sprites at this point too.
        """
        if not inspect.isfunction(handler):
            raise TypeError("callback is not a function")
        
        self._onClick = EventCallback(self, handler)
        self._allClickEvents = allClicks
        
    def broadcast(self, messageName, **kwargs):
        for sp in self.sprites():
            sp.message(messageName, **kwargs)
            
            
    #################################################
    ##                  SENSING
    #################################################
    # TODO keypress - should go to sprites too??
    
    #################################################
    ##                  VARIABLES
    #################################################
    # TODO: show variable?  or leave it to a debugger?
            
        