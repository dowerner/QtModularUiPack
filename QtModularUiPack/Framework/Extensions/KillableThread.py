from threading import Thread, _active
import ctypes


class KillableThread(Thread):
    """
    This thread can be terminated manually.
    """

    def __init__(self, *args, **kwargs):
        super(KillableThread, self).__init__(*args, **kwargs)
        self.daemon = True

    def __async_raise__(self, tid, excobj):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(excobj))
        if res == 0:
            raise ValueError('nonexistent thread id')
        elif res > 1:
            """if it returns a number greater than one, you're in trouble,
            and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError('PyThreadState_SetAsyncExc failed')

    def raise_exc(self, excobj):
        if self.isAlive():
            for tid, tobj in _active.items():
                if tobj is self:
                    self.__async_raise__(tid, excobj)
                    return

    def terminate(self):
        """must raise the SystemExit type, instead of a SystemExit() instance
        due to a bug in PyThreadState_SetAsyncExc"""
        self.raise_exc(SystemExit)
