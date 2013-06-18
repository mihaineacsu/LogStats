import os

from config import log_folder

class LogStats:
    def __init__(self, log_file):
        try: 
            self.log_file = open(os.path.join(log_folder, log_file), 'r')
        except IOError:
            "Could not open file"

    def get_log_file(self):
        return self.log_file
