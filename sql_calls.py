#!/usr/bin/env python3

import collections
import uuid
import re
import sys
import prettytable

MAX_ROWS_TO_PRINT = 30
SYSTEMD_MATCH = r'^(?P<date>\w+\s+\d+\s+\d{2}:\d{2}:\d{2}((\.|\,)\d{3,6})?)(?P<line> (?P<host>\S+) \S+\[\d+\]\: INFO sqlalchemy.engine.Engine \[.*\] (?P<sql_query>(INSERT|UPDATE|DELETE|ROLLBACK).*))$'
SYSTEMDRE = re.compile(SYSTEMD_MATCH)


def get_sql_query_from_line(line):
    parsed_line = {}
    m = SYSTEMDRE.match(line)
    return m.group('sql_query') if m else None


def parse_file(file_path):
    sql_queries = collections.defaultdict(int)
    with open(file_path) as f:
        for line in f:
            sql_query = get_sql_query_from_line(line)
            if sql_query:
                sql_queries[sql_query] += 1
    return sql_queries


def print_results(data):
    overall_table = prettytable.PrettyTable(["SQL Query", "Counter"])
    overall_table.sortby = "Counter"
    overall_table.reversesort = True
    overall_table._max_width = {"SQL Query": 250, "Counter": 10}
    overall_table.hrules = prettytable.ALL
    overall_table.vrules = prettytable.ALL
    overall_table.end = MAX_ROWS_TO_PRINT
    for sql_query, counter in data.items():
        overall_table.add_row([sql_query, counter])
    print(overall_table)


if __name__ == "__main__":
    file_path = sys.argv[1]
    data = parse_file(file_path)
    print_results(data)
