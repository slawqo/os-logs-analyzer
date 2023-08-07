#!/usr/bin/env python3

import re
import uuid
import sys
from prettytable import PrettyTable

REQUESTS_HEADER = "Request"
REQ_COUNT_HEADER = "Counter"

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


def parse_line(line):
    parsed_line = {}
    m = SYSTEMDRE.match(line)
    if m:
        parsed_line['status'] = m.group('status') or "NONE"
        parsed_line['line'] = m.group('line')
        parsed_line['method'] = m.group('method')
        parsed_line['uri'] = m.group('uri')
        parsed_line['resp_status'] = m.group('resp_status')
        return parsed_line
    return None


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
                    logged_calls[request] = 1
                else:
                    logged_calls[request] += 1
    return logged_calls


def print_results(data, sortby=REQ_COUNT_HEADER, desc_sort=True):
    overall_table = PrettyTable([REQUESTS_HEADER, REQ_COUNT_HEADER])
    overall_table.sortby = sortby
    overall_table.reversesort = desc_sort
    overall_table._max_width = {REQUESTS_HEADER: 100, REQ_COUNT_HEADER: 10}
    all_requests_counter = 0
    for request, request_count in data.items():
        overall_table.add_row([request, request_count])
        all_requests_counter += request_count
    print(overall_table)
    print("There was %s API requests in total." % all_requests_counter)


if __name__ == "__main__":
    file_path = sys.argv[1]
    data = parse_file(file_path)
    print_results(data)
