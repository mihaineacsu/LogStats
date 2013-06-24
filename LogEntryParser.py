import urlparse
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

        pr = urlparse.urlparse(line)
        since = urlparse.parse_qs(pr.query).get('since', [''])[0]

        if not since:
            return None

        return since.partition(' ')[0]

    def get_until(self, line, date):
        """
            Return 'until' timestamp value.

            If 'until' value is missing, set it to date of request
        """

        pr = urlparse.urlparse(line)
        until = urlparse.parse_qs(pr.query).get('until', [''])[0]

        if not until:
            date = datetime.datetime.strptime(date, '%d/%b/%Y')
            return str(time.mktime(date.timetuple()))

        return until.partition(' ')[0]

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
