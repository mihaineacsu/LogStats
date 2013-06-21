import unittest
import random
import os
import time
import datetime

from logStats import LogStats

from config import log_folder

class TestLogStats(unittest.TestCase):
    def setUp(self):
        """
            Selects a random log file for each test.
        """

        log_files = os.listdir(log_folder)
        random_log_name = log_files[random.randrange(len(log_files))]
        print random_log_name
        self.logStats = LogStats(random_log_name)

        self.parser = self.logStats.parser

        log_file = self.logStats.get_log_file()
        self.num_lines = len(log_file.readlines())
        log_file.seek(0, 0)

        self.entries = self.logStats.get_entries_day()
        log_file.seek(0, 0)

    def tearDown(self):
       self.logStats.get_log_file().close()

#    def test_open_file(self):
#        self.assertIsNotNone(self.logStats.get_log_file())
#
#    def test_read_lines(self):
#        """
#            Helped me find why a different test didn't pass, best to be kept.
#        """
#
#        for line_num in range(random.randrange(self.num_lines)):
#            line = self.logStats.get_entry()
#            if not line:
#                continue
#            self.assertIsNotNone(line)
#
#    def validate_date(self, date):
#        result = None
#
#        try:
#            result = datetime.datetime.strptime(date, '%d/%b/%Y')
#        except ValueError:
#            print('Invalid date!')
#
#        return result
#
#    def test_parse_date(self):
#        for line_number in range(random.randrange(self.num_lines)):
#            current_line = self.logStats.get_entry()
#            if not current_line:
#                continue
#            date = self.parser.parse_date(current_line)
#
#            self.assertIsNotNone(self.validate_date(date))
#
#    def validate_interval(self, interval):
#        since = interval[0]
#        until = interval[1]
#        result = None
#        try:
#            since_date = datetime.datetime.fromtimestamp(float(since)).strftime('%Y-%m-%d %H:%M:%S')
#            until_date = datetime.datetime.fromtimestamp(float(until)).strftime('%Y-%m-%d %H:%M:%S')
#            result = (since_date, until_date)
#        except ValueError:
#            print('Invalid since/until date!')
#
#        return result
#
#    def test_parse_interval_limits(self):
#        '''
#            Tests parser on returning 'since' and 'until' values.
#        '''
#
#        for line_number in range(random.randrange(self.num_lines)):
#            current_line = self.logStats.get_entry()
#            if not current_line:
#                continue
#            interval = self.parser.parse_interval(current_line)
#            if not self.parser.is_interval_valid(interval):
#                continue
#            self.assertIsNotNone(self.validate_interval(interval))
#
#    def test_organize_by_day(self):
#        for line_number in range(random.randrange(self.num_lines)):
#            current_line = self.logStats.get_entry()
#            if not current_line:
#                continue
#            date = self.parser.parse_date(current_line)
#            interval = self.parser.parse_interval(current_line)
#            if not self.parser.is_interval_valid(interval):
#                continue
#            self.assertTrue(date in self.entries)
#            self.assertTrue(interval in self.entries[date])
#
#    def test_previous_intervals_dates(self):
#        for date in self.entries:
#            prev_intervals = self.logStats.get_previous_intervals(date)
#            #we're looking at every 5 days intervals, and I added older
#            #than 90 days
#            self.assertEqual(len(prev_intervals), 90 / 5)
#            for prev_date in prev_intervals:
#                self.assertTrue(type(prev_date) is datetime.datetime)
#
#    def test_convert_dates_timestamp(self):
#        for date in self.entries:
#            prev_intervals = self.logStats.get_previous_intervals(date)
#            conv_intervals = self.logStats.convert_timestamp(prev_intervals)
#            self.assertEqual(len(conv_intervals), 90 / 5)
#            for interval in conv_intervals:
#                self.assertTrue(type(interval) is float)
#
#    def test_get_stats(self):
#        for date in self.entries:
#            prev_intervals = self.logStats.get_previous_intervals(date)
#            conv_intervals = self.logStats.convert_timestamp(prev_intervals)
#            day_stats = self.logStats.get_stats(conv_intervals, self.entries[date])
#            self.assertIsNotNone(day_stats)
#
    def test_plot(self):
        all_stats = []
        for date in self.entries:
            prev_intervals = self.logStats.get_previous_intervals(date)
            new_months = self.logStats.convert_timestamp(prev_intervals)
            all_stats.append(self.logStats.get_stats(new_months, self.entries[date]))

        overall_stats = self.logStats.gather_overall_stats(all_stats)
        self.logStats.plot_stats(all_stats, overall_stats, self.entries)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
