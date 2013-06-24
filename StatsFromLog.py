import os
import datetime
import time

from dateutil.relativedelta import *

from LogEntryParser import EntryParser
from config import log_folder

class StatsFromLog:
    """
        Class used to compute stats for each log files.
        Uses EntryParser to gather data from valid entries.
    """
        
    def __init__(self, log_file, parser):
        full_path = os.path.join(log_folder, log_file)
        try:
            if os.path.splitext(log_file)[1] == '.gz':
                self.log_file = gzip.open(full_path, 'r')
            else:
                self.log_file = open(full_path, 'r')
        except IOError:
            print "Could not open file"

        self.parser = parser

    def get_entries_by_day(self):
        """
            Organize log entries by day in a dict.
            Day of request is key, (until, since) are values.
        """

        log_entries = {}
        for entry in self.log_file:
            if not self.parser.is_entry_valid(entry):
                continue

            date = self.parser.parse_date(entry)
            # interval is a (since, until) tuple
            interval = self.parser.parse_interval(entry)

            if not self.parser.is_interval_valid(interval):
                continue

            # if dict already contains date entry, updates it's values
            if date in log_entries:
                new_list = log_entries.get(date)
                new_list.append(interval)
                log_entries[date] = new_list
            else:
                log_entries[date] = [interval]

        return log_entries

    def get_prev_intervals(self, date):
        """
            Compute previous dates for every 5 days before 'date'.
            Return those dates in a list.
        """

        date = datetime.datetime.strptime(date, "%d/%b/%Y")

        dates_before = []
        for i in range(5, 91, 5):
            prev_date = date - relativedelta(days=i)
            dates_before.append(prev_date)

        return self.convert_timestamp(dates_before)

    def convert_timestamp(self, dates):
        """
            Convert dates to unix timestamp.
        """

        return [time.mktime(date.timetuple()) for date in dates]

    def get_day_stats(self, previous_intervals, since_values):
        """
            Compare 'since' values with previous intervals and return 
            number of accesses to data for each past # days.
            
            'previous_intervals' is list of previous dates for every
            5 days prior to date of request.
            since_values is list of (since, until) tuples.
        """

        # '+ 1' to handle the 'older than 90 days' case
        date_stats = [0] * (len(previous_intervals) + 1)
        for accessed_interval in since_values:
            since = float(accessed_interval[0])
            # 'interval_index' is used to mark the accessed period
            # in regard to date of request
            interval_index = 0
            found = False
            for date in previous_intervals:
                if since > date:
                    date_stats[interval_index] += 1
                    found = True
                    break
                interval_index += 1

            # if 'since' is older than all previous intervals,
            # we mark it under the last position -> 'older'
            if found is False:
                date_stats[interval_index] += 1

        return date_stats

    def compute(self):
        """
            Parse log entries and return list with number of accesses for each
            past #days.
        """

        log_stats = {}
        entries = self.get_entries_by_day()

        for date in entries:
            prev_intervals = self.get_prev_intervals(date)
            log_stats.setdefault(date, []).extend(self.get_day_stats(prev_intervals,
                        entries[date]))

        return log_stats
