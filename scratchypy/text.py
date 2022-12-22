# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import re
import asyncio
import pygame.surface
from pygame.locals import *
from scratchypy import color

def render_text(font, text, rect, color=color.BLACK, bgcolor=None):
    maxWidth = rect.w
    
    # word wrap.  TODO: honor existing newlines
    lines = []
    words = re.split('\\s', text)
    i = 1
    while i <= len(words):
        w,_ = font.size(' '.join(words[:i]))
        if w > maxWidth:
            # one word too many, unless it's the only word, might truncate
            if i == 0:
                lines.append(words[0])
                words = words[1:]
            else:
                lines.append(' '.join(words[:i-1]))
                words = words[i-1:]
            i=0
        else:
            i+=1
    # add remaining
    if words:
        lines.append(' '.join(words))
    
    # calculate size of single render surface
    surfaces = [font.render(line, True, color) for line in lines]
    if len(surfaces) == 1:
        if bgcolor:
            bg = surfaces[0].copy()
            bg.fill(bgcolor)
            bg.blit(surfaces[0], (0,0))
            return bg
        else:
            return surfaces[0]  #TODO: may not honor maxHeight
    # else blit them all to a single surface
    width = min(maxWidth, max([s.get_size()[0] for s in surfaces]))
    totalHeight = min(rect.h, font.get_linesize() * len(surfaces))
    #TODO: nicer cutoff of lines^^^
    bigsurf = pygame.surface.Surface((width, totalHeight), pygame.SRCALPHA, 32)
    if bgcolor:
        bigsurf.fill(bgcolor)
    
    # render the lines
    y = 0
    for surf in surfaces:
        bigsurf.blit(surf, (0,y))
        y += font.get_linesize()
    return bigsurf


class AskDialog(pygame.sprite.Sprite):
    """
    Shows a text box and handles key events, while rendering them to
    the UI as typed.  Only one line is allowed and RETURN submits the
    line.  Callers should use this like a sprite, then await on the
    done() future to get the string that was typed.
    """
    def __init__(self, rect):
        super().__init__()
        self.name = "askModalDialog"  # conform with ScratchyPy sprite
        self._doneFuture = asyncio.Future()
        self._text = ""
        self._draggable = False
        scr = rect
        self.rect = pygame.Rect(10, scr.h-40, scr.w-20, 30)
        self._paddedText = self.rect.inflate(-15,-15)
        self._font = pygame.font.SysFont("sans serif", 24)
    
    def done(self):
        return self._doneFuture
    
    def _on_key_down(self, event):
        if event.key == K_RETURN:
            self._doneFuture.set_result(self._text)
        elif event.key == K_ESCAPE:
            self._doneFuture.cancel()
        else:
            self._text += event.unicode
        # else ignore
        while self._font.size(self._text)[0] > self._paddedText.w:
            self._text = self._text[:-1]
    
    def _render(self, screen):
        pygame.draw.rect(screen, color.WHITE, self.rect)
        pygame.draw.rect(screen, color.BLACK, self.rect, width=2, border_radius=2)
        surf = self._font.render(self._text, True, color.BLACK)
        screen.blit(surf, self._paddedText)



