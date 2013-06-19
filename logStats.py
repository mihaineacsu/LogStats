import os
import re
import ast
import time
import datetime

from dateutil.relativedelta import *

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

    def get_previous_months_dates(self, date):
        """
            Computes the dates for all the 3 months before date;
            Returns these dates (datetime.datetime type) in a list.
        """

        dates_before = []                
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        for i in range(1,4):
            new_date = date - relativedelta(months=i)
            dates_before.append(new_date)
        return dates_before

    def convert_timestamp(self, dates):
        new_dates = []
        for date in dates:
            new_dates.append(time.mktime(date.timetuple()))
        return new_dates

    def compare_dates_day(self, previous_months, accessed_dates):
        """
            accessed_dates is list of (since, until) tuples;
            previous_months contains ending dates of previous_months intervals;
            Returns a list with the num of data accesses for each month.
        """

        results = [0, 0, 0, 0]
        for accessed_date in accessed_dates:
            since = float(accessed_date[0])
            #'month' is used to mark the accessed month in regard to date of request
            month = 0
            found = False
            for date in previous_months:
                if since > date:
                    results[month] = results[month] + 1
                    found = True
                    break
                month = month + 1

            if found is False:
                results[month] = results[month] + 1
        return results

    def gather_overall_results(self, day_results):
        """
            Uses result from each day to compute overall results
        """
        overall = [0, 0, 0 ,0]
        for day in day_results:
            overall = [(x + y) for x, y in zip(overall, day)]

        return overall
