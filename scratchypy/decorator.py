# Copyright 2022 Mark Malek
# See LICENSE file for full license terms. 

import scratchypy.thread as th

#XXX
def ui_safe(uiFunc):
    # See EventCallback for significance of this
    uiFunc._uiThreadOk = True
    return uiFunc

def to_thread(uiFunc):
    # See EventCallback for significance of this
    uiFunc._to_thread = True
    return uiFunc

def ui_only(func):
    def inner():
        if not th.is_ui_thread():
            raise Exception("%s can only be called from the UI thread" % func.__name__)
        else:
            return func
    return inner
