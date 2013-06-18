import os
import re

from config import log_folder

class EntryParser:
    def parse_date(self, line):
        #skip first character '['
        line = line[1:]
        date = re.split('\s', line)[0]
        return date

class LogStats:
    def __init__(self, log_file):
        try: 
            self.log_file = open(os.path.join(log_folder, log_file), 'r')
        except IOError:
            "Could not open file!"

    def get_log_file(self):
        return self.log_file

    def get_line(self):
        return self.log_file.readline()
