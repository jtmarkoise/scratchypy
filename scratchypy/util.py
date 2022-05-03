'''
Created on May 1, 2022

@author: markoise
'''
import asyncio
import os

async def wait(seconds):
    await asyncio.sleep(seconds)
    
def username():
    return os.getlogin()