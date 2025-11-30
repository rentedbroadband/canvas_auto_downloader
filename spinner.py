# spinner.py
import sys
import threading
import itertools
import time

class Spinner:
    def __init__(self, message=""):
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.message = message
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True

    def _spin(self):
        while not self.stop_event.is_set():
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
