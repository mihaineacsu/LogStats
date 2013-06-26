import re
import datetime
import time

from config import filters

class EntryParser:
    """
        Class used to parse and validate entries in log file.
    """

    def parse_date(self, line):
        """
            Skip first character '[',
            and return the first elem till ':' which is the date
        """

        line = line[1:]

        return line.partition(':')[0]

    def get_since(self, line):
        """
            Return 'since' timestamp value.
        """
        
        since = re.search(r'since=\d+', line).group()
        return re.search(r'\d+', since).group()

    def get_until(self, line, date):
        """
            Return 'until' timestamp value.

            If 'until' value is missing, set it to date of request
        """

        until = re.search(r'until=\d+', line)

        if not until:
            date = datetime.datetime.strptime(date, '%d/%b/%Y')
            return str(time.mktime(date.timetuple()))

        return re.search(r'\d+', until.group()).group()

    def parse_interval(self, line):
        """
            Return a (since, until) tuple from line
        """

        date = self.parse_date(line)

        return (self.get_since(line), self.get_until(line, date))

    def is_interval_valid(self, interval):
        """
            Check whether 'since' values are valid.
            Faulty entries with 'since=0' have been found in log.
        """

        if len(interval) != 2:
            return False

        since = interval[0]
        if since is None or int(since) == 0:
            return False

        return True

    def is_entry_valid(self, line):
        """
            Check if log entry contains data request for a certain interval
            by checking if all filter entries apply.
            Filter entries are set in config.py
        """

        if 'since' not in line:
            return False

        for filter_entry in filters:
            if filter_entry not in line:
                return False

        return True
