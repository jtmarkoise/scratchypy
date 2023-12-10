# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 
"""
Misc. utility functions.
"""
import asyncio
import os
import threading
import datetime



async def wait(seconds):
    await asyncio.sleep(seconds)
    
def username():
    return os.getlogin()

def days_since_2000():
    now = datetime.datetime.today()
    y2k = datetime.datetime(2000,1,1)
    return (now-y2k).total_seconds() / 86400

#
# THREADING
#
_uiThreadId = None
def set_ui_thread():
    global _uiThreadId
    _uiThreadId = threading.get_ident()

def is_ui_thread():
    return _uiThreadId == threading.get_ident()

#
# DECORATORS
#
def to_thread(uiFunc):
    # See EventCallback for significance of this
    uiFunc._to_thread = True
    return uiFunc

def ui_only(func):
    def inner():
        if not is_ui_thread():
            raise Exception("%s can only be called from the UI thread" % func.__name__)
        else:
            return func
    return inner


