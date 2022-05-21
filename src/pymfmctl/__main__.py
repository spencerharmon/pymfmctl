import multiprocessing
import argparse
import logging
from datetime import datetime
from .runner import Runner
from .watcher import Watcher
from .config import Config
from .log import logger, log_level, set_log_file

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--config", type=str,
                    help="path to the pymfmctl config file", default="pymfmctl.yaml")

args = parser.parse_args()


def main():
    try:
        config = Config(args.config)
    except:
        raise Exception(f"Error loading config: {args.config}")
    logging.basicConfig(
        level=log_level[config.log_level],
        format='%(asctime)s %(name)s %(levelname)s:%(message)s'
    )

    config.output_path = f'{config.output_path}/{str(datetime.now().timestamp())}'
    set_log_file(config.output_path)

    logger.info(f"Begin pymfmctl.")
    logger.info(f"Set output dir to {config.output_path}")

    restarts = 0
    while True:
        logger.info(
            f"Starting a new simulation. Number of restarts: {restarts}")
        restarts += 1
        runner_queue = multiprocessing.Queue()
        watcher_queue = multiprocessing.Queue()

        # watcher starts before runner
        w = Watcher(config, runner_queue, watcher_queue)
        w.start()

        r = Runner(config, runner_queue, watcher_queue)
        r.start()

        r.join()
        w.join()


if __name__ == "__main__":
    main()
