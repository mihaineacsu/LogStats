import unittest
import random
import os

from logStats import LogStats
from config import log_folder

class TestLogStats(unittest.TestCase):
    def setUp(self):
        """
            Select a random log file for each test.
        """

        log_files = os.listdir(log_folder)
        self.random_log_file = log_files[random.randrange(len(log_files))]
        self.stats = LogStats(self.random_log_file)
        
        
    def test_open_file(self):
        self.assertIsNotNone(self.stats.get_log_file())


def main():
    unittest.main()

if __name__ == '__main__':
    main()
