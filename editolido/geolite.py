# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
import operator
from collections import namedtuple
from decimal import Decimal
from functools import partial

"""
latitude is a Decimal and unit is degrees
longitude is a Decimal and unit is degrees

rlat is the float latitude in radians (lambda is a reserved name in python)
phi is the float longitude in radians

Store a tuple of (latitude, longitude) using the namedtuple LatLng
Store a tuple of (rlat, phi) using the namedtuple LatPhi

"""
R = 6371000.0  # earth mean radius in meters
NM = 1852.0  # nm in meters

# Base points
LatLng = namedtuple('LatLng', ['latitude', 'longitude'])
LatPhi = namedtuple('LatPhi', ['rlat', 'phi'])

# Converters
rad_to_nm = partial(operator.mul, R / NM)
rad_to_km = partial(operator.mul, R / 1000.0)
nm_to_rad = partial(operator.mul, NM / R)
km_to_rad = partial(operator.mul, 1000.0 / R)
km_to_nm = partial(operator.mul, 1000.0 / NM)


def latphi2latlng(latphi):
    """
    Converts a LatPhi to a LatLng
    :param latphi: LatPhi
    :return: LatLng
    """
    return LatLng(*map(Decimal, map(math.degrees, latphi)))


def dm2decimal(s):
    """convert geo coordinates in degrees, minutes in signed decimal value
    N5500.0 => Decimal('55.0')
    W02000.0 => Decimal('-20.0')
    :param s: str
    """
    letter = s[0]
    assert letter in 'NSEW'
    sign = 1 if letter in ('N', 'E') else -1
    offset = 3 if letter in ('N', 'S') else 4
    degrees = Decimal(s[1:offset])
    minutes = Decimal(s[offset:])
    return sign * (degrees + minutes / 60)


def latlng2dm(latlng):
    """
    Degrees Minutes representation of LatLng
    :param latlng: LatLng
    :return: unicode
    >>> latlng2dm(LatLng(45.5, 30.5))
    u'N4530.0E03030.0'
    """
    def dm(v, pattern):
        f, degrees = math.modf(abs(v))
        cents, minutes = math.modf(f * 60)
        cents = round(cents * 10)
        if cents >= 10:
            cents = 0
            minutes += 1
        return pattern.format(
            int(degrees),
            int(minutes),
            int(cents)
        )

    return '{0}{1}{2}{3}'.format(
        'N' if latlng.latitude >= 0 else 'S',
        dm(latlng.latitude, '{0:0>2d}{1:0>2d}.{2}'),
        'E' if latlng.longitude > 0 else 'W',
        dm(latlng.longitude, '{0:0>3d}{1:0>2d}.{2}'),
    )
