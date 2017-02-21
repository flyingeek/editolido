# -*- coding: utf-8 -*-
from __future__ import unicode_literals


PIN_NONE = 0
PIN_BLUE = 1
PIN_YELLOW = 2
PIN_BROWN = 3
PIN_ORANGE = 4
PIN_PINK = 5
PIN_RED = 6
PIN_GREEN = 7
PIN_PURPLE = 8
PINS = (
    '#placemark-none', '#placemark-blue', '#placemark-yellow',
    '#placemark-brown', '#placemark-orange', '#placemark-pink',
    '#placemark-red', '#placemark-green', '#placemark-purple')
GOOGLE_ICONS = list(map(
    lambda c: 'http://chart.googleapis.com/'
              'chart?chst=d_map_pin_letter&chld=|{0}'.format(c),
    [
        'FFFFFF', '6699FF', 'FFFF00',
        'CC9966', 'FF9922', 'DD5599',
        'FF0000', '22DD44', 'BB11EE',
        ]))

NAT_POSITION_ENTRY = 0
NAT_POSITION_EXIT = 1
OGIMET_IMAGE_URL_MODE = '###RETURN_OGIMET_IMAGE_URL###'

