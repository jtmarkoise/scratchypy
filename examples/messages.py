# Copyright 2023 Mark Malek
# See LICENSE file for full license terms. 

import sys
sys.path.append("..")
from scratchypy import *
from scratchypy import color

class MainScreen(Stage):
    def on_init(self):
        # Convenience: specifying the stage automatically adds it.
        self._sender = Sprite("assets/axolotl1.png", 
                         x=100,y=300,
                         size=50, 
                         name='sender', stage=self)
        # Set handler for "hello" message
        self._sender.when_i_receive("hello", self.helloMessageHandler)
        self._sender.when_i_receive("broadcast", self.broadcastHandler)
        self._receiver1 = self._sender.clone("receiver1", self)
        self._receiver2 = self._sender.clone("receiver2", self)
        self._receiver3 = self._sender.clone("receiver3", self)
        
        self.when_started(self._async_start)
        
    async def _async_start(self, obj):
        t1 = self._receiver1.glide_to(500, 100, 2)
        t2 = self._receiver2.glide_to(500, 300, 2)
        t3 = self._receiver3.glide_to(500, 500, 2)
        await t1
        await t2
        await t3
        
        self._sender.when_clicked(self.onSenderClicked)
        self._sender.say("Click me to send a message to the first clone.")
        
    def onSenderClicked(self, sprite, pos):
        sprite.say()
        self._receiver1.message("hello", {'senderName':"Axel Ottle"})
        
    async def helloMessageHandler(self, sprite, argDictionary):
        await sprite.say_and_wait("Why hello %s" % argDictionary.get("senderName", "??"), 2)
        sprite.when_clicked(self.onReceiver1Clicked)
        sprite.say("Click me to broadcast a message to everyone else.")
        
    def onReceiver1Clicked(self, sprite, pos):
        # broadcasts happen from the stage only
        self.broadcast("broadcast", excludeOriginator=sprite)
        sprite.say()

    async def broadcastHandler(self, sprite, argDictionary):
        await sprite.say_and_wait("Roger that.", 3)

if __name__ == '__main__':
    start(stage=MainScreen())
    
    
    