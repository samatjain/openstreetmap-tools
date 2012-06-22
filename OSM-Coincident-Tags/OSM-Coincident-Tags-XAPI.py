#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import json
import pprint
import operator
import sys

from collections import OrderedDict

import jinja2

from lxml import etree


def processOSMFile(t):
    counts = {}
    for e in t.iterfind('.//tag'):
        k = e.get('k')
        v = e.get('v')
        c = counts.get((k, v), 0)
        counts[(k, v)] = c+1

    # Prune blacklisted keys and everything that only occurs once
    blacklisted_keys = {'addr:city',
                        'addr:country',
                        'addr:housenumber',
                        'addr:postcode',
                        'addr:state',
                        'addr:street',
                        'created_by',
                        'phone',
                        'source' }
    pruned_counts = {}
    for (k, v) in counts.iteritems():
        # Ignore low counts
        if v < 2:
            continue

        # Ignore blacklisted keys
        if k[0] in blacklisted_keys:
            continue

        pruned_counts[k] = v

    return pruned_counts


def group_by_key(d):
    grouped = OrderedDict() 
    for (k, v) in d.iteritems():
        l = grouped.get(k[0], {})
        l[k[1]] = v
        grouped[k[0]] = l
    return grouped


def output_html(title, grouped):
    jt = jinja2.Template(file('template.html').read())

    # Compact JSON
    jsonData = json.dumps(grouped, separators=(',', ':'))

    return jt.render(tagName=title, json=jsonData, tags=grouped)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Find most-used tags in an OpenStreetMap XAPI query')
    arg_parser.add_argument('--mode', '-m', choices=['json', 'html'],
                            default='json', help="Output format")

    group = arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filename', '-i', help='Saved XAPI query')
    group.add_argument('--query', '-q', help='XAPI query predicates, e.g. "[name=Starbucks]"')

    args = arg_parser.parse_args()

    if len(sys.argv) < 2:
        print('Please run with filename as 1st option', file=sys.stderr)
        sys.exit(1)

    if args.query:
        url = 'http://open.mapquestapi.com/xapi/api/0.6/*%s' % args.query
        t = etree.parse(url)
        html_title = args.query
    elif args.filename:
        t = etree.parse(args.filename)
        html_title = args.filename

    r = processOSMFile(t)
    # Sort by value (number of times a tag has appeared
    r = OrderedDict(sorted(r.iteritems(), key=operator.itemgetter(1), reverse=True))
    grouped = group_by_key(r)


    if args.mode == 'json':
        print(json.dumps(grouped, indent=4))
    elif args.mode == 'html':
        print(output_html(html_title, grouped).encode('utf8'))
