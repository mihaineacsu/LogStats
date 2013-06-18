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

    def is_entry_valid(self, line):
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

        self.parser = EntryParser()

    def get_log_file(self):
        return self.log_file

    def get_line(self):
        return self.log_file.readline()

    def get_entries(self):
        """
            Organizes entries by day in a dict.
            Day of request is key, (until, since) are values.
        """

        entries = {}
        for entry in self.log_file:
            if not self.parser.is_entry_valid(entry):
                continue
            date = self.parser.parse_date(entry)
            interval = self.parser.parse_interval(entry)
            if date in entries:
                new_list = entries.get(date)
                new_list.append(interval)
                entries[date] = new_list
            else:
                entries[date] = [interval]

        return entries
