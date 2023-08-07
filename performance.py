#!/usr/bin/env python3

# This script can be used to get some data from the performance.json file

import json
import sys
from prettytable import PrettyTable

DB_HEADER = "db"
OP_HEADER = "operation"
COUNT_HEADER = "count"

HEADERS = ["SELECT", "INSERT", "UPDATE", "DELETE", "ROLLBACK", "RELEASE", "SAVEPOINT", "ALL"]

def consolidate_db_data(data):
    consolidated_data = {
        'all_dbs': {
            'SELECT': 0,
            'INSERT': 0,
            'UPDATE': 0,
            'DELETE': 0,
            'ROLLBACK': 0,
            'RELEASE': 0,
            'SAVEPOINT': 0,
            'ALL': 0
        }
    }
    for row in data:
        if row['db'] not in consolidated_data:
            consolidated_data[row['db']] = {
                row['op']: row['count'],
                'ALL': row['count']
            }
        else:
            consolidated_data[row['db']][row['op']] = row['count']
            consolidated_data[row['db']]['ALL'] += row['count']
        consolidated_data['all_dbs'][row['op']] += row['count']
        consolidated_data['all_dbs']['ALL'] += row['count']
    return consolidated_data


def print_db_data(data):
    #table = PrettyTable([DB_HEADER, OP_HEADER, COUNT_HEADER])
    #table.sortby = OP_HEADER
    #import pdb; pdb.set_trace()
    table = PrettyTable([DB_HEADER] + HEADERS)
    for db, counters in data.items():
        if db == 'all_dbs':
            continue
        db_counters = []
        for header in HEADERS:
            db_counters.append(counters.get(header, "-"))
        table.add_row([db] + db_counters)
    all_dbs_counters = []
    for header in HEADERS:
        all_dbs_counters.append(data['all_dbs'].get(header, "-"))
    table.add_row(["All databases"] + all_dbs_counters)
    print(table)



if __name__ == '__main__':
    file_path = sys.argv[1]
    with open(file_path) as f:
        perf_json = json.load(f)
    db_data = perf_json.get("db")
    if not db_data:
        print("No DB data found in the %s file" % file_path)
        sys.exit(1)
    print_db_data(consolidate_db_data(db_data))
