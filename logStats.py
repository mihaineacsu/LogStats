import os
import re
import ast
import time
import datetime
import urlparse
import gzip
import tarfile
import csv

import numpy
import matplotlib.pyplot as plt
from dateutil.relativedelta import *

from config import log_folder, results_folder, filters

class LogStats:
    def __init__(self, log_file):
        print log_file
        full_path = os.path.join(log_folder, log_file)
        print full_path
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
            Returns a valid entry or empty string is EOF has been reached.
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

def ensure_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def set_env():
    results_path = os.path.join(os.getcwd(), results_folder)
    ensure_dir(results_path)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M-%S')
    save_path = os.path.join(results_path, current_time)
    ensure_dir(save_path)
    return save_path

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

def compute_overall(results):
    overall = []
    for i in range(19):
        overall.append(0)
    for day in results:
        overall = [(x + y) for x, y in zip(overall, results[day])]
    return overall

def write_to_file(save_folder, machine_name, results):
    if machine_name is '.':
        machine_name = 'untitled'
    save_path = os.path.join(save_folder, machine_name)
    ensure_dir(save_path)
    for day in results:
        f_name = datetime.datetime.strptime(day, "%d/%b/%Y").strftime('%Y-%m-%d')
        with open(os.path.join(save_path, f_name) + '.csv', 'w+') as f:
            writer = csv.writer(f, delimiter=",")
            time_intervals = range(0, 91, 5)[1:]
            time_intervals.append('older')
            writer.writerow(['Accesses', 'Time intervals'])
            index = 0
            for i in results[day]:
                writer.writerow([i, time_intervals[index]])
                index = index + 1
    with open(os.path.join(save_path, 'overall_' + machine_name) + '.csv', 'w+') as f:
        writer = csv.writer(f, delimiter=",")
        time_intervals = range(0, 91, 5)[1:]
        time_intervals.append('older')
        writer.writerow(['Accesses', 'Time intervals'])
        index = 0
        results_overall = compute_overall(results)
        for i in results_overall:
            writer.writerow([i, time_intervals[index]])
            index = index + 1

def plot_individual_graph(list_machines):
    for machine in list_machines:
        fig = plt.figure()
        if machine is '.':
            fig.suptitle('untitled', fontsize=20)
        fig.suptitle(machine, fontsize=20)
        x_axis = numpy.arange(len(list_machines[machine]))
        subplot = plt.subplot(111)
        bars = subplot.bar(x_axis, list_machines[machine], align='center')
        intervals = range(0, 91, 5)[1:]
        intervals.append('older')
        plt.xticks(x_axis, intervals, size='small')
        for bar in bars:
            height = bar.get_height()
            if height == 0:
                continue
            subplot.text(bar.get_x() + bar.get_width() / 2., 5000 + height,
                    '%d'%int(height), ha='center', va='bottom')

def plot_prod_api(list_machines):
    figure = plt.figure()
    figure.suptitle("prod-api's", fontsize=20)
    x_axis = numpy.arange(len(list_overall['prod-api1']))
    subplot = plt.subplot(111)
    width = 0.4
    bars = subplot.bar(x_axis - width / 2, list_overall['prod-api1'], width, color='blue', align='center')
    bars2 = subplot.bar(x_axis + width / 2, list_overall['prod-api2'], width, color='black', align='center')
    intervals = range(0,91,5)[1:]
    intervals.append('older')
    plt.xticks(x_axis + width, intervals, size='small')
    for bar in bars:
        height = bar.get_height()
        if height == 0:
            continue
        subplot.text(bar.get_x() + bar.get_width() / 2., 1.2 * height,
                '%d'%int(height), ha='center', va='bottom', color='blue')
    for bar in bars2:
        height = bar.get_height()
        if height == 0:
            continue
        subplot.text(bar.get_x() + bar.get_width() / 2., 1.2 * height,
                '%d'%int(height), ha='center', va='bottom', color='black')

    bars_all = [bars, bars2]
    subplot.legend((bar[0] for bar in bars_all),
                ["prod-api1", "prod-api2"])

    subplot.autoscale(tight=True)

def plot_same_graph(list_machines):
    figure = plt.figure()
    figure.suptitle("all", fontsize=20)
    x_axis = numpy.arange(len(list_overall['prod-api1']))
    subplot = plt.subplot(111)
    width = 0.3
    bars = subplot.bar(x_axis - width, list_overall['prod-api1'], width, color='blue', align='center')
    bars2 = subplot.bar(x_axis, list_overall['prod-api2'], width, color='black', align='center')
    bars3 = subplot.bar(x_axis + width, list_overall['ubvu-api1'], width, color='red', align='center')
    intervals = range(0,91,5)[1:]
    intervals.append('older')
    plt.xticks(x_axis + 1.5 * width, intervals, size='small')
    subplot.autoscale(tight=True)

    bars_all = [bars, bars2, bars3]
    subplot.legend((bar[0] for bar in bars_all),
                ["prod-api1", "prod-api2", "ubvu-api1"])

def plot_custom(list_overall):
    """
        Plots prod apis aggregated in a single graph figure.
    """
    plot_prod_api(list_overall)
    new_dict = {'ubvu-api1': list_overall['ubvu-api1']}
    plot_individual_graph(new_dict)
    plot_same_graph(list_overall)
    plt.show()

if __name__ == '__main__':
    save_folder = set_env()
    extract_logs()
    dir_dict = get_files(log_folder)
    list_overall = {}

    for d in dir_dict:
        results = {}
        for f in dir_dict[d]:
            if d is not '.':
                f = os.path.join(d, f)
            stats = LogStats(f)
            results = combine(results, stats.compute())
        write_to_file(save_folder, d, results)
        list_overall[d] = compute_overall(results)

    plot_custom(list_overall)
