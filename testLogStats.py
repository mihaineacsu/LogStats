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

    def test_open_file(self):
        self.assertIsNotNone(self.logStats.get_log_file())

    def test_read_lines(self):
        """
            Helped me find why a different test didn't pass, best to be kept.
        """

        for line in range(random.randrange(self.num_lines)):
            self.assertIsNotNone(self.logStats.get_entry())

    def validate_date(self, date):
        result = None

        try:
            result = datetime.datetime.strptime(date, '%d/%b/%Y')
        except ValueError:
            print('Invalid date!')

        return result

    def test_parse_date(self):
        for line_number in range(random.randrange(self.num_lines)):
            current_line = self.logStats.get_entry()
            date = self.parser.parse_date(current_line)

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

        return result

    def test_parse_interval_limits(self):
        '''
            Tests parser on returning 'since' and 'until' values.
        '''

        for line_number in range(random.randrange(self.num_lines)):
            current_line = self.logStats.get_entry()
            interval = self.parser.parse_interval(current_line)
            if not self.parser.is_interval_valid(interval):
                continue
            self.assertIsNotNone(self.validate_interval(interval))

    def test_organize_by_day(self):
        for line_number in range(random.randrange(self.num_lines)):
            current_line = self.logStats.get_entry()
            date = self.parser.parse_date(current_line)
            interval = self.parser.parse_interval(current_line)
            if not self.parser.is_interval_valid(interval):
                continue
            self.assertTrue(date in self.entries)
            self.assertTrue(interval in self.entries[date])

    def test_previous_months_dates(self):
        for date in self.entries:
            months = self.logStats.get_previous_months_dates(date)
            self.assertEqual(len(months), 3)
            for month in months:
                self.assertTrue(type(month) is datetime.datetime)

    def test_convert_dates_timestamp(self):
        for date in self.entries:
            months = self.logStats.get_previous_months_dates(date)
            new_months = self.logStats.convert_timestamp(months)
            self.assertEqual(len(new_months), 3)
            for month in new_months:
                self.assertTrue(type(month) is float)

    def test_get_date_stats(self):
        for date in self.entries:
            months = self.logStats.get_previous_months_dates(date)
            new_months = self.logStats.convert_timestamp(months)
            day_stats = self.logStats.get_date_stats(new_months, self.entries[date])
            self.assertIsNotNone(day_stats)

    def test_plot(self):
        all_stats = []
        for date in self.entries:
            months = self.logStats.get_previous_months_dates(date)
            new_months = self.logStats.convert_timestamp(months)
            all_stats.append(self.logStats.get_date_stats(new_months, self.entries[date]))

        overall_stats = self.logStats.gather_overall_stats(all_stats)
        self.logStats.plot_stats(all_stats, overall_stats, self.entries)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
