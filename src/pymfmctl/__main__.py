import multiprocessing
from .runner import Runner
from .watcher import Watcher
from .config import Config
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--config", type=str, help="path to the pymfmctl config file", default="pymfmctl.yaml")

args = parser.parse_args()

def main():
    try:
        config = Config(args.config)
    except:
        raise Exception(f"Error loading config: {args.config}")
    while True:
        runner_queue = multiprocessing.Queue()

        # watcher starts before runner
        w = Watcher(config, runner_queue)
        w.start()
        
        r = Runner(config, runner_queue)
        r.start()

        r.join()
        w.join()
    
if __name__ == "__main__":
    main()
