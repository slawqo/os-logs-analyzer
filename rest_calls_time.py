#!/usr/bin/env python3

from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy
import uuid
import re
import sys
from prettytable import PrettyTable


REQUESTS_HEADER = "Requests"
NUMBER_OF_REQUESTS_HEADER = "Number of requests"
AVERAGE_TIME_HEADER = "Average request time"
MIN_TIME_HEADER = "Min request time"
MAX_TIME_HEADER = "Max request time"
MEDIAN_TIME_HEADER = "Median request time"
TOTAL_TIME_HEADER = "Total request time"

PLOT_PATH = "/tmp/"
PLOT_FORMAT = "png"

SYSLOGDATE = '\w+\s+\d+\s+\d{2}:\d{2}:\d{2}((\.|\,)\d{3,6})?'
DATEFMT = '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}((\.|\,)\d{3,6})?'
STATUSFMT = '(DEBUG|INFO|WARNING|ERROR|TRACE|AUDIT|CRITICAL)'
METHODFMT = '(GET|POST|PUT|DELETE)'

OSLO_LOGMATCH = '^(?P<date>%s)(?P<line>(?P<pid> \d+)? (?P<status>%s).*)' % \
            (DATEFMT, STATUSFMT)

SYSLOG_MATCH = ('^(?P<date>%s)(?P<line> (?P<host>[\w\-]+) '
                '(?P<service>[^\[\s]+):.*)' %
                (SYSLOGDATE))

SYSTEMD_MATCH = (
    '^(?P<date>%s)(?P<line> (?P<host>\S+) \S+\[\d+\]\: (?P<status>%s)?.*)' %
    (SYSLOGDATE, STATUSFMT))

SYSTEMD_MATCH = (
        '^(?P<date>%s)(?P<line> (?P<host>\S+) \S+\[\d+\]\: (?P<status>%s)?.* "(?P<method>%s) (?P<uri>.+) HTTP/1\.1\" status: (?P<resp_status>\d+)  len: (?P<resp_len>\d+) time: (?P<resp_time>\S+))' %
    (SYSLOGDATE, STATUSFMT, METHODFMT))

OSLORE = re.compile(OSLO_LOGMATCH)
SYSLOGRE = re.compile(SYSLOG_MATCH)
SYSTEMDRE = re.compile(SYSTEMD_MATCH)


def parse_line(line):
    parsed_line = {}
    m = SYSTEMDRE.match(line)
    if m:
        parsed_line['status'] = m.group('status') or "NONE"
        parsed_line['line'] = m.group('line')
        parsed_line['date'] = m.group('date')
        parsed_line['host'] = m.group('host')
        parsed_line['method'] = m.group('method')
        parsed_line['uri'] = m.group('uri')
        parsed_line['resp_status'] = m.group('resp_status')
        parsed_line['resp_len'] = m.group('resp_len')
        parsed_line['resp_time'] = m.group('resp_time')
        return parsed_line
    return None


def _format_uuid_string(string):
    return (string.replace('urn:', '')
                  .replace('uuid:', '')
                  .strip('{}')
                  .replace('-', '')
                  .lower())


def is_uuid_like(val):
    try:
        return str(uuid.UUID(val)).replace('-', '') == _format_uuid_string(val)
    except (TypeError, ValueError, AttributeError):
        return False


def get_parsed_uri(uri):
    result = []
    uri = uri.split("?")[0]
    for el in uri.split("/"):
        if is_uuid_like(el):
            el = "*"
        result.append(el)
    return "/".join(result)


def parse_file(file_path):
    logged_calls = {}
    with open(file_path) as f:
        for line in f:
            parsed_line = parse_line(line)
            if parsed_line:
                request = "%s %s" % (
                    parsed_line['method'],
                    get_parsed_uri(parsed_line['uri']))

                if request not in logged_calls.keys():
                    logged_calls[request] = {
                        'summary': {
                            'call_counts': 0,
                            'total_resp_time': 0
                        },
                        'requests': []
                    }

                logged_calls[request]['requests'].append({
                    'request at': parsed_line['date'],
                    'response length': parsed_line['resp_len'],
                    'response time': parsed_line['resp_time']
                })
    return logged_calls


def calculate_stats(data):
    for req_data in data.values():
        resp_times = [float(r['response time']) for r in req_data['requests']]
        req_data['summary']['response_times'] = resp_times
        req_data['summary']['call_counts'] = len(req_data['requests'])
        req_data['summary']['total_resp_time'] = sum(resp_times)
        req_data['summary']['min_resp_time'] = min(resp_times)
        req_data['summary']['max_resp_time'] = max(resp_times)
        req_data['summary']['median_resp_time'] = numpy.median(resp_times)
        req_data['summary']['average_time'] = (
            req_data['summary']['total_resp_time'] /
            req_data['summary']['call_counts'])


def print_results(data, sortby=AVERAGE_TIME_HEADER, desc_sort=True):
    overall_table = PrettyTable(
        [REQUESTS_HEADER, NUMBER_OF_REQUESTS_HEADER,
         AVERAGE_TIME_HEADER, MEDIAN_TIME_HEADER,
         MIN_TIME_HEADER, MAX_TIME_HEADER, TOTAL_TIME_HEADER])
    overall_table.sortby = sortby
    overall_table.reversesort = desc_sort
    for request, request_data in data.items():
        overall_table.add_row(
            [request,
             request_data['summary']['call_counts'],
             request_data['summary']['average_time'],
             request_data['summary']['median_resp_time'],
             request_data['summary']['min_resp_time'],
             request_data['summary']['max_resp_time'],
             request_data['summary']['total_resp_time']])

    print(overall_table)


def plot_graphs(data, top=None, sortby='average_time'):
    requests_to_plot = data
    if top:
        requests_to_plot = OrderedDict(
            sorted(data.items(),
                   key=lambda x: x[1]['summary'][sortby],
                   reverse=True))
    already_plotted_rows = 0
    for request, request_data in requests_to_plot.items():
        resp_times = request_data['summary']['response_times']
        x_values = range(1, len(resp_times) + 1)
        plt.scatter(x_values, resp_times, label=request)
        # Draw line with median value:
        plt.plot(x_values,
                 [request_data['summary']['median_resp_time']] * len(x_values),
                 label="Median response time")
        # Draw line with average value
        plt.plot(x_values,
                 [request_data['summary']['average_time']] * len(x_values),
                 label="Average response time")
        plt.xlabel('request')
        plt.ylabel('time')
        plt.legend()
        plt.show()

        file_name = "%s.%s" %(
            request.replace(" ", "_").replace("/", "_"),
            PLOT_FORMAT)
        plt.savefig('%s/%s' % (PLOT_PATH, file_name))
        plt.clf()
        already_plotted_rows+=1
        if top and already_plotted_rows >= top:
            break


if __name__ == "__main__":
    file_path = sys.argv[1]
    data = parse_file(file_path)
    calculate_stats(data)
    print_results(data)
    plot_graphs(data, 5)
