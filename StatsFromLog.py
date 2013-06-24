import os
import datetime
import time
from dateutil.relativedelta import *

from LogEntryParser import EntryParser
from config import log_folder

class StatsFromLog:
    def __init__(self, log_file):
        full_path = os.path.join(log_folder, log_file)
        try:
            if os.path.splitext(log_file)[1] == '.gz':
                self.log_file = gzip.open(full_path, 'r')
            else:
                self.log_file = open(full_path, 'r')
        except IOError:
            print "Could not open file"

        self.parser = EntryParser()

    def get_log_file(self):
        return self.log_file

    def get_entry(self):
        """
            Returns a valid log entry or empty string is EOF has been reached.
        """

        line = ""
        while not self.parser.is_entry_valid(line):
            line = self.log_file.readline()
            if not line:
                break

        return line

    def get_entries_day(self):
        """
            Organizes entries by day in a dict.
            Day of request is key, (until, since) are values.
        """

        entries = {}
        for entry in self.log_file:
            if not self.parser.is_entry_valid(entry):
                continue

            date = self.parser.parse_date(entry)
            # interval is a (since, until) tuple
            interval = self.parser.parse_interval(entry)

            if not self.parser.is_interval_valid(interval):
                continue

            # if dict already contains date entry, updates it's values
            if date in entries:
                new_list = entries.get(date)
                new_list.append(interval)
                entries[date] = new_list
            else:
                entries[date] = [interval]

        return entries

    def get_previous_intervals(self, date):
        """
            Computes dates for every 5 days before 'date'.
            Returns those dates (datetime.datetime type) in a list.
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

    def get_stats(self, previous_intervals, accessed_dates):
        """
            accessed_dates is list of (since, until) tuples;
            previous_months contains ending dates of previous_months intervals;
            Returns a list with the num of data accesses for each interval.
        """

        results = [0] * (len(previous_intervals) + 1)
        for accessed_date in accessed_dates:
            since = float(accessed_date[0])
            # 'day' is used to mark the accessed day
            # in regard to date of request
            day = 0
            found = False
            for date in previous_intervals:
                if since > date:
                    results[day] = results[day] + 1
                    found = True
                    break
                day = day + 1

            if found is False:
                results[day] = results[day] + 1

        return results

    def compute(self):
        all_stats = {}
        entries = self.get_entries_day()
        for date in entries:
            prev_intervals = self.get_previous_intervals(date)
            all_stats.setdefault(date, []).extend(self.get_stats(prev_intervals,
                        entries[date]))

        return all_stats
