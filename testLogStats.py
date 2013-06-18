import unittest
import random
import os
import time

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

        self.num_lines = len(self.stats.get_log_file().readlines())
        self.stats.get_log_file().seek(0, 0)

    def tearDown(self):
        self.stats.get_log_file().close()
       
    def test_open_file(self):
        self.assertIsNotNone(self.stats.get_log_file())

    def test_read_lines(self):
        for line in range(random.randrange(self.num_lines)):
            self.assertIsNotNone(self.stats.get_line())

    def validate_date(self, date):
        result = None
        try:
            result = time.strptime(date, '%Y-%m-%d')
        except ValueError:
              print('Invalid date!')

        return result

    def test_parse_entries(self):
        parser = EntryParser()
        for line_number in range(random.randrange(self.num_lines)):
            current_line = self.stats.get_line()
            date = parser.parse_date(current_line)
            self.assertIsNotNone(self.validate_date(date))

def main():
    unittest.main()

if __name__ == '__main__':
    main()
