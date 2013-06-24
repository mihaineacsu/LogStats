import urlparse
import datetime
import time

from config import filters

class EntryParser:
    def parse_date(self, line):
        """
            Skips first character '[',
            and returns the first elem till ':' which is the date
        """

        line = line[1:]
        return line.partition(':')[0]

    def get_since(self, line):
        """
            Returns 'since' timestamp value.
        """

        pr = urlparse.urlparse(line)
        try:
            since = urlparse.parse_qs(pr.query)['since'][0]
            since = since.partition(' ')[0]
        except KeyError:
            since = None
        return since

    def get_until(self, line, date):
        """
            Returns 'until' timestamp value.
            If 'until' value is missing, we set it to date of request
        """

        pr = urlparse.urlparse(line)
        try:
            until = urlparse.parse_qs(pr.query)['until'][0]
            until = until.partition(' ')[0]
        except KeyError:
            date = datetime.datetime.strptime(date, '%d/%b/%Y')
            until = str(time.mktime(date.timetuple()))
        return until

    def parse_interval(self, line):
        """
            Returns a (since, until) tuple from line
        """

        date = self.parse_date(line)
        return (self.get_since(line), self.get_until(line, date))

    def is_interval_valid(self, interval):
        """
            Checks whether 'since' values are valid.
            Faulty entries with 'since=0' have been found in log.
        """

        since = interval[0]
        if since is None or int(since) == 0:
            return False
        return True

    def is_entry_valid(self, line):
        """
            Checks if log entry contains data request for a certain interval.
            It's not valid if it doesn't contain 'since' keyword, it's not 
            GET request with mention search.
        """
        for filter_entry in filters:
            if filter_entry not in line:
                return False

        return True

