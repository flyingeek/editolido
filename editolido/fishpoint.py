# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import csv
import fnmatch
import os
import sys

if sys.version_info[0] >= 3:
    PY2 = False
    SORTLOWER = str.lower
else:
    PY2 = True
    SORTLOWER = unicode.lower

DOCUMENTS = os.path.join(os.path.expanduser('~'), 'Documents')
GEO_WPT_REGEX = r'(\d{2,4}[NS]\d{3,5}[EW]|[NESW]\d{4}|\d[NESW]\d{3}[^EW])'


def sort_fishfiles(files):
    if files:
        return sorted(files, key=SORTLOWER, reverse=True)
    return []


def find_fishfile(path=DOCUMENTS):
    files = []
    if os.path.exists(path):
        for f in os.listdir(path):
            if fnmatch.fnmatch(f.lower(), 'wpts_oca*.csv'):
                files.append(os.path.join(path, f))
    if files:
        return sort_fishfiles(files)[0]
    return None


def get_missing_fishpoints(missings, fishfile=None):
    fish_points = {}

    def add_fish_point(data):
        k = data[0].strip()
        if k in missings:
            fish_points[k] = (data[1].replace(',', '.'), data[2].replace(',', '.'))

    if missings and fishfile and os.path.isfile(fishfile):
        if PY2:
            with open(fishfile, 'rb') as csvfile:
                fishreader = csv.reader(csvfile, delimiter=b';',
                                        quotechar=b'"')
                fishreader.next()
                for row in fishreader:
                    add_fish_point(row)
        else:
            with open(fishfile, 'rU') as csvfile:
                fishreader = csv.reader(csvfile, delimiter=';', quotechar='"')
                next(fishreader)
                for row in fishreader:
                    add_fish_point(row)

    return fish_points


