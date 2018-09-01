#!/usr/bin/env python3

import re
import sys
from prettytable import PrettyTable


TEST_NAME_HEADER = "Test name"
TEST_TIME_HEADER = "Test time"
TEST_WORKER = "Test worker"
TEST_RESULT_HEADER = "Test result"

DATEFMT = '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}((\.|\,)\d{3,6})?'
TEST_RESULT_MATCH = (
    '^(?P<date>%s) \| (?P<host>\S+) \| \{(?P<worker>\d+)\} (?P<test_name>\S+) \[(?P<test_time>\d+\.\d+)s\] \.\.\. (?P<test_result>\S+)' %
    DATEFMT)

TEST_RESULT_RE = re.compile(TEST_RESULT_MATCH)


def parse_line(line):
    parsed_line = {}
    m = TEST_RESULT_RE.match(line)
    if m:
        parsed_line['date'] = m.group('date')
        parsed_line['host'] = m.group('host')
        parsed_line['worker'] = m.group('worker')
        parsed_line['test_name'] = m.group('test_name')
        parsed_line['test_time'] = float(m.group('test_time'))
        parsed_line['test_result'] = m.group('test_result')
        return parsed_line
    return None


def parse_file(file_path):
    tests_results = []
    with open(file_path) as f:
        for line in f:
            parsed_line = parse_line(line)
            if parsed_line:
                tests_results.append(parsed_line)
    return tests_results


def print_results(data, sortby=TEST_TIME_HEADER, desc_sort=True):
    overall_table = PrettyTable(
        [TEST_NAME_HEADER, TEST_WORKER, TEST_RESULT_HEADER, TEST_TIME_HEADER])
    overall_table.sortby = sortby
    overall_table.reversesort = desc_sort
    for test in data:
        overall_table.add_row(
            [test['test_name'],
             test['worker'],
             test['test_result'],
             test['test_time']])

    print(overall_table)


if __name__ == "__main__":
    file_path = sys.argv[1]
    data = parse_file(file_path)
    print_results(data)
