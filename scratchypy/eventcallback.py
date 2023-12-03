# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 
"""
Contains the EventCallback class for seamlessly encapsulating many different
types of callback strategies.
"""

import asyncio
import traceback
from scratchypy.util import is_ui_thread

class EventCallback:
    '''
    Encapsulates a callback and the calling of it.
    It handles these cases:
    * callback is None; do nothing
    * callback is async; create a task for it and run it on the event loop
    * callback is a regular function; call it synchronously on the next loop
    * caller has annotated with @to_thread; call it on threadpool
    Exceptions from the user callback are caught and logged.
    TODO: Also supports detection of args and kwargs as optional.??
    
    '''

    def __init__(self, obj, cb, name=''):
        '''
        @param obj The object initiating the callback (e.g. a certain stage or sprite).
               Usually this doesn't change for the lifetime of the callback setting.
        @param cb The callback.  May be a regular or async function, or None for no action.
        @param name Optional name used for debugging.  If omitted, this will try to find
               the __name__ of the callback function.
        '''
        self._obj = obj
        self._task = None
        self._name = name if name else cb.__name__ if cb else '(none)'
        self.set(cb)
        
    def clone(self, newObj):
        """
        Clone this handler to make a copy using the new object.  Used during
        Sprite cloning to attach the same callbacks to the new object.
        Any existing tasks are not cloned.
        """
        return EventCallback(newObj, self._cb, self._name)
        
    def name(self):
        """ @return the name given to this callback, mostly for debugging """
        return self._name
            
    def set(self, cb):
        """
        Set/reset the callback to the given function 'cb'.
        If an existing previous callback is in progress, it is cancelled.
        @param cb A regular or async function.  See class doc for details.
               May also be None.
        """
        self._cb = cb
        
        if self._task:
            print("Resetting callback '%s' while it was running! Canceling" % self._name)
            self._task.cancel()
            self._task = None
            
        if cb is None:
            self._doCall = self._call_noop
        elif asyncio.iscoroutinefunction(self._cb):
            self._doCall = self._call_async
        elif hasattr(self._cb, "_to_thread"):
            self._doCall = self._call_threaded
        else:
            self._doCall = self._call_sync
            
    def _call_noop(self, *args):
        "Do nothing when callback is None"
        pass
            
    def _call_sync(self, *args):
        """
        Call the callback synchronously while handling exceptions.
        Ensures we're on the UI thread as a safety measure.
        """
        if not is_ui_thread():
            raise Exception("Synchronous callback not from UI thread")
    
        # Consistently call within event loop;
        # prevents race condition if `when_started` is async
        # and the tick would happen before initialization.
        # BUT, this makes the callback delayed slightly
        asyncio.get_running_loop().call_soon(
            self._safe_call_sync, *args  ##FIXME: no kwargs
        )
        
    def _call_async(self, *args):
        """
        Call an 'async' callback as an asyncio task.  Returns immediately after the task is scheduled.
        """
        if self._task:
            print("Async callback '%s' still in progress, canceling" % self._name)
            self._task.cancel()
        self._task = asyncio.create_task(self._safe_call_async(*args), name=self._name)
        
    def _call_threaded(self, *args):
        """
        Kick the callback to a separate thread and treat that as the task.
        """
        if self._task:
            print("Thread callback '%s' still in progress, canceling" % self._name)
            self._task.cancel()
        #Python 3.9 or later would use to_thread()
        self._task = asyncio.get_running_loop().run_in_executor(None, self._safe_call_sync, *args) # no kwargs 
            
    def _safe_call_sync(self, *args):
        "Call the callback synchronously while handling exceptions"
        try:
            self._cb(self._obj, *args)
        except Exception as ex:
            print("Callback error: %s: %s" % (self._name, ex))
            traceback.print_exception(ex, ex, ex.__traceback__)
        self._task = None # no-op for sync case; used for @to_thread
            
    async def _safe_call_async(self, *args):
        """
        Wrapper for calling the async callback and doing the housekeeping of the
        tracked task when finished.
        This ensures it runs in the same slice as the callback, as opposed to
        using add_done_callback(), which posts it additionally and could run later.
        """
        try:
            await self._cb(self._obj, *args)
        except asyncio.exceptions.CancelledError:
            pass
        except Exception as ex:
            print("Callback error: %s: %s" % (self._name, ex))
            traceback.print_exception(ex, ex, ex.__traceback__)
        self._task = None  # ready for next one
        
    def __call__(self, *args):
        """
        How to actually call the callback.
        evt = EventCallback(...)
        evt()   # or more explicitly, evt.call()
        """
        self._doCall(*args)
    call = __call__
    
    
    