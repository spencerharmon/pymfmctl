import multiprocessing
import subprocess
import time
import logging
from .config import Config
from .log import logger
import queue

class Runner(multiprocessing.Process):
    def __init__(self, config: Config, queue: multiprocessing.Queue, watcher_queue: multiprocessing.Queue):
        self.shutdown_callback = multiprocessing.Event()
        self.config = config
        self.queue = queue
        self.watcher_queue = watcher_queue
        super().__init__()

    def command(self, command: str):
        """
        all commands executed by the queue are done here.
        """
        logger.info(f"received command: {command}")
        func = {
            "shutdown": self.shutdown_callback.set
            }
        func[command]()
        
    def run(self):
        proc = subprocess.Popen(self.config.command, shell=True)
        while not self.shutdown_callback.is_set():
            code = proc.poll()
            if code is not None:
                logger.info(f"Process exited with return code {code}")
                self.watcher_queue.put("shutdown")
                break
            try:
                self.command(self.queue.get_nowait())
            except queue.Empty:
                pass

            time.sleep(1)
        proc.kill()
