import os
import re
import ast
import time
import datetime
import urlparse
import gzip
import tarfile

import numpy
import matplotlib.pyplot as plt
from dateutil.relativedelta import *

from config import log_folder, filters


class LogStats:
    def __init__(self, log_file):
        full_path = os.path.join(log_folder, log_file)
        try:
            if os.path.splitext(log_file)[1] == '.gz':
                self.log_file = gzip.open(full_path, 'r')
            else:
                self.log_file = open(full_path, 'r')
        except IOError:
            print "Could not open file"

        self.parser = self.EntryParser()

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

    def get_log_file(self):
        return self.log_file

    def get_entry(self):
        """
            Returns a valid entry or empty string is EOF has been reached
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
            interval = self.parser.parse_interval(entry)
            if not self.parser.is_interval_valid(interval):
                continue
            #if dict already contains date entry, updates it's values
            if date in entries:
                new_list = entries.get(date)
                new_list.append(interval)
                entries[date] = new_list
            else:
                entries[date] = [interval]

        return entries

    def get_previous_intervals(self, date):
        """
            Computes the dates for every 5 days before date.
            Returns those dates (datetime.datetime type) in a list.
        """

        dates_before = []
        date = datetime.datetime.strptime(date, "%d/%b/%Y")
        for i in range(5, 91, 5):
            new_date = date - relativedelta(days=i)
            dates_before.append(new_date)
        return dates_before

    def convert_timestamp(self, dates):
        """
            Convert dates to unix timestamp
        """

        return [time.mktime(date.timetuple()) for date in dates]

    def get_stats(self, previous_intervals, accessed_dates):
        """
            accessed_dates is list of (since, until) tuples;
            previous_months contains ending dates of previous_months intervals;
            Returns a list with the num of data accesses for each month.
        """

        results = []
        for i in range(len(previous_intervals) + 1):
            results.append(0)
        for accessed_date in accessed_dates:
            since = float(accessed_date[0])
            #'day' is used to mark the accessed day
            #in regard to date of request
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

    def gather_overall_stats(self, day_results):
        """
            Adds stats from each day to compute overall stats.
        """

        overall = []
        for i in range(len(day_results[0])):
            overall.append(0)
        for day in day_results:
            overall = [(x + y) for x, y in zip(overall, day)]

        return overall

    def compute(self):
        all_stats = {}
        entries = self.get_entries_day()
        for date in entries:
            prev_intervals = self.get_previous_intervals(date)
            new_months = self.convert_timestamp(prev_intervals)
            all_stats.setdefault(date, []).extend(self.get_stats(new_months, entries[date]))
        
        return all_stats

    def plot_stats(self, day_stats, overall_stats, entries):
        days_plot = plt.figure()
        days_ax0 = days_plot.add_subplot(111)

        x_day_location = numpy.arange(len(day_stats))
        width = 0.1

        one_month_ago = [a for a, b, c, d in day_stats]
        two_months_ago = [b for a, b, c, d in day_stats]
        three_months_ago = [c for a, b, c, d in day_stats]
        older = [d for a, b, c, d in day_stats]
        days = [day for day in entries]

        rect_one_month = days_ax0.bar(x_day_location, one_month_ago,
                width, color='r')
        rect_two_months = days_ax0.bar(x_day_location + width, two_months_ago,
                width, color='g')
        rect_three_months = days_ax0.bar(x_day_location + 2 * width,
                three_months_ago, width, color='b')
        rect_older = days_ax0.bar(x_day_location + 3 * width, older, width,
                color='y')
        rects = [rect_one_month, rect_two_months, rect_three_months, rect_older]

        month_legend = ["One month ago", "Two months ago", "Three months ago",
                "Older"]

        days_ax0.set_ylabel('Accesses')
        days_ax0.set_title('Accesses to data by day')
        days_ax0.set_xticks(x_day_location + width / 2)
        days_ax0.set_xticklabels(days)
        days_ax0.legend((rect[0] for rect in rects),
                month_legend)

        for rect in rects:
            for index in range(len(rect)):
                height = rect[index].get_height()
                days_ax0.text(rect[index].get_x() + rect[index].get_width()/2.,
                        1.05*height, '%d'%int(height), ha='center', va='bottom')

                print results
                print stats
        overall_plot = plt.figure()
        overall_ax0 = overall_plot.add_subplot(111)

        x_overall_location = numpy.arange(len(rects))
        overall_width = 0.5

        rect_overall = overall_ax0.bar(x_overall_location, overall_stats,
                overall_width, color = 'r')

        overall_ax0.set_ylabel('Accesses')
        overall_ax0.set_title('Overall accesses')
        overall_ax0.set_xticks(x_overall_location + overall_width / 2)
        overall_ax0.set_xticklabels(month_legend)

        for index in range(len(overall_stats)):
            height = rect_overall[index].get_height()
            overall_ax0.text(rect_overall[index].get_x()+rect_overall[index].get_width()/2.,
                    1.05*height, '%d'%int(height), ha='center', va='bottom')

        plt.show()

def ensure_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def set_env():
    results_folder = os.path.join(os.getcwd(), 'results')
    ensure_dir(results_folder)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M-%S')
    current_results = os.path.join(results_folder, current_time)
    ensure_dir(current_results)

def extract_logs():
    for f in os.listdir(log_folder):
        if os.path.splitext(f)[1] == '.tgz':
            tar_path = os.path.join(log_folder, f)
            tar_file = tarfile.open(tar_path, 'r')

            extract_path = os.path.join(log_folder, os.path.splitext(f)[0])
            ensure_dir(extract_path)

            items = tar_file.getnames()
            for item in items:
                item_path = os.path.join(extract_path, item)
                if not os.path.exists(item_path):
                    tar_file.extract(item, extract_path)

def get_files(dir_name):
    files = {}
    for f in os.listdir(dir_name):
        if os.path.splitext(f)[1] == '.tgz':
            continue
        if os.path.isdir(os.path.join(log_folder, f)):
            if dir_name is not log_folder:
                continue
            files[f] = get_files(os.path.join(log_folder, f))['.']
        else:
            files.setdefault('.', []).append(f)

    return files

def combine(results, stats):
    for day in stats.keys():
        if day in results:
            results[day] = [(x + y) for x, y in zip(results[day], stats[day])] 
        else:
            results[day] = stats[day]
    return results

if __name__ == '__main__':
    set_env()
    extract_logs()
    dir_dict = get_files(log_folder)
    for d in dir_dict:
        results = {}
        for f in dir_dict[d]:
            stats = LogStats(f)
            results = combine(results, stats.compute())
