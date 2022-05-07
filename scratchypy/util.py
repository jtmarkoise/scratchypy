# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import asyncio
import os

async def wait(seconds):
    await asyncio.sleep(seconds)
    
def username():
    return os.getlogin()