import logging
from .config import Config
import re
import os

logger = logging.getLogger(__name__)
class Marshal:
    def __init__(self, config: Config):
        self.config = config
                 
    def __call__(self, data: dict):
        """
        This is the marshal function for the Config class. Basically, it raises warnings or rejects config option values.
        Each valid config option has a check function. The config keys and their check functions are listed in the funcs
        dict below. Other keys found in the data (from the loaded config) are silently ignored. 
        Marshal will also validate the default values when used. E.g., if there's a path used from the default value in the 
        Config class, Marshal will make sure that it's not a file that already exists.
        Marshall treats the command check separately, performing this check last in order to appent the output dir ("-d" or 
        "--dir") option to mfms.
        """
        logger.warning(f'loaded config: {data}')
        funcs = {
            "matches": self.matches_check,
            "tmp_path": self.tmp_path_check,
            "output_path": self.output_path_check,
            }
        for key in funcs.keys():
            try:
                #set config to mashalled value
                setattr(self.config, key, funcs[key](data[key]))
            except KeyError:
                logger.warning(f"key '{key}' not found in config. using default, '{getattr(self.config, key)}'.")
                # don't forget to make sure the default value is also conformant.
                funcs[key](getattr(self.config, key))

        # command check comes last to append the already-marshalled tmp_path:
        try:
            self.config.command = self.command_check(data["command"])
        except KeyError:
            self.config.command = self.command_check(self.config.command)
            logger.warning(f"key 'command' not found in config. using default, '{self.config.command}'.")
            

    def command_check(self, data: str):
        if re.match(data, "-d") or re.match(data, "--dir"):
            logger.warning("-d or --dir option specified in command string. This can cause unexpected behavior.")
            return data
        else:
            return f'{data} -d {self.config.tmp_path}'


    def matches_check(self, data: list):
        return data

    def tmp_path_check(self, data: str):
        if os.path.exists(data):
            if os.path.isfile(data):
                raise Exception(f"Cannot use tmp path {data}. Path exists and it's a file.")
        else:
            os.mkdir(data)
        return data

    def output_path_check(self, data: str):
        if os.path.exists(data):
            if os.path.isfile(data):
                raise Exception(f"Cannot use output path {data}. Path exists and it's a file.")
        else:
            os.mkdir(data)
        return data
        

