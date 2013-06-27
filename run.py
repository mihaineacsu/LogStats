#! /usr/bin/python

import os
import re
import tarfile
import sys
import datetime
import argparse

import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from config import *
from HostLogs import HostLogs

USAGE_DESC = "Plot accesses to data based on logs."
PATH = os.path.join

def ensure_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def extract_logs():
    """
        Logs for each each machine are kept in tar gz achives.
        
        Extract all found archives in separate folder.
    """

    if not os.path.exists(log_folder):
        print "log_folder: '" + log_folder + "' does not exist."
        sys.exit(1)

    for f in os.listdir(log_folder):
        if os.path.splitext(f)[1] == '.tgz':
            tar_file = tarfile.open(PATH(log_folder, f), 'r')

            # Create dir for extraction
            extract_path = PATH(log_folder, os.path.splitext(f)[0])
            ensure_dir(extract_path)

            # Extract archive content in it's own dir
            items = tar_file.getnames()
            for item in items:
                item_path = PATH(extract_path, item)
                if not os.path.exists(item_path):
                    tar_file.extract(item, extract_path)

def plot_by_intervals(list_overall, title, pdf_file):
    """
        Plot accesses on each past interval.
    """

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
            # Don't print bar score if it's equal to 0
            if height == 0:
                continue

            plt.text(bar.get_x() + bar.get_width() / 2., 1000 + height,
                    '%d'%int(height), ha='center', va='bottom',
                    color=colors[col_index], rotation=90)
        col_index = col_index + 1

    plt.title(title)
    plt.xticks(x_axis, intervals, size='small')
    plt.legend((bar[0] for bar in all_bars), list_overall.keys())
    plot_set_settings(pdf_file)

def plot_by_days(days_dict, title, pdf_file):
    """"
        Plot number of requests per day.
    """

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
        # Don't print bar score if it's equal to 0
        if height == 0:
            continue

        plt.text(bar.get_x() + bar.get_width() / 2., 1.05 * height,
                '%d'%int(height), ha='center', va='bottom', rotation=90)

    plt.title(title)
    plt.xticks(x_axis, days, size='small')
    plot_set_settings(pdf_file)

def plot_set_settings(pdf_file):
    """
        Set plot figure settings. Needs to be called
        after each new plot figure.
    """

    plt.subplots_adjust(left=subplot_left, right=subplot_right,
            top=subplot_top, bottom=subplot_bottom)
    plt.ylabel('accesses')
    plt.grid(b=show_grid_axes, which="both", linestyle=grid_linestyle,
            alpha=grid_alpha)
    plt.autoscale(tight=True)

    plt.savefig(pdf_file, format='pdf')

def plot(overall_intervals, overall_day, save_file):
    """
        Plot apis aggregated
    """

    if save_file is None:
        save_file = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M-%S') + '.pdf'
    pdf_file = PdfPages(save_file)

    plot_by_intervals(overall_intervals, 'Accesses to each interval', pdf_file)

    for host in overall_day:
        plot_by_days(overall_day[host], host + " by days", pdf_file)

    pdf_file.close()

    plt.show()

def get_hosts_from_logs():
    """
        Each log archive is extracted in it's own dir.
        Return a list of dirs, each dir represing a host.
    """

    extract_logs()

    hosts = []
    for item in os.listdir(log_folder):
        item_path = PATH(log_folder, item)
        if os.path.isdir(item_path):
            hosts.append(item)

    return hosts
            
def match_hosts(args_hosts):
    """
        Returns a list of matched hosts received as
        command line args and hosts that have logs.
    """

    hosts = get_hosts_from_logs()

    matched = []
    for arg_host in args_hosts:
        matched.extend([word for index, word in enumerate(hosts) if
                re.search(arg_host, word)])

    return matched

def get_args():
    """
        Print usage info, parse command-line args
        and match hosts received as args with hosts that have logs
        in 'log_folder'.
    """

    parser = arg_parser = argparse.ArgumentParser(description = USAGE_DESC,
            prog='run')

    parser.add_argument('-s', '--save', nargs=1,
            default = [None], type = str,
            help="""Save plots in specified file.
                    By default files are saved using current time/date stamp.""")
                 
    
    parser.add_argument('-H', '--HOST', type=str, required=True, nargs='+',
            help="""Plot specified hosts.""")

    args = vars(parser.parse_args(sys.argv[1:]))
    
    matched_hosts = match_hosts(args['HOST'])

    if len(matched_hosts) != len(args['HOST']):
        print "Didn't match all yours hosts.\n" \
            "Available host logs: " + '%s' % \
            ', '.join(map(str, get_hosts_from_logs()))

        sys.exit(1)

    args['HOST'] = matched_hosts
    args['save'] = args['save'][0]

    return args

def main():
    args = get_args()

    machines_intervals = {}
    machines_days = {}
    for h in args['HOST']:
        host = HostLogs(h)

        machines_intervals[h] = host.compute_overall_intervals()
        machines_days[h] = host.compute_overall_days()

    plot(machines_intervals, machines_days, args['save'])

if __name__ == '__main__':
    sys.exit(main())
