import logging
import yaml
import json

class Config:
    # note: certain mfms commands will cause an error for 
    command = "/usr/bin/mfms {{2H2}} -gj -ep .gen/bin/libcue.so --no-gui --haltonempty --haltonfull -cp start.mfs --run"
    matches = [
        {"equal_to": 0, "name": "Empty"},
        ]
    #ouput directory for mfms
    tmp_path = "/tmp/mfms/"
    #output directory for pymfmctl (for hits), logs, et c..
    output_path = "pymfmctl/"
    # whether to copy to the path given by output_path
    copy_all = True
    # whether to write result json to file
    result_to_file = True
    # number of epochs after a hit to run the sim
    after_hit_epochs = 0
    # whether to stop the mfms process after a hit is complete and all of the subsequent hit behavior
    stop_mfms = True

    def __init__(self, configfile):
        from .config_marshal import Marshal
        self.marshal = Marshal(self)
        self.load(configfile)

    def load(self, f):
        #accept json or yaml.
        try:
            data = json.loads(f)
        except json.decoder.JSONDecodeError:
            with open(f) as yf:
                data = yaml.load(yf)
        self.marshal(data)
