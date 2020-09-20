import multiprocessing
import re
import os
import logging
import time
import shutil
import json
from .config import Config
from mfm_griddata_parser.grid_data import GridData
from mfm_griddata_parser.grid_search import GridSearch

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

class Watcher(multiprocessing.Process):
    def __init__(self, config: Config, runner_queue: multiprocessing.Queue):
        self.shutdown_callback = multiprocessing.Event()
        self.runner_queue = runner_queue
        self.config = config
        self.result = {"matches": [], "filtered_grids":[]}
        self.hit = False
        self.matches = config.matches
        self.json_files = {}
        self.our_dir_name = None
        self.our_dir = None
        super().__init__()

    def compare_file_set(self):
        files = set(os.listdir(self.our_dir))
        json_files = {f for f in files if re.search('.*.json$', f)}
        if len(json_files) > len(self.json_files):
            new_file = {f for f in json_files if f not in self.json_files}.pop()
            logger.info(f'found: {new_file}')
            self.json_files = json_files
            return new_file

    def process_new_file(self, f):
        # reset the result dict.
        self.result = {"matches": [], "filtered_grids":[]}
        grid_data = GridData(f'{self.our_dir}/{f}')
        
        for match in self.matches:
            logger.info(f'searching for match: {match}')
            gs = GridSearch()
            result = gs(grid_data, match)
            if result:
                logger.info("Got a hit!")
                self.hit = True
                match.update({"hit": True})
                self.result["matches"].append(match)
                match.pop("hit")
                self.result["filtered_grids"].append([site.get_dict() for site in gs.filtered_grid])
            else:
                match.update({"hit": False})
                self.result["matches"].append(match)
                match.pop("hit")
                self.result["filtered_grids"].append([site.get_dict() for site in gs.filtered_grid])

        
    def run(self):
        #first, see what directorys already exist in the tmp dir.
        not_our_dirs = set(os.listdir(self.config.tmp_path))
        # then, wait to find the directory we're monitoring.
        while True:
            if self.shutdown_callback.is_set():
                break
            ls =  set(os.listdir(self.config.tmp_path))
            new_dir_set = {d for d in ls if d not in not_our_dirs}
            if new_dir_set != set():
                self.our_dir_name = new_dir_set.pop()
                self.our_dir = f'{self.config.tmp_path}/{self.our_dir_name}/'
                logger.warning(f'found directory: {self.our_dir}')
                break
            time.sleep(2)
        # next, process the mfms json output
        while not self.hit:
            if self.shutdown_callback.is_set():
                break
            new_file = self.compare_file_set()
            if new_file is not None:
                time.sleep(0.1)
                self.process_new_file(new_file)
            if self.hit:
                #skip sleep if hit
                break
            time.sleep(2)
        # after a hit, do the after hit stuff.
        if self.hit:
            logger.debug("begin after hit routine")
            if self.config.after_hit_epochs > 0:
                logger.info("waiting another {self.config.after_hit_epochs} epochs before ending sim.")
                epochs_since_hit = 0
                while epochs < self.config.after_hit_epochs:
                    if self.shutdown_callback.is_set():
                        break
                    # we don't process json files after a hit.
                    if self.compare_file_set() is not None:
                        ++epochs_since_hit
            our_output_dir = f'{self.config.output_path}/{self.our_dir_name}'
            if self.config.copy_all:
                logger.info(f"Copying all data from {self.our_dir} to {our_output_dir}")
                shutil.copytree(self.our_dir, our_output_dir)
            if self.config.result_to_file:
                if not os.path.exists(our_output_dir):
                    logger.info(f"Making directory {our_output_dir}")
                    os.mkdir(our_output_dir)
                with open(f'{our_output_dir}/result.json', '+w') as f:
                    logger.info(f"writing file {our_output_dir}/result.json")
                    f.write(json.dumps(self.result))
            if self.config.stop_mfms:
                logger.info("Sending shutdown command to runner")
                self.runner_queue.put("shutdown")

