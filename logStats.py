import os
import re
import ast

from config import log_folder

class EntryParser:
    def parse_date(self, line):
        #skip first character '['
        line = line[1:]
        return re.split('\s', line)[0]

    def get_since(self, line):
        """
            Returns 'since' timestamp value.
        """

        since_index = line.find('since')
        newline = line[since_index:]
        return newline[:newline.find(',')].split()[1]

    def get_until(self, line):
        """
            Returns 'until' timestamp value.
        """

        until_index = line.find('until')
        newline = line[until_index:]
        return newline[:newline.find('}')].split()[1]

    def parse_interval(self, line):
        return (self.get_since(line), self.get_until(line))

    def is_line_valid(self, line):
        """
            Checks if log entry contains data request for a certain interval.
        """

        if line.find('since') != -1:
            return True
        return False

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
