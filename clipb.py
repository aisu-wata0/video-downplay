
import time
import threading
import pyperclip


def ctype_async_raise(thread_obj, exception):
    import ctypes
    found = False
    target_tid = 0
    for tid, tobj in threading._active.items():
        if tobj is thread_obj:
            found = True
            target_tid = tid
            break

    if not found:
        raise ValueError("Invalid thread object")

    ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        target_tid, ctypes.py_object(exception))
    # ref: http://docs.python.org/c-api/init.html#PyThreadState_SetAsyncExc
    if ret == 0:
        raise ValueError("Invalid thread ID")
    elif ret > 1:
        # Huh? Why would we notify more than one threads?
        # Because we punch a hole into C level interpreter.
        # So it is better to clean up the mess.
        ctypes.pythonapi.PyThreadState_SetAsyncExc(target_tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")
    print("Successfully set asynchronized exception for", target_tid)

# example predicate


def is_url(clipboard_content):
    return True

# example callback


def print_to_stdout(clipboard_content):
    print("Found url: %s" % str(clipboard_content), flush=True)


class ClipboardWatcher(threading.Thread):
    def __init__(self, predicate, callback, cooldown=5.):
        """
        self
        """
        super(ClipboardWatcher, self).__init__()
        self._predicate = predicate
        self._callback = callback
        self._cooldown = cooldown
        self._stopping = False
        self._paused = False
        self._threads = []

    def run(self):
        # Initialize with current clipboard content
        recent_value = pyperclip.paste()
        while not self._stopping:
            # If content changed
            tmp_value = pyperclip.paste()
            if tmp_value != recent_value:
                # Update recent_value with current content
                recent_value = tmp_value
                if not self._paused:
                    if self._predicate(recent_value):
                        self._threads.append(self._callback(recent_value))
            time.sleep(self._cooldown)

    def pause(self):
        print('pausing...', flush=True)
        self._paused = True

    def unpause(self):
        print('continuing...', flush=True)
        self._paused = False

    def stop(self):
        print('stopping...', flush=True)
        self._stopping = True
        for thread in self._threads:
            try:
                ctype_async_raise(thread, SystemExit)
            except:
                continue
