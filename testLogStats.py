import unittest
import random
import os
import time
import datetime

from StatsFromLog import StatsFromLog
from LogEntryParser import EntryParser
from run import extract_logs

from config import log_folder

class TestLogStats(unittest.TestCase):
    def setUp(self):
        """
            Selects a random log file for each test.
        """

        extract_logs()
        log_files = []
        for dir_name, subdir_list, file_list in os.walk(log_folder, topdown=False):
            for f in file_list:
                if os.path.splitext(f)[1] != '.tgz' and f != '.DS_Store':
                    parent_dir = os.path.basename(dir_name)
                    log_files.append(os.path.join(parent_dir, f))
                    
        random_log_name = log_files[random.randrange(len(log_files))]
        print random_log_name

        self.parser = EntryParser()
        self.stats_log = StatsFromLog(random_log_name, self.parser)

        self.log_file = self.stats_log.get_log_file()
        self.num_lines = len(self.log_file.readlines())
        self.log_file.seek(0, 0)

        self.entries = self.stats_log.get_entries_by_day()
        self.log_file.seek(0, 0)

    def tearDown(self):
       self.log_file.close()

    def validate_date(self, date):
        result = None

        try:
            result = datetime.datetime.strptime(date, '%d/%b/%Y')
        except ValueError:
            print('Invalid date!')

        return result

    def test_parse_date(self):
        for entry in self.log_file:
            if not self.parser.is_entry_valid(entry):
                continue

            date = self.parser.parse_date(entry)

            self.assertIsNotNone(self.validate_date(date))

    def validate_interval(self, interval):
        since = interval[0]
        until = interval[1]
        result = None
        try:
            since_date = datetime.datetime.fromtimestamp(float(since)).strftime('%Y-%m-%d %H:%M:%S')
            until_date = datetime.datetime.fromtimestamp(float(until)).strftime('%Y-%m-%d %H:%M:%S')
            result = (since_date, until_date)
        except ValueError:
            print('Invalid since/until date!')
        finally:
            return result

    def test_parse_interval_limits(self):
        '''
            Tests parser on returning 'since' and 'until' values.
        '''

        for entry in self.log_file:
            if not self.parser.is_entry_valid(entry):
                continue

            interval = self.parser.parse_interval(entry)

            if not self.parser.is_interval_valid(interval):
                continue

            self.assertIsNotNone(self.validate_interval(interval))

    def test_organize_by_day(self):
        for entry in self.log_file:
            if not self.parser.is_entry_valid(entry):
                continue

            date = self.parser.parse_date(entry)
            interval = self.parser.parse_interval(entry)

            if not self.parser.is_interval_valid(interval):
                continue

            self.assertTrue(date in self.entries)
            self.assertTrue(interval in self.entries[date])

    def test_previous_intervals_dates(self):
        for date in self.entries:
            prev_intervals = self.stats_log.get_prev_intervals(date)
            self.assertEqual(len(prev_intervals), 90 / 5)

            for prev_date in prev_intervals:
                self.assertTrue(type(prev_date) is float)

    def test_get_stats(self):
        for date in self.entries:
            prev_intervals = self.stats_log.get_prev_intervals(date)
            day_stats = self.stats_log.get_day_stats(prev_intervals, self.entries[date])
            self.assertIsNotNone(day_stats)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
