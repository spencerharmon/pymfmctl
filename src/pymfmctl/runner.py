import multiprocessing
import subprocess
import time
import logging
from .config import Config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

class Runner(multiprocessing.Process):
    def __init__(self, config: Config, queue: multiprocessing.Queue):
        self.shutdown_callback = multiprocessing.Event()
        self.config = config
        self.queue = queue
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
            self.command(self.queue.get())
        proc.kill()
