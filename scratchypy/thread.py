'''
Created on Apr 14, 2022

@author: markoise
'''
import threading
import concurrent.futures as cf

_threadPool = cf.ThreadPoolExecutor(max_workers=40) #TODO
_uiThreadId = None

def set_ui_thread():
    global _uiThreadId
    _uiThreadId = threading.get_ident()

def is_ui_thread():
    return _uiThreadId == threading.get_ident()

def get_thread_pool():
    return _threadPool