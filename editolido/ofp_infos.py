# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import re
import sys
from datetime import datetime, timedelta, tzinfo, time

MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
          'Nov', 'Dec')

ZERO = timedelta(0)


# A UTC class.
class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        if sys.version_info[0] == 2:
            return b"UTC"
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()


def ofp_infos(text, raw_fpl_text, raw_flight_summary_text):
    """
    Dictionary of common OFP data:
    - flight (AF009)
    - departure (KJFK)
    - destination (LFPG)
    - datetime (a python datetime for scheduled departure block time)
    - date (OFP text date 25Apr2016)
    - datetime2 (a python datetime for scheduled arrival block time)
    - ofp (OFP number 9/0/1)
    - alternates a list of alternate
    - ralts a list of route alternates (ETOPS)
    - taxitime (int departure taxi time in mn)
    :return: Dict[str, Any]
    """
    infos = {}
    pattern = r'(?P<flight>AF.+)' \
              r'(?P<departure>\S{4})/' \
              r'(?P<destination>\S{4})\s+' \
              r'(?P<datetime>\S+/\S{4})z.*OFP\s+' \
              r'(?P<ofp>\S+)Main'
    m = re.search(pattern, text)
    if not m:
        pattern = r'(?P<flight>AF\s+\S+\s+)' \
                  r'(?P<departure>\S{4})/' \
                  r'(?P<destination>\S{4})\s+' \
                  r'(?P<datetime>\S+/\S{4})z.*OFP\s+' \
                  r'(?P<ofp>\d+\S{0,8})'
        m = re.search(pattern, text, re.DOTALL)
    if m:
        infos.update(m.groupdict())
        infos['flight'] = infos['flight'].replace(' ', '')
        infos['ofp'] = infos['ofp'].replace('\xa9', '')
        s = infos['datetime']
        infos['date'] = s[:-5]
        date_text = "{0}{1:0>2}{2}".format(
            s[0:2],
            MONTHS.index(s[2:5]) + 1,
            s[5:]
        )
        date_object = datetime.strptime(date_text, '%d%m%Y/%H%M'
                                        ).replace(tzinfo=utc)
        infos['datetime'] = date_object
        pattern = r'-%s' % infos['destination'] + r'(\d{4})\s'
        m = re.search(pattern, raw_fpl_text)
        if m:
            infos['duration'] = time(
                int(m.group(1)[:2]), int(m.group(1)[2:]), tzinfo=utc)
        else:
            print('duration not found in opt, please report !')
            print('duration set arbitrary to 1 hour')
            infos['duration'] = time(1, 0, tzinfo=utc)
        # try with 2 alternates first
        pattern = r'-%s' % infos['destination'] + r'.+\s(\S{4})\s(\S{4})\s?[\n\-]'
        m = re.search(pattern, raw_fpl_text)
        infos['alternates'] = []
        if m:
            infos['alternates'] = list(m.groups())
        else:
            # backup with one alternate only
            pattern = r'-%s' % infos['destination'] + r'.+\s(\S{4})\s?[\n\-]'
            m = re.search(pattern, raw_fpl_text)
            if m:
                infos['alternates'] = list(m.groups())
        pattern = r'RALT/((?:\S{4}[ \n])+)'
        m = re.search(pattern, raw_fpl_text)
        infos['ralts'] = []
        if m:
            infos['ralts'] = m.group(1).split()

        pattern = r'\s(\d{2})(\d{2})\s+TAXI IN'
        m = re.search(pattern, raw_flight_summary_text)
        infos['taxitime'] = 0
        if m:
            infos['taxitime'] = (
                    int(m.group(1)) * 60 + int(m.group(2)))

    return infos
