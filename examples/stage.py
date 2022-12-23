# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import sys
sys.path.append("..")
from scratchypy import *
from scratchypy import color

class TitleScreen(Stage):
    def on_init(self):
        # Convenience: specifying the stage automatically adds it.
        self._sprite1 = Sprite("assets/axolotl1.png", 
                         x=400,y=100,
                         size=50, 
                         name='ax1', stage=self)
        
        # Or the stage can be added explicitly.
        self._title = TextSprite("The Most Amazing Game Ever", x=400, y=300, maxWidth=800)
        self.add(self._title)
        
        # how to add an event handler for class methods
        self._startButton = TextSprite("Start", x=400, y=400, bgcolor=color.GREEN, stage=self)
        self._startButton.when_clicked(self.onStart)
        
    def onStart(self, sender, pos):
        set_stage(GameScreen())

class GameScreen(Stage):
    def on_init(self):
        self._sprite1 = Sprite("assets/axolotl1.png", 
                         x=300,y=300,
                         size=50, 
                         name='ax1',
                         stage=self)
        self.forever(self.tick)
        self.gravity = 1
        
    def tick(self, stage):
        # 'stage' arg ^^ is redundant
        self._sprite1.change_y_by(self.gravity)
        self.gravity *= 1.1
        if self._sprite1.touching_edge():
            set_stage(EndScreen())

class EndScreen(Stage):
    def on_init(self):
        self._title = TextSprite("End stage:\nOoops you died", x=400, y=300, maxWidth=800, justification='center', stage=self)

if __name__ == '__main__':
    start(stage=TitleScreen())
    
    
    