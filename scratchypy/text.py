'''
Created on Apr 14, 2022

@author: markoise
'''
import re
import pygame.surface
import scratchypy.color

def render_text(font, text, rect, color=scratchypy.color.BLACK):
    maxWidth = rect.w
    
    # word wrap
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
        return surfaces[0]  #TODO: may not honor maxHeight
    # else blit them all to a single surface
    width = min(maxWidth, max([s.get_size()[0] for s in surfaces]))
    totalHeight = min(rect.h, font.get_linesize() * len(surfaces))
    #TODO: nicer cutoff of lines^^^
    bigsurf = pygame.surface.Surface((width, totalHeight), pygame.SRCALPHA, 32)
    
    # render the lines
    y = 0
    for surf in surfaces:
        bigsurf.blit(surf, (0,y))
        y += font.get_linesize()
    return bigsurf