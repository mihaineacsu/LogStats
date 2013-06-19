import os
import re
import ast
import time
import datetime

import numpy
import matplotlib.pyplot as plt
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

    def plot_stats(self, day_stats, overall_stats, entries):
        num_days = len(day_stats)
        x_day_location = numpy.arange(num_days)
        width = 0.1

        one_month_ago = [a for a, b, c, d in day_stats]
        two_months_ago = [b for a, b, c, d in day_stats]
        three_months_ago = [c for a, b, c, d in day_stats]
        older = [d for a, b, c, d in day_stats]
        days = [day for day in entries]
        print days

        days_plot = plt.figure()                    
        days_ax0 = days_plot.add_subplot(111)

        rect_one_month = days_ax0.bar(x_day_location, one_month_ago,
                width, color='r')
        rect_two_months = days_ax0.bar(x_day_location + width, two_months_ago,
                width, color='g')
        rect_three_months = days_ax0.bar(x_day_location + 2 * width, three_months_ago,
                width, color='b')
        rect_older = days_ax0.bar(x_day_location + 3 * width, older, width, color='y')
        rects = [rect_one_month, rect_two_months, rect_three_months, rect_older]

        days_ax0.set_ylabel('Accesses')
        days_ax0.set_title('Accesses to data by day')
        days_ax0.set_xticks(x_day_location + width)
        days_ax0.set_xticklabels(days)
        days_ax0.legend((rect[0] for rect in rects),
                ("One month ago", "Two months ago", "Three months ago", "Older"))

        for rect in rects:
            for index in range(len(rects)):
                height = rect[index].get_height()
                days_ax0.text(rect[index].get_x()+rect[index].get_width()/2.,
                        1.05*height, '%d'%int(height), ha='center', va='bottom')

        plt.show()
