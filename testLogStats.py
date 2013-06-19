import unittest
import random
import os
import time
import datetime

from logStats import LogStats
from logStats import EntryParser

from config import log_folder

class TestLogStats(unittest.TestCase):
    def setUp(self):
        """
            Select a random log file for each test.
        """

        log_files = os.listdir(log_folder)
        self.random_log_file = log_files[random.randrange(len(log_files))]
        self.stats = LogStats(self.random_log_file)

        self.parser = EntryParser()

        self.num_lines = len(self.stats.get_log_file().readlines())
        self.stats.get_log_file().seek(0, 0)
        self.entries = self.stats.get_entries()
        self.stats.get_log_file().seek(0, 0)

    def tearDown(self):
        self.stats.get_log_file().close()
       
    def test_open_file(self):
        self.assertIsNotNone(self.stats.get_log_file())

    def test_read_lines(self):
        """
            Helped me find why a different test didn't pass.
        """

        for line in range(random.randrange(self.num_lines)):
            self.assertIsNotNone(self.stats.get_line())

    def validate_date(self, date):
        result = None
        try:
            result = time.strptime(date, '%Y-%m-%d')
        except ValueError:
              print('Invalid date!')

        return result

    def test_parse_date(self):
        for line_number in range(random.randrange(self.num_lines)):
            current_line = self.stats.get_line()
            date = self.parser.parse_date(current_line)
            self.assertIsNotNone(self.validate_date(date))

    def validate_interval(self, since, until):
        result = None
        try:
            since_date = datetime.datetime.fromtimestamp(int(since)).strftime('%Y-%m-%d %H:%M:%S')
            until_date = datetime.datetime.fromtimestamp(int(until)).strftime('%Y-%m-%d %H:%M:%S')
            result = (since_date, until_date)
        except ValueError:
            print('Invalid since/until date!')

        return result
            
    def test_parse_interval_limits(self):
        '''
            Tests parser on 'since' and 'until' values.
        '''
        
        for line_number in range(random.randrange(self.num_lines)):
            current_line = self.stats.get_line()
            if not self.parser.is_entry_valid(current_line):
                continue
            (since, until) = self.parser.parse_interval(current_line)
            self.assertIsNotNone(self.validate_interval(since, until))

    def test_organize_by_day(self):
        for line_number in range(random.randrange(self.num_lines)):
            current_line = self.stats.get_line()
            if not self.parser.is_entry_valid(current_line):
                continue
            date = self.parser.parse_date(current_line)
            interval = self.parser.parse_interval(current_line)

            self.assertTrue(date in self.entries)
            self.assertTrue(interval in self.entries[date])

    def test_interval_limits(self):
        for req_date in self.entries:
            limits = self.stats.get_previous_months_dates(req_date)
            self.assertEqual(len(limits), 3)
            for date in limits:
                self.assertTrue(type(date) is datetime.datetime)

    def test_convert_dates_timestamp(self):
        for req_date in self.entries:
            limits = self.stats.get_previous_months_dates(req_date)
            new_limits = self.stats.convert_timestamp(limits)
            self.assertEqual(len(limits), 3)
            for date in new_limits:
                self.assertTrue(type(date) is float)

    def test_compare_dates_day(self):
        for req_date in self.entries:
            limits = self.stats.get_previous_months_dates(req_date)
            new_limits = self.stats.convert_timestamp(limits)
            results = self.stats.compare_dates_day(new_limits, self.entries[req_date])
            self.assertIsNotNone(results)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
