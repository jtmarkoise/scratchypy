# Copyright 2023 Mark Malek
# See LICENSE file for full license terms. 
"""
Contains the Sprite class, the base of all sprites on a stage, as well as 
several other specialized subclasses.
"""

import pygame.sprite
import pygame.font
import math
import asyncio
import inspect
import copy
from typing import Literal, Tuple, Union
from scratchypy.window import get_window
from scratchypy import color
from scratchypy.eventcallback import EventCallback
import scratchypy.text


# Rotation styles
DONT_ROTATE = 0
LEFT_RIGHT = 1
ALL_AROUND = 2

# For making unique sprite names
_idCounter = 0

class Sprite(pygame.sprite.Sprite): 
    
    def __init__(self, costumes,
                 x=None, y=None, topleft=None, topright=None,
                 name=None, size=None, stage=None):
        """
        Like Scratch, x,y is in the center of the sprite.
        Where that is may change based on the costume.
        """
        #TODO: separate from pygame groups
        self.groups = [ stage ] if stage else []
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        global _idCounter
        _idCounter += 1
        self._name = name if name else "sprite" + str(_idCounter)
        
        self._costumes = []  #TODO ordered dictionary so we can lookup by name too
        self._costumeIndex = 0 #TODO does not exist yet
        self._image = None # set in _applyImage
        self._mask = None  #ditto
        self._rect = None # ditto
        self._visible = True
        winx, winy = get_window().size
        self._x = x if x is not None else winx/2
        self._y = y if y is not None else winy/2
        
        self._scale = 1 # 0..1..n, but API uses 0..100%..n%
        if size is not None and size >= 0: #TODO confusing name, but matches scratch
            self._scale = size/100
        self._rotation = 0  # degrees clockwise, like Scratch
        self._rotationStyle = ALL_AROUND # matches Scratch modes, may flip
        
        #TODO
        self._draggable = False
        self._sayThinkImages = None # images (right,left) when saying or thinking
        self._debug = False
    
        # Events
        self._on_click = EventCallback(self, None)
        self._messageHandlers = {}
        self._keyHandlers = {} # Dict of key->EventCallback
        self._on_tick = EventCallback(self, None)
        
        # TODO: have a mode to keep on screen
        self._loadCostumes(costumes if isinstance(costumes, list) else [ costumes ])
        #TODO: assert at least one costume
        
        #Easy way to position by topleft/topright instea
        if topleft:
            self.go_rect(topleft=topleft)
        elif topright:
            self.go_rect(topright=topright)
            
        if stage is not None:
            stage.add(self)
            
        # Important: if you add any new members, you must take a look at clone()
        
    def _loadCostumes(self, listOfImages):
        for im in listOfImages:
            if isinstance(im, str):
                image = pygame.image.load(im)
                image.convert(32, pygame.SRCALPHA)
            elif isinstance(im, pygame.Surface):
                image = im
            self._costumes.append(image)
        self.switch_costume_to(0)
        
    def _applyImage(self):
        """ Apply scales and transforms to original image, then set sprite vars """
        # These variables needed for sprite conventions
        self._image = orig = self._costumes[self._costumeIndex]
        if self._rotationStyle == LEFT_RIGHT and self._rotation >= 180:
            self._image = pygame.transform.flip(self._image, True, False)
        elif self._rotationStyle == ALL_AROUND and self._rotation:
            #self._image = pygame.transform.rotozoom(self._image, -self._rotation, self._scale) # pygame is CCW
            self._image = pygame.transform.rotate(self._image, -self._rotation) # pygame is CCW
        # else no rotation or flip
        
        if self._scale:
            r = self._image.get_rect()
            newSize = (int(r.width * self._scale), int(r.height * self._scale))
            self._image = pygame.transform.smoothscale(self._image, newSize)

        self._image.set_colorkey(orig.get_colorkey()) 
        self._mask = pygame.mask.from_surface(self._image)
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
    def _on_mouse_motion(self, event):
        if self._draggable:
            pass #TODO
    
    @property
    def name(self):
        """
        @return the name of the sprite set in the constructor
        """
        return self._name
    
    @property
    def visible(self):
        """
        @return True if visible, or False if hide() has been called.
        """
        return self._visible
    
    @property
    def rect(self):
        return self._rect
    
    #################################################
    ##                  MOTION
    #################################################
    
    def move(self, steps:float):
        """
        Move C{steps} (pixel lengths) in the direction of the current
        rotation.
        @param steps Distance to travel.  May be a fraction.
        FIXME for left-right mode
        """
        dy = steps * math.sin(self._rotation * math.pi / 180)
        dx = steps * math.cos(self._rotation * math.pi / 180)
        self._y += dy
        self._x += dx
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
    def turn(self, degrees:float):
        """
        Change the direction by the amouny of degrees given in C{degrees}.
        A positive number is clockwise 🔃.
        A negative number is counter-clockwise 🔄.
        """
        self._rotation += degrees
        self._rotation %= 360
        self._applyImage()
        
    def go_to_position(self, position:Tuple[float,float]):
        """
        Go to the (x,y) postion, given as a tuple.
        @see scratchypy.random_position()
        @see scratchypy.mouse_pointer()
        """
        self.goTo(position[0], position[1])
        
    def go_to(self, x:float, y:float):
        self._x = x
        self._y = y
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
    def go_rect(self, **kwargs):
        """
        Go to a position determined by the keywords accepted by pygame.Rect.
        """
        self._rect = self._image.get_rect(**kwargs)
        self._x = self._rect.centerx
        self._y = self._rect.centery
        
    async def glide_to_and_wait(self, x:float, y:float, seconds:float):
        nframes = get_window().fps * seconds
        while nframes > 0:
            # Recalculate each time in case another event moved us
            dx = (x - self._x) / nframes
            dy = (y - self._y) / nframes
            self.change_x_by(dx)
            self.change_y_by(dy)
            nframes -= 1
            await get_window().next_frame()
        # When done, should be at final spot
        self.go_to(x, y)
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
        
    def glide_to(self, x:float, y:float, seconds:float):
        """
        Glide to the given x, y in the background without waiting.
        @return The task object which can be waited on for completion.
        """
        return asyncio.create_task(self.glide_to_and_wait(x, y, seconds))
    
    async def glide_to_position_and_wait(self, position:Tuple[float,float], seconds:float):
        "Similar to glide_to_and_wait but with single position argument"
        await self.glide_to_and_wait(position[0], position[1], seconds)
    
    def glide_to_position(self, position:Tuple[float,float], seconds:float):
        "Similar to glide_to but with single position argument"
        return self.glide_to(position[0], position[1], seconds)
        
    def point_in_direction(self, degrees:float):
        """
        Set the *direction* to the given C{degrees}.  The sprite will
        point that direction regardless of its current direction.
        """
        self._rotation = (degrees - 90) % 360
        self._applyImage()
        
    def point_towards(self, positionXY):
        if isinstance(positionXY, Sprite):
            posX = positionXY.x
            posY = positionXY.y
        else:
            posX = positionXY[0]
            posY = positionXY[1]

        # The rotation(direction) is calculated no matter the mode.
        # Instead, _applyImage() decides whether to draw the rotation.
        dy = posY - self._y # may be negatives
        dx = posX - self._x
        if dx == 0:  # straight up or down
            self._rotation = 0 if dy >= 0 else 180
        else:
            self._rotation = math.atan(dy/dx) * 180 / math.pi
            if dx < 0:
                self._rotation += 180
        self._applyImage()
            
    def change_x_by(self, steps):
        self._x += steps
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
    def set_x_to(self, x):
        self._x = x  # TODO: snap to screen?
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
    def change_y_by(self, steps):
        self._y += steps
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
    def set_y_to(self, y):
        self._y = y
        self._rect = self._image.get_rect(center=(self._x, self._y))
        
    def if_on_edge_bounce(self):
        """
        TODO: add padding
        """
        winx,winy = get_window().size
        if self._rect.left < 0:
            self._x = self._rect.w / 2
            self.point_in_direction(-self.direction)
        if self._rect.right >= winx:
            self._x = winx - self.rect.w / 2
            self.point_in_direction(-self.direction)
        if self._rect.top < 0:
            self._y = self._rect.h / 2
            self.point_in_direction(180-self.direction)
        if self._rect.bottom >= winy:
            self._y = winy - self._rect.h / 2
            self.point_in_direction(180-self.direction)
            
    def if_on_edge_snap(self, padding=0):
        pass #TODO
            
    def set_rotation_style(self, style:Literal[DONT_ROTATE, LEFT_RIGHT, ALL_AROUND]):
        """ Use one of the enumerated values. """
        if not style in (DONT_ROTATE, LEFT_RIGHT, ALL_AROUND):
            raise ValueError("bad style type")
        self._rotationStyle = style
        if style in (DONT_ROTATE, ALL_AROUND):
            self._rotation = 0
        self._applyImage()
        
    @property
    def x_position(self) -> float:
        """
        sprite.x is an alias for this.
        @return the x coordinate of the center of this sprite.
        """
        return self._x
    x = x_position
    
    @property
    def y_position(self) -> float:
        """
        sprite.y is an alias for this.
        @return the y coordinate of the center of this sprite.
        """
        return self._y
    y = y_position
    
    @property
    def position(self) -> Tuple[float,float]:
        return (self._x, self._y)
    
    @property
    def direction(self) -> float:
        """
        The "direction" in Scratch is the angle the character is facing.
        By default, the cat faces right, 90 degrees - that is equivalent
        to not being rotated (0 degrees).
        Direction is in the range -179.99.. to +180 inclusive.
        """
        d = (self._rotation + 270) % 360 - 180  
        return d if d != -180 else 180   # prefer positive 180
            
    #################################################
    ##                  LOOKS
    #################################################

    def _make_bubble(self, speechText:str):
        #render the text
        font = pygame.font.SysFont("sans serif", 25)
        bounds = pygame.Rect(0,0,320,320)
        textSurf = scratchypy.text.render_text(font, speechText, bounds)
        
        # Draw the bubble - TODO-handle min sizes
        textRect = textSurf.get_rect().move(4,4) #adjust so can inflate
        bubbleRect = textRect.inflate(8,8)
        
        bubbleSurf = pygame.surface.Surface((bubbleRect.w, bubbleRect.h+10), pygame.SRCALPHA, 32)
        pygame.draw.rect(bubbleSurf, color.WHITE, bubbleRect, width=0, border_radius=10)
        pygame.draw.rect(bubbleSurf, color.BLACK, bubbleRect, width=1, border_radius=10)
        bubbleSurf.blit(textSurf, textRect)
        return bubbleSurf

    def say(self, speechText:str=None):
        """ 
        Will stay indefinitely or until another say/think.
        Say None or blank to clear bubble.
        """
        if not speechText:
            self._sayThinkImages = None
            return
        
        right = self._make_bubble(speechText)
        left = right.copy()
        r = right.get_rect()
        # draw tail for right orientation (left side)
        points = [ (15, r.bottom-11),
                   (10, r.bottom),
                   (22, r.bottom-11) ]
        pygame.draw.polygon(right, color.WHITE, points, width=0)
        pygame.draw.lines(right, color.BLACK, False, points, width=1)
        # draw tail for left orientation (right side)
        points = [(r.right-x, y) for x,y in points]
        pygame.draw.polygon(left, color.WHITE, points, width=0)
        pygame.draw.lines(left, color.BLACK, False, points, width=1)
        # set it
        self._sayThinkImages = (right, left)
        
    async def say_and_wait(self, speechText:str, howManySeconds:float):
        self.say(speechText)
        await asyncio.sleep(howManySeconds)
        self._sayThinkImages = None
        
    def think(self, thoughtText:str):
        """ 
        Will stay indefinitely or until another say/think.
        Say None or blank to clear bubble.
        """
        if not thoughtText:
            self._sayThinkImages = None
            return
        
        right = self._make_bubble(thoughtText)
        left = right.copy()
        r = right.get_rect()
        # right side (left bubbles) 
        pygame.draw.circle(right, color.WHITE, (16, r.bottom-9), 4, width=0)
        pygame.draw.circle(right, color.BLACK, (16, r.bottom-9), 4, width=1)
        pygame.draw.circle(right, color.WHITE, (11, r.bottom-4), 2, width=0)
        pygame.draw.circle(right, color.BLACK, (11, r.bottom-4), 2, width=1)
        # left side (right bubbles) 
        pygame.draw.circle(left, color.WHITE, (r.right-16, r.bottom-9), 4, width=0)
        pygame.draw.circle(left, color.BLACK, (r.right-16, r.bottom-9), 4, width=1)
        pygame.draw.circle(left, color.WHITE, (r.right-11, r.bottom-4), 2, width=0)
        pygame.draw.circle(left, color.BLACK, (r.right-11, r.bottom-4), 2, width=1)
        # set it
        self._sayThinkImages = (right, left)
        
    async def think_and_wait(self, thoughtText:str, howManySeconds:float):
        self.think(thoughtText)
        await asyncio.sleep(howManySeconds)
        self._sayThinkImages = None
    
    def switch_costume_to(self, index:int):
        """
        TODO: support switch by name (file name?)
        @param number The index (number) of the costume to select.
                      Remember, in Python, counting starts at 0, 1, 2, ...
        """
        if not self._costumes:
            return #BOOM
        if index < 0 or index > len(self._costumes):
            index = 0
        self._costumeIndex = index
        self._applyImage()
        
    def next_costume(self):
        self._costumeIndex = (self._costumeIndex + 1) % len(self._costumes)
        self._applyImage()
        
    # switch_backdrop_to() is on the stage object
    # next_backdrop() is on the stage object
    
    def change_size_by(self, percentChange:float):
        #TODO: don't let less than 5% or n pixels or x% bigger than screen
        self._scale = self._scale + percentChange/100
        if self._scale < 0.05:
            self._scale = 0.05
        self._applyImage()
    
    def set_size_to(self, percent:float):
        #TODO: don't let less than 5% or n pixels or x% bigger than screen
        if percent < 0:
            raise ValueError("setSizeTo(scale) must be >= 0")
        self._scale = percent/100
        self._applyImage()
    
    #TODO: color effects
        
    def show(self):
        self._visible = True
        
    def hide(self):
        self._visible = False
        
    #TODO layers
    
    @property
    def costume_number(self) -> int:
        return self._costumeIndex
    
    @property
    def costume_name(self) -> str:
        return "TODO: implement me"
    
    # backdrop on stage
    
    @property
    def size(self) -> float:
        """
        @return the size (scaling percent) as a number, where 100% is full size.
        """
        return self._scale * 100
    
    #################################################
    ##                  SOUND - should be a separate module
    #################################################
    
    #################################################
    ##                  EVENTS
    #################################################
    
    # when flag clicked = whenStarted on start()
    
    def when_key_pressed(self, key, functionToCall):
        if not inspect.isfunction(functionToCall):
            raise TypeError("callback is not a function")
        if isinstance(key, str):
            intkey = pygame.key.key_code(key) #throw if not found
        elif isinstance(key, int):
            intkey = key
        else:
            raise TypeError("unknown key")
        name = pygame.key.name(intkey) + " key handler: " + functionToCall.__name__
        self._keyHandlers[intkey] = EventCallback(self, functionToCall, name=name)
        
    def _on_key_down(self, event):
        handler = self._keyHandlers.get(event.key)
        if handler:
            handler()
    
    def when_clicked(self, handler):
        """
        When this sprite is clicked, call the given handler.
        The handler is of the form:
        ```
        def myClickHandler(sprite, clickPosition):
            pass
        ```
        Where 'sprite' is this sprite object where the click was delivered, and
        clickPosition is the tuple (x,y) position of the click relative to the
        sprite.
        """
        self._on_click.set(handler)
    when_this_sprite_clicked = when_clicked
    
    def when_i_receive(self, messageName:str, handlerFunction):
        """
        Register a callback to call when this sprite receives a message with
        the given messageName.
        The handler is of the form:
        ```
        def myMessageHandler(sprite, argDictionary):
            pass
        ```
        Where 'sprite' is this sprite object where the click was delivered, and
        the argDictionary is whatever kind of extra information goes with the
        message, as a dictionary of key, value pairs.
        """
        self._messageHandlers[messageName] = EventCallback(self, handlerFunction)
    
    def message(self, messageName:str, argDictionary={}):
        """
        Sends a message to this sprite.  (Bonus extension of Scratch).
        If there is no message event handler (registered with when_i_receive()),
        for the given messageName, then the message is ignored.
        @param messageName The message name, as a string
        @param argDictionary Optional extra parameters to give as part of the message
        FIXME: this should post to a queue, not run handler directly?
        """
        handler = self._messageHandlers.get(messageName)
        if handler:
            handler(argDictionary)
        elif self._debug:
            print("%s: no handler found for message %s" % (self._name, messageName))
    
    def broadcast(self, messageName, **kwargs):
        pass  #TODO - in stage
    
    # broadcast_and_wait????  Supposed to wait until all handlers complete
    
    #################################################
    ##                  CONTROL
    #################################################
    def forever(self, functionToCall):
        self._on_tick.set(functionToCall)
        
    def clone(self, name=None, stage=None):
        """
        Make a shallow clone of this sprite.
        Important: The cloned sprite is not automatically on the same stage as
        the original; specify the 'stage' parameter to add the sprite to the
        stage.
        Costumes are not reloaded but can be manipulated independently.  
        The new sprite is at the same location and with the all the same 
        properties as this sprite. You can change properties or call functions 
        on the new returned object.
        @param name A unique name for the new sprite, or one will be
               automatically assigned.
        @param stage If not None, will be automatically added to the stage.
        """
        newObj = copy.copy(self)
        global _idCounter
        _idCounter += 1
        newObj._name = name if name else "sprite" + str(_idCounter)
        newObj._costumes = self._costumes.copy()
        newObj.groups = self.groups.copy()
        if stage is not None:
            stage.add(newObj)
        # Clone all handlers and handler dictionaries
        newObj._on_click = self._on_click.clone(newObj)
        newObj._on_tick = self._on_tick.clone(newObj)
        newObj._messageHandlers = { msg:cb.clone(newObj) for (msg, cb) in self._messageHandlers.items()}
        newObj._keyHandlers = { msg:cb.clone(newObj) for (msg, cb) in self._keyHandlers.items()}
        
        return newObj
    
    #################################################
    ##                  SENSING
    #################################################
    
    EDGE = 99
    def touching(self, what):
        """
        @param what Can be any of
            * Sprite another sprite - will compare against masks
            * pygame.sprite.Group [ADVANCED]
            * An (x,y) position tuple
            * A pygame.color.Color (but can't be an RGB tuple)
            * Sprite.EDGE to mean the screen edge.
        """
        if isinstance(what, pygame.sprite.Sprite):
            return pygame.sprite.collide_mask(self, what) is not None
        elif isinstance(what, pygame.sprite.Group):
            return len(pygame.sprite.spritecollideany(self, what, pygame.sprite.collide_mask)) > 0
        elif isinstance(what, tuple):  #coordinates
            try:
                return 1 == self._mask.get_at(what[0]-self._rect.left, what[1]-self._rect.top)
            except: # way out of bounds.. TODO optimize no exception?
                return False
        elif isinstance(pygame.color.Color):
            return self.touching_color(what)
        else: #assume EDGE
            return self.touching_edge()
        
    def touching_edge(self):
        #TODO: the mask may not necessarily go to the bounding rectangle
        w, h = get_window().size
        return self._rect.left < 0 \
            or self._rect.top < 0 \
            or self._rect.right >= w \
            or self._rect.bottom >= h
    
    def touching_color(self, color):
        raise NotImplementedError()
        #TODO... how
    
    #TODO: color is touching color??
    
    def distance_to(self, what):
        """
        @param what Can be any of
            * Sprite another sprite - distance center to center
            * An (x,y) position tuple
        """
        def dist(pos1, pos2):
            x1, y1 = pos1
            x2, y2 = pos2
            return math.sqrt((x2-x1)**2 + (y2-y1)**2)
        
        if isinstance(what, pygame.sprite.Sprite):
            return dist(self.position, what.position)
        elif isinstance(what, tuple):  #coordinates
            return dist(self.position, what)
        else:
            raise ValueError("Unknown type given to distance_to()")
        
    def direction_to(self, what):
        """
        Bonus: gives the direction in degrees from this Sprite to the
        given thing.
        @param what Can be any of
            * Sprite another sprite - distance center to center
            * An (x,y) position tuple
        @return a direction in the range [-180,180), where 0 means the
                other object is directly above this one.
        """
        if isinstance(what, Sprite):
            posX = what.x
            posY = what.y
        else:
            posX = what[0]
            posY = what[1]

        dy = posY - self._y # may be negatives
        dx = posX - self._x
        if dx == 0:  # straight up or down
            return 0 if dy >= 0 else 180
        
        rotation = math.atan(dy/dx) * 180 / math.pi
        if dx < 0:
            rotation += 180
        return (rotation + 270) % 360 - 180
        
    async def ask_and_wait(self, whatisyourname):
        """
        @return answer as a string
        """
        self.say(whatisyourname)
        answer = await scratchypy.get_stage()._ask_prompt()
        self.say(None)
        return answer
    
    # key_pressed on window
    # mouse_down, x, y on window
    
    def set_draggable(self, canDrag):
        self._draggable = canDrag
    
    #################################################
    ##                  MISC extras
    #################################################
    def set_debug(self, onoff=True):
        self._debug = onoff
        
    def _render(self, screen):
        if self._visible:
            screen.blit(self._image, self._rect)
            if self._sayThinkImages:
                bubbleRect = self._sayThinkImages[0].get_rect() # assume same size
                # Y no higher than top of screen
                bubbleY = max(0, self._rect.top - bubbleRect.h)
                # Bubble on right side if fits, else left
                if self._rect.right + bubbleRect.w <= screen.get_size()[0]:
                    r = bubbleRect.move(self._rect.right, bubbleY)
                    screen.blit(self._sayThinkImages[0], r) #right
                else:
                    r = bubbleRect.move(self._rect.left - bubbleRect.w, bubbleY)
                    screen.blit(self._sayThinkImages[1], r) #left
            if self._debug:
                pygame.draw.rect(screen, color.BLUE, self._rect, width=1)
                pygame.draw.line(screen, color.GREEN, (self._x-5, self._y), (self._x+5, self._y))
                pygame.draw.line(screen, color.GREEN, (self._x, self._y-5), (self._x, self._y+5))
    blit = _render #XXX
        
    def update(self):
        """
        Called once per frame to do updates.
        """
        self._on_tick()
    
    
class TextSprite(Sprite):
    """
    An extension of a Scratchy Sprite to display text dynamically.
    The text is rendered to a surface and stored as the one and only
    costume.
    This is a simple-to-use sprite on top of pygame.font.
    """
    def __init__(self, text, color=color.BLACK, 
                 font=None, size=50,
                 x=0, y=0, topleft=None, topright=None,
                 justification='left',
                 name=None, maxWidth=600,
                 bgcolor=None, stage=None):
        """
        If x,y is given, the sprite is positioned from center like normal.
        If topleft is given, the left edge remains constant when text changes.
        If topright is given, the right edge remains constant.
        The 'justification' (left, right, center) applies to text that has or
        wraps to multiple lines, and is the alignment within the sprite.
        If a custom font is given, then 'size' is ignored.
        """
        self._maxWidth = maxWidth
        self._color = color
        self._size = size
        self._font = font if font else pygame.font.SysFont("sans serif", self._size)
        self._topleft = topleft
        self._topright = topright
        self._justification = justification
        self._bgcolor = bgcolor
        surface = self._render_text(text)
        Sprite.__init__(self, surface, x=x, y=y, topleft=topleft, name=name, stage=stage)
    
    def _render_text(self, text):
        """
        """
        bounds = pygame.Rect(0,0,self._maxWidth,320)
        return scratchypy.text.render_text(self._font, text, bounds, self._color, self._bgcolor, self._justification)
    
    def set_text(self, text):
        surface = self._render_text(text)
        self._costumes = [ surface ]
        self._applyImage()
        # readjust if we're justified
        if self._topleft:
            self.go_rect(topleft=self._topleft)
        if self._topright:
            self.go_rect(topright=self._topright)
        
        
class AnimatedSprite(Sprite):
    """
    A convenience Sprite that can animate its costumes, assuming
    one frame per costume.  Functions are provided for easy start
    and stop of the animation.  This sprite inherits from Sprite
    and you can still move it and do any other Sprite actions.
    """
    def __init__(self, costumes, fps:int=5, x=0, y=0, name=None, size=None, stage=None):
        """
        @param costumes: List of frame/costume images.  See Sprite doc.
        @param fps: Frames Per Second you want the animation to play at,
               since e.g. a full 30 FPS is usually too fast for simple
               animations.  Will be rounded to the nearest rate compatible
               with the overall framerate.
               
        """
        super().__init__(costumes, x=x, y=y, name=name, size=size, stage=stage)
        FPS = get_window().fps
        if fps <= 0 or fps > FPS:
            raise ValueError("fps must be 1..FPS")
        self._framesPerTick = FPS // fps
        self._frameCounter = 0
        self._playing = True
        
    def start(self):
        self._playing = True
        
    def pause(self):
        self._playing = False
        
    def stop(self, homeFrame = 0):
        self._playing = False
        self.switch_costume_to(homeFrame)
    
    def update(self):
        """
        Called once per frame to do updates.
        """
        super().update()
        if self._playing:
            self._frameCounter += 1
            if self._frameCounter % self._framesPerTick == 0:
                self.next_costume()
        
        
        