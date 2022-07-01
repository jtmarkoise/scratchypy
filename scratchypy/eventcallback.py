# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import asyncio
import traceback
from scratchypy.util import is_ui_thread

class EventCallback:
    '''
    Encapsulates a callback and the calling of it.
    It handles these cases:
    * callback is async; create a task for it and run it
    * callback is a regular function; call it synchronously on the next loop
    * caller has annotated with @to_thread; call it on threadpool
    Exceptions from the user callback are caught and logged.
    The callback can be empty as well, in which case calling this is a no-op.
    TODO
    Also supports detection of args and kwargs as optional.??
    
    '''

    def __init__(self, sender, cb, name=''):
        '''
        '''
        self._sender = sender #FIXME: here or below?
        self._cb = cb
        self._task = None
        self._name = name if name else cb.__name__ if cb else '(none)'
        
    def name(self):
        return self._name
        
    def set(self, cb):
        self._cb = cb
        if self._task:
            self._task.cancel()
            
    def _safe_call(self, *args):
        "Call the callback synchronously while handling exceptions"
        try:
            self._cb(self._sender, *args)
        except Exception as ex:
            print("Callback error: %s: %s" % (self._name, ex))
            traceback.print_exception(ex, ex, ex.__traceback__)
    
    def _on_task_done(self, task):
        "When coroutine is done, handle exceptions and bookkeeping"
        if task.cancelled():
            return
        ex = task.exception()
        if ex:
            print("Callback error: %s: %s" % (self._name, ex))
            #task.print_stack() # might be a future, not a task
            traceback.print_exception(ex, ex, ex.__traceback__)
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
            #print("callback on pool thread") #TODO
            #Python 3.9 or later would use to_thread()
            self._task = asyncio.get_running_loop().run_in_executor(None, self._cb, *args) # no kwargs
            self._task.add_done_callback(self._on_task_done)
        elif is_ui_thread():
            # Consistently call within event loop;
            # prevents race condition if `when_started` is async
            # and the tick would happen before initialization.
            # BUT, this makes the callback delayed slightly
            asyncio.get_running_loop().call_soon(
                self._safe_call, *args  ##FIXME: no kwargs
            )
        else: # not on UI thread but not marked ok; TBD
            raise Exception("Callback from different thread")
    call = __call__
    
    
    