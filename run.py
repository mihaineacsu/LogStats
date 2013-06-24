import os
import re
import ast
import gzip
import tarfile
import csv
import sys
import datetime

import numpy
import matplotlib.pyplot as plt

from StatsFromLog import StatsFromLog
from config import log_folder, results_folder

def ensure_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def set_env():
    """
        Set up dir to save results, returns path to dir.
    """

    results_path = os.path.join(os.getcwd(), results_folder)
    ensure_dir(results_path)

    current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M-%S')
    save_path = os.path.join(results_path, current_time)
    ensure_dir(save_path)

    return save_path

def extract_logs():
    """
        Logs for each each machine are kept in tar gz achives.
        
        Extract all found archives in separate folder.
    """

    for f in os.listdir(log_folder):
        if os.path.splitext(f)[1] == '.tgz':
            tar_path = os.path.join(log_folder, f)
            tar_file = tarfile.open(tar_path, 'r')

            # Create dir for extraction
            extract_path = os.path.join(log_folder, os.path.splitext(f)[0])
            ensure_dir(extract_path)

            # Extract archive content in it's own dir
            items = tar_file.getnames()
            for item in items:
                item_path = os.path.join(extract_path, item)
                if not os.path.exists(item_path):
                    tar_file.extract(item, extract_path)

def get_files(dir_name):
    """
        Return a dict with dir names as keys,
        and the files in dir as values.

        Log files found 'log_folder' are kept under '.'.
    """

    files = {}
    for f in os.listdir(dir_name):
        if os.path.splitext(f)[1] == '.tgz' or f == ".DS_Store":
            continue

        if os.path.isdir(os.path.join(log_folder, f)):
            if dir_name is not log_folder:
                continue
            files[f] = get_files(os.path.join(log_folder, f))['.']
        else:
            files.setdefault('.', []).append(f)

    return files

def combine_logs(logs):
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

def compute_overall_intervals(machine_stats):
    """
        Sum up all accesses for each interval on all days.
        'machine_stats" contains accesses on intervals for each day.
        
    """

    intervals = 19
    stats_overall = [0] * intervals
    for day in machine_stats:
        stats_overall = [(x + y) for x, y in zip(stats_overall,
                machine_stats[day])]

    return stats_overall

def compute_overall_days(machine_stats):
    """
        Sum up all accesses for each day
        'machine_stats" contains accesses on intervals for each day.
    """

    stats_overall = {}
    for day in machine_stats:
        stats_overall[day] = sum(machine_stats[day])

    return stats_overall

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
        results_overall = compute_overall_intervals(results)
        for i in results_overall:
            writer.writerow([i, time_intervals[index]])
            index = index + 1

def plot_by_intervals(list_overall, title):
    plt.figure()

    intervals = range(0, 91, 5)[1:]
    intervals.append('older')
    x_axis = numpy.arange(len(intervals))

    width = x_axis[1] / float(len(list_overall))

    all_bars = []
    colors = ['blue', 'black', 'red']
    col_index = 0

    for machine in list_overall:
        all_bars.append(plt.bar(x_axis, list_overall[machine], width=width,
                    color=colors[col_index]))
        x_axis = x_axis + width
        col_index = col_index + 1

    col_index = 0
    for bars in all_bars:
        for bar in bars:
            height = bar.get_height()
            if height == 0:
                continue
            plt.text(bar.get_x() + bar.get_width() / 2., 1000 + height,
                    '%d'%int(height), ha='center', va='bottom',
                    color=colors[col_index], rotation=90)
        col_index = col_index + 1

    plt.title(title)
    plt.xticks(x_axis, intervals, size='small')
    plt.legend((bar[0] for bar in all_bars), list_overall.keys())
    plot_set_settings()

def plot_by_days(days_dict, title):
    plt.figure()

    days = sorted(days_dict.keys())
    x_axis = numpy.arange(len(days))

    width = x_axis[1] / float(len(days))

    acc = []
    for day in days:
        acc.append(days_dict[day])

    bars = plt.bar(x_axis, acc, width=width)
    x_axis = x_axis + width

    for bar in bars:
        height = bar.get_height()
        if height == 0:
            continue

        plt.text(bar.get_x() + bar.get_width() / 2., 1.05 * height,
                '%d'%int(height), ha='center', va='bottom', rotation=90)

    plt.title(title)
    plt.xticks(x_axis, days, size='small')
    plot_set_settings()

def plot_set_settings():
    """
        Set plot figure settings. Needs to be called
        after each new plot figure.
    """

    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    plt.ylabel('accesses')
    plt.grid(True, which="both", linestyle="dotted", alpha=0.7)
    plt.autoscale(tight=True)

def plot_custom(overall_intervals, overall_day):
    """
        Plot apis aggregated
    """

    machines = overall_intervals
    prod_apis = {'prod-api1': machines['prod-api1'],
        'prod-api2': machines['prod-api2']}
    plot_by_intervals(prod_apis, "prod api's")

    ubvu_api = {'ubvu-api1': machines['ubvu-api1']}
    plot_by_intervals(ubvu_api, 'ubvu api')

    all_apis = dict(prod_apis.items() + ubvu_api.items())
    plot_by_intervals(all_apis, 'all')

    machines = overall_day
    for m in machines:
        plot_by_days(machines[m], m + " by days")

    plt.show()

def main():
    save_folder = set_env()
    extract_logs()
    dir_dict = get_files(log_folder)

    machines_intervals = {}
    machines_days = {}
    for d in dir_dict:
        stats_log = []
        for f in dir_dict[d]:
            if d is not '.':
                f = os.path.join(d, f)
            stats_log.append(StatsFromLog(f).compute())

        stats_machine = combine_logs(stats_log)
        write_to_file(save_folder, d, stats_machine)

        # all stats organized by intervals or days for each machine
        machines_intervals[d] = compute_overall_intervals(stats_machine)
        machines_days[d] = compute_overall_days(stats_machine)

    plot_custom(machines_intervals, machines_days)

if __name__ == '__main__':
    sys.exit(main())
