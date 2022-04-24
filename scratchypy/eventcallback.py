'''
Created on Apr 3, 2022

@author: markoise
'''

import asyncio
import traceback
from scratchypy.thread import is_ui_thread, get_thread_pool

class EventCallback:
    '''
    Encapsulates a callback and the calling of it.
    Callback can be asyncio, or run in a threadpool.
    Also supports detection of args and kwargs as optional.??
    Can be empty as well, in which case no-op.
    Prevents calling twice TODO
    Catch exceptions TODO
    '''

    def __init__(self, sender, cb=None, name=''):
        '''
        '''
        self._sender = sender #FIXME: here or below?
        self._cb = cb
        self._task = None
        self._name = name if name else cb.__name__ if cb else '(none)'
        
    def set(self, cb):
        self._cb = cb
        if self._task:
            self.task.cancel()
    
    def _on_task_done(self, task):
        ex = task.exception()
        if ex:
            print("Callback error: %s: %s" % (self._name, ex))
            task.print_stack()
        self._task = None  # ready for next one
        
    def __call__(self, sender, *args, **kwargs):
        # No callback is ok: no-op
        if not self._cb:
            return 
        #print(self._cb)
        # if cb is async
        if asyncio.iscoroutinefunction(self._cb):
            if self._task:
                print("coroutine still in progress, canceling")
                self._task.cancel()
            self._task = asyncio.create_task(self._cb(sender, *args, **kwargs), name=self._name)
            self._task.add_done_callback(self._on_task_done)
        elif hasattr(self._cb, "_to_thread"):
            if self._task:
                print("thread still in progress, canceling")
                self._task.cancel()
            print("callback on pool thread") #TODO
            #Python 3.9 or later would use to_thread()
            self._task = asyncio.get_running_loop().run_in_executor(None, self._cb, *args) # no kwargs
            self._task.add_done_callback(self._on_task_done)
        elif is_ui_thread():
            try:
                self._cb(self._sender, *args, **kwargs)
            except Exception as ex:
                print("Callback error: %s: %s" % (self._name, ex))
                traceback.print_exc()
        else: # not on UI thread but not marked ok; TBD
            raise Exception("Callback from different thread")
    call = __call__