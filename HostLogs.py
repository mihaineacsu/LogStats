import os

from config import log_folder, results_folder
from StatsFromLog import StatsFromLog
from LogEntryParser import EntryParser

PATH = os.path.join

class HostLogs():
    def __init__(self, host):
        parser = EntryParser()

        host_folder = PATH(log_folder, host)
        stats_from_logs = []

        for f in os.listdir(host_folder):
            if f == '.DS_Store':
                continue
            stats_from_logs.append(StatsFromLog(PATH(host, f), parser).compute())

        self.stats_machine = self.combine_logs(stats_from_logs)

    def combine_logs(self, logs):
        """
            Combine stats from all logs on a particular machine.
            'stats' is a dict organized by days, the values for
            each day are the num of acccesses on a particular interval.
        """

        machine = {}
        for log in logs:
            for day in log.keys():
                if day in machine:
                    machine[day] = [(x + y) for x, y in zip(machine[day], log[day])]
                else:
                    machine[day] = log[day]

        return machine

    def compute_overall_intervals(self):
        """
            Sum up all accesses for each interval on all days.
            'machine_stats" contains accesses on intervals for each day.
        """
        machine_stats = self.stats_machine

        intervals = 19
        stats_overall = [0] * intervals
        for day in machine_stats:
            stats_overall = [(x + y) for x, y in zip(stats_overall,
                    machine_stats[day])]

        return stats_overall

    def compute_overall_days(self):
        """
            Sum up all accesses for each day
            'machine_stats" contains accesses on intervals for each day.
        """
        machine_stats = self.stats_machine

        stats_overall = {}
        for day in machine_stats:
            stats_overall[day] = sum(machine_stats[day])

        return stats_overall
