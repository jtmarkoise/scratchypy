import pygame.sprite
import pygame.font
import math
import asyncio
import inspect
from typing import Literal, Tuple, Union
import scratchypy
from scratchypy.window import window_size
from scratchypy import color
from scratchypy.eventcallback import EventCallback

_BLUE = pygame.Color(0,0,255)
_WHITE = pygame.Color(255,255,255)
_GREEN = pygame.Color(0,255,255)
FPS=30

# Rotation styles
DONT_ROTATE = 0
LEFT_RIGHT = 1
ALL_AROUND = 2

# For making unique sprite names
_idCounter = 0

class Sprite(pygame.sprite.Sprite): 
    
    def __init__(self, costumes, x=0, y=0, name=None, size=None, stage=None):
        """
        Like Scratch, x,y is in the center of the sprite.
        Where that is may change based on the costume.
        """
        self.groups = [ stage ] if stage else []
        pygame.sprite.Sprite.__init__(self, self.groups)
        global _idCounter
        _idCounter += 1
        self.name = name if name else "sprite" + str(_idCounter)
        self._costumes = []
        self._costumeIndex = 0
        self.masks = []
        self.visible = True
        self.x = x
        self.y = y
        self._scale = 1 # 0..1..n, but API uses 0..100%..n%
        if size is not None and size >= 0: #TODO confusing name, but matches scratch
            self._scale = size/100
        self.rotation = 0  # degrees clockwise, like Scratch
        self._rotationStyle = ALL_AROUND # matches Scratch modes, may flip
        self._draggable = False
        self._animation = None
        self._sayThinkImages = None # images (right,left) when saying or thinking
        self._debug = False
        self._loadCostumes(costumes if isinstance(costumes, list) else [ costumes ])
        # Events
        self._onClick = EventCallback(self, None)
        self._messageHandlers = {}
        self._keyHandlers = {} # Dict of key->EventCallback
        self._on_tick = EventCallback(self, None)
        
        # TODO: have a mode to keep on screen
        
    def _loadCostumes(self, listOfImages):
        for im in listOfImages:
            if isinstance(im, str):
                image = pygame.image.load(im)
                image.convert()
            elif isinstance(im, pygame.Surface):
                image = im
            self._costumes.append(image)
            mask = pygame.mask.from_surface(image)
            self.masks.append(mask)
        self.switch_costume_to(0)
        
    def _applyImage(self):
        """ Apply scales and transforms to original image, then set sprite vars """
        # These variables needed for sprite conventions
        self.image = orig = self._costumes[self._costumeIndex]
        self.mask = self.masks[self._costumeIndex]
        if self._rotationStyle == LEFT_RIGHT and self.rotation >= 180:
            self.image = pygame.transform.flip(self.image, True, False)
        elif self._rotationStyle == ALL_AROUND and self.rotation:
            #self.image = pygame.transform.rotozoom(self.image, -self.rotation, self._scale) # pygame is CCW
            self.image = pygame.transform.rotate(self.image, -self.rotation) # pygame is CCW
        # else no rotation or flip
        
        if self._scale:
            r = self.image.get_rect()
            newSize = (int(r.width * self._scale), int(r.height * self._scale))
            self.image = pygame.transform.smoothscale(self.image, newSize)

        self.image.set_colorkey(orig.get_colorkey()) 
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def _on_mouse_motion(self, event):
        if self._draggable:
            pass #TODO
        
        
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
        dy = steps * math.sin(self.rotation * math.pi / 180)
        dx = steps * math.cos(self.rotation * math.pi / 180)
        self.y += dy
        self.x += dx
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def turn(self, degrees:float):
        """
        Change the direction by the amound of degrees given in C{degrees}.
        A positive number is clockwise 🔃.
        A negative number is counter-clockwise 🔄.
        """
        self.rotation += degrees
        self.rotation %= 360
        self._applyImage()
        
    def go_to_position(self, position:Tuple[float,float]):
        """
        Go to the (x,y) postion, given as a tuple.
        @see scratchypy.random_position()
        @see scratchypy.mouse_pointer()
        """
        self.goTo(position[0], position[1])
        
    def go_to(self, x:float, y:float):
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def glide_to_position(self, position:Tuple[float,float], seconds:float):
        self.glideTo(position[0], position[1], seconds)
        
    def glide_to(self, x:float, y:float, seconds:float):
        # check seconds > 0
        dx = (x - self.x) / (FPS * seconds)
        dy = (y - self.y) / (FPS * seconds)
        class GlideAnimation:
            def __init__(self, sprite, dx, dy, nframes):
                self.sprite = sprite
                self.dx = dx
                self.dy = dy
                self.frames = nframes
            def update(self):
                if self.frames <= 0:
                    return False
                self.sprite.change_x_by(self.dx)
                self.sprite.change_y_by(self.dy)
                self.frames -= 1
                return True
        self._animation = GlideAnimation(self, dx, dy, FPS*seconds)
        if not self._animation.update():
            self._animation = None

        
    def point_in_direction(self, degrees:float):
        """
        Set the *direction* to the given C{degrees}.  The sprite will
        point that direction regardless of its current direction.
        """
        self.rotation = (degrees - 90) % 360
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
        dy = posY - self.y # may be negatives
        dx = posX - self.x
        if dx == 0:  # straight up or down
            self.rotation = 0 if dy >= 0 else 180
        else:
            self.rotation = math.atan(dy/dx) * 180 / math.pi
            if dx < 0:
                self.rotation += 180
        self._applyImage()
            
    def change_x_by(self, steps):
        self.x += steps
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def set_x_to(self, x):
        self.x = x  # TODO: snap to screen?
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def change_y_by(self, steps):
        self.y += steps
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def set_y_to(self, y):
        self.y = y
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def if_on_edge_bounce(self):
        """
        TODO: only does left-right
        FIXME: doesn't bounce until center x,y at edge
        """
        win = window_size()
        if self.x < 0:
            self.x = 0
            self.point_in_direction(-self.direction())
        if self.x >= win[0]:
            self.x = win[0]
            self.point_in_direction(-self.direction())
        if self.y < 0:
            self.y = 0
            self.point_in_direction(180-self.direction())
        if self.y >= win[1]:
            self.y = win[1]
            self.point_in_direction(180-self.direction())

        self.rect = self.image.get_rect(center=(self.x, self.y))
        self._applyImage()
            
            
    def set_rotation_style(self, style:Literal[DONT_ROTATE, LEFT_RIGHT, ALL_AROUND]):
        """ Use one of the enumerated values. """
        if not style in (DONT_ROTATE, LEFT_RIGHT, ALL_AROUND):
            raise ValueError("bad style type")
        self._rotationStyle = style
        if style in (DONT_ROTATE, ALL_AROUND):
            self.rotation = 0
        self._applyImage()
        
    # TODO: make a property?
    def x_position(self) -> float:
        return self.x
    
    def y_position(self) -> float:
        return self.y
    
    def position(self) -> Tuple[float,float]:
        return (self.x, self.y)
    
    def direction(self) -> float:
        # FIXME: Scratch direction is different than rotation
        return (self.rotation + 90) % 360
            
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

    def say(self, speechText:str):
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
        @param number The index (number) of the costume to select.
                      Remember, in Python, counting starts at 0, 1, 2, ...
        """
        #TODO support file name??
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
        self.visible = True
        
    def hide(self):
        self.visible = False
        
    #TODO layers
    
    def costume_number(self) -> int:
        return self._costumeIndex
    
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
            handler(self)
    
    def when_clicked(self, handler):
        """
        when this sprite is clicked, call the given handler
        
        """
        self._onClick.set(handler)
    when_this_sprite_clicked = when_clicked
    
    def when_i_receive(self, messageName:str, handlerFunction):
        self._messageHandlers[messageName] = handlerFunction
    
    def message(self, messageName:str, **kwargs):
        """
        Sends a message to this sprite.  (Bonus extension of Scratch).
        If there is no message event handler (registered with when_i_receive()),
        for the given messageName, then the message is ignored.
        @param messageName The message name, as a string
        @param **kwargs Optional extra parameters to give as part of the message
        FIXME: this should post to a queue, not run handler directly
        """
        handler = self._messageHandlers.get(messageName)
        if handler:
            # Support both simple names and advanced kwargs
            spec = inspect.getfullargspec(handler)
            if spec.varkw:
                handler(**kwargs)
            else:
                handler()
        elif self._debug:
            print("%s: no handler found for message %s" % (self.name, messageName))
    
    def broadcast(self, messageName, **kwargs):
        pass  #TODO - in stage
    
    # broadcast_and_wait????  Supposed to wait until all handlers complete
    
    #################################################
    ##                  CONTROL
    #################################################
    def forever(self, functionToCall):
        self._on_tick.set(functionToCall)
    
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
                return 1 == self.mask.get_at(what[0]-self.rect.left, what[1]-self.rect.top)
            except: # way out of bounds.. TODO optimize no exception?
                return False
        elif isinstance(pygame.color.Color):
            return self.touching_color(what)
        else: #assume EDGE
            return self.touching_edge()
        
    def touching_edge(self):
        #TODO: the mask may not necessarily go to the bounding rectangle
        w, h = window_size()
        return self.rect.left < 0 \
            or self.rect.top < 0 \
            or self.rect.right >= w \
            or self.rect.bottom >= h
    
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
            return dist(self.position(), what.position())
        elif isinstance(what, tuple):  #coordinates
            return dist(self.position(), what)
        else:
            raise ValueError("Unknown type given to distance_to()")
        
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
    # TODO: animation: costume loop vs. motion - may be both
    def stop_animation(self):
        self._animation = None
                
          
    def set_debug(self, onoff=True):
        self._debug = onoff
        
    def _render(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect)
            if self._sayThinkImages:
                bubbleRect = self._sayThinkImages[0].get_rect() # assume same size
                # Y no higher than top of screen
                bubbleY = max(0, self.rect.top - bubbleRect.h)
                # Bubble on right side if fits, else left
                if self.rect.right + bubbleRect.w <= screen.get_size()[0]:
                    r = bubbleRect.move(self.rect.right, bubbleY)
                    screen.blit(self._sayThinkImages[0], r) #right
                else:
                    r = bubbleRect.move(self.rect.left - bubbleRect.w, bubbleY)
                    screen.blit(self._sayThinkImages[1], r) #left
            if self._debug:
                pygame.draw.rect(screen, _BLUE, self.rect, width=1)
                pygame.draw.line(screen, _GREEN, (self.x-5, self.y), (self.x+5, self.y))
                pygame.draw.line(screen, _GREEN, (self.x, self.y-5), (self.x, self.y+5))
    blit = _render #XXX
        
    def update(self):
        """
        Called once per frame to do updates.
        """
        if self._on_tick:
            self._on_tick.call(self)
        
        if self._animation:
            if not self._animation.update():
                self._animation = None
    
    
    
class TextSprite(Sprite):
    """
    An extension of a Scratchy Sprite to display text dynamically.
    The text is rendered to a surface and stored as the one and only
    costume.
    This is a simple-to-use sprite on top of pygame.font.
    """
    def __init__(self, text, color=color.BLACK, x=0, y=0, name=None, maxWidth=320):
        self._maxWidth = maxWidth
        self._color = color
        surface = self._render_text(text)
        Sprite.__init__(self, surface, x=x, y=y, name=name)
    
    def _render_text(self, text):
        """
        """
        font = pygame.font.SysFont("sans serif", 50) #TODO names
        bounds = pygame.Rect(0,0,self._maxWidth,320)
        return scratchypy.text.render_text(font, text, bounds, self._color)
    
    def set_text(self, text):
        surface = self._render_text(text)
        self._costumes = [ surface ]
        
        
class AnimatedSprite(Sprite):
    """
    A convenience Sprite that can animate its costumes, assuming
    one frame per costume.  Functions are provided for easy start
    and stop of the animation.  This sprite inherits from Sprite
    and you can still move it and do any other Sprite actions.
    """
    def __init__(self, costumes, fps:int=5, x=0, y=0, name=None, size=None):
        """
        @param costumes: List of frame/costume images.  See Sprite doc.
        @param fps: Frames Per Second you want the animation to play at,
               since e.g. a full 30 FPS is usually too fast for simple
               animations.  Will be rounded to the nearest rate compatible
               with the overall framerate.
               
        """
        super().__init__(costumes, x=x, y=y, name=name, size=size)
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
        
        
        