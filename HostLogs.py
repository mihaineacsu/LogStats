import os

from config import log_folder
from StatsFromLog import StatsFromLog
from LogEntryParser import EntryParser

PATH = os.path.join

class HostLogs():
    """
        Class used to compute stats on a host's logs.
    """

    def __init__(self, host):
        self.host_folder = PATH(log_folder, host)
        self.host_stats = None

    def compute_host_stats(self):
        """
            Gather stats from each file inside host's log folder
            and save them in object's field 'host_stats'.
        """

        if self.host_stats is not None:
            return

        parser = EntryParser()
        stats_from_logs = []
        for f in os.listdir(self.host_folder):
            # skip hidden files
            if f[0] is '.':
                continue

            file_path = PATH(self.host_folder, f)
            stats_from_logs.append(StatsFromLog(file_path, parser).compute())

        self.host_stats = self.combine_logs(stats_from_logs)


    def combine_logs(self, logs):
        """
            Combine stats from all logs on a particular host machine because
            some logs may contain entries for the same day.

            'logs' is a list of dict organized by days, the values for
            each day are the num of acccesses on a particular interval.
        """

        stats = {}
        for log in logs:
            for day in log:
                if day in stats:
                    stats[day] = [(x + y) for x, y in zip(stats[day], log[day])]
                else:
                    stats[day] = log[day]

        return stats

    def compute_overall_intervals(self):
        """
            Sum up all accesses for each interval on all days.
            'host_stats" contains accesses on intervals for each day.
        """

        self.compute_host_stats()

        intervals = 19
        stats_overall = [0] * intervals
        for day in self.host_stats:
            stats_overall = [(x + y) for x, y in zip(stats_overall,
                    self.host_stats[day])]

        return stats_overall

    def compute_overall_days(self):
        """
            Sum up all accesses for each day
            'host_stats" contains accesses on intervals for each day.
        """

        self.compute_host_stats()

        stats_overall = {}
        for day in self.host_stats:
            stats_overall[day] = sum(self.host_stats[day])

        return stats_overall
