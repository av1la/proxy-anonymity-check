"""
    queue_manager.py

    dispoe classe para enviar rotinas para multiprocessamento.
"""

import threading
import time
import inspect
import ctypes


class Worker(threading.Thread):

    def __init__(self, fn, args):
        threading.Thread.__init__(self)

        self.fn = fn
        self.args = args
        self.started_at = 0


    def kill(self):
        if self.is_alive():
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self._ident),
                ctypes.py_object(SystemExit))


    def run(self):
        self.started_at = time.time()
        self.fn(*self.args)


class Queue:

    def __init__(self, routines: list, max_threads=100, timeout=10):
        self.routines = routines
        self.max_threads = max_threads
        self.threads = []
        self.timemout = timeout + 5


    def garbage_collector(self):
        while len(self.threads):
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)
                    continue

                if time.time() > (thread.started_at + self.timemout):
                    thread.kill()
        print('processado {count} proxies em {time}s'.format(
            count=len(self.routines), 
            time=time.time()-self.started_at))


    def collector(self):
        while True:
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)
            if len(self.threads) >= self.max_threads:
                continue
            break


    def start(self):
        self.started_at = time.time()

        for routine in self.routines:

            self.collector()

            thread = Worker(
                routine['function'], tuple(routine['args'].values()))
            self.threads.append(thread)
            thread.start()

        garbage = threading.Thread(target=self.garbage_collector, args=())
        garbage.start()
        garbage.join()
