# -*- coding: utf-8 -*-
from __future__ import unicode_literals


try:
    # noinspection PyCompatibility
    from urllib.request import urlopen
    PY2 = False
except ImportError:
    # noinspection PyCompatibility
    from urllib2 import urlopen
    PY2 = True
import csv
import json
import os

from itertools import chain
import editolido.geohash as geohash
from editolido.geolite import km_to_rad
from editolido.geopoint import GeoPointEncoder, as_geopoint


def wmo_importer(url='https://raw.githubusercontent.com/flyingeek/editolido/gh-pages/ext-sources/nsd_bbsss.txt'):
    # http://tgftp.nws.noaa.gov/data/nsd_bbsss.txt
    if PY2:
        delimiter = b';'
        data = urlopen(url)
    else:
        delimiter = ';'
        import codecs
        data = codecs.iterdecode(urlopen(url), 'utf-8')
    reader = csv.reader(data, delimiter=delimiter, quoting=csv.QUOTE_NONE)

    def geo_normalize(value):
        # recognize NSEW or undefined (which is interpreted as North)
        orientation = value[-1]
        sign = -1 if orientation in 'SW' else 1
        coords = value if orientation not in 'NEWS' else value[:-1]
        coords += '-0-0'  # ensure missing seconds or minutes are 0
        degrees, minutes, seconds = map(float, coords.split('-', 3)[:3])
        return sign * (degrees + (minutes / 60) + (seconds / 3600))

    not_airport = '----'

    for row in reader:
        name = row[0] + row[1] if row[2] == not_airport else row[2]
        yield name, row[0] + row[1], geo_normalize(row[8]), geo_normalize(row[7])


def vola_importer(url="https://raw.githubusercontent.com/flyingeek/editolido/gh-pages/ext-sources/vola_legacy_report.txt"):
    # https://oscar.wmo.int/oscar/vola/vola_legacy_report.txt
    if PY2:
        delimiter = b'\t'
        data = urlopen(url)
    else:
        delimiter = '\t'
        import codecs
        data = codecs.iterdecode(urlopen(url), 'utf-8')
    reader = csv.reader(data, delimiter=delimiter, quoting=csv.QUOTE_NONE)

    def geo_normalize(value):
        # recognize NSEW or undefined (which is interpreted as North)
        orientation = value[-1]
        sign = -1 if orientation in 'SW' else 1
        coords = value if orientation not in 'NEWS' else value[:-1]
        coords += ' 0 0'  # ensure missing seconds or minutes are 0
        degrees, minutes, seconds = map(float, coords.split(' ', 3)[:3])
        return sign * (degrees + (minutes / 60) + (seconds / 3600))

    headers = next(reader)
    for row in reader:
        name = row[5]
        if not name:
            continue
        yield name, geo_normalize(row[9]), geo_normalize(row[8]), row[28].split(', ')


def merge_importers():
    vola = {}
    for wid, lon, lat, remarks in vola_importer():
        vola[wid] = (lon, lat, remarks)
    wmo = []
    for name, wid, lon, lat in wmo_importer():
        if wid not in vola:
            continue
        vola_lon, vola_lat, remarks = vola[wid]
        if name in ['CYMT']:
            continue
        if 'GOS' not in remarks:
            continue
        if round(vola_lon, 1) != round(lon, 1) or round(vola_lat, 1) != round(lat, 1):
            continue
        wmo.append(wid)
        yield name, lon, lat

    if PY2:
        items = vola.iteritems
    else:
        items = vola.items

    for key, value in items():
        if key not in wmo:
            if 'GOS' in value[2]:
                yield key, value[0], value[1]



# dependence between hashtag's precision and distance accurate calculating
# in fact it's sizes of grids in km
GEO_HASH_GRID_SIZE = {
    1: 5000.0,
    2: 1260.0,
    3: 156.0,
    4: 40.0,
    5: 4.8,
    6: 1.22,
    7: 0.152,
    8: 0.038
}


class GeoGridIndex(object):
    """
    Class for store index based on geohash of points for quick-and-dry
    neighbors search
    GeoGridIndex Credits:
    https://github.com/gusdan/geoindex/blob/master/geoindex/geo_grid_index.py
    """

    def __init__(self, precision=3):
        """
        :param precision:
        """
        self.precision = precision
        self.data = {}

    def get_point_hash(self, point):
        """
        return geohash for given point with self.precision
        :param point: GeoPoint instance
        :return: string
        """
        return geohash.encode(float(point.latitude),
                              float(point.longitude),
                              self.precision)

    def add_point(self, point):
        """
        add point to index, point must be a GeoPoint instance
        :param point:
        :return:
        """
        point_hash = self.get_point_hash(point)
        points = self.data.setdefault(point_hash, [])
        points.append(point)

    def get_nearest_points_dirty(self, center_point, radius,
                                 converter=km_to_rad):
        """
        return approx list of point from circle with given center and radius
        it uses geohash and return with some error (see GEO_HASH_ERRORS)
        :param center_point: center of search circle
        :param radius: radius of search circle
        :param converter: function to convert the radius unit in radians
        :return: list of GeoPoints from given area
        """
        grid_size = km_to_rad(GEO_HASH_GRID_SIZE[self.precision])
        if converter:
            radius = converter(radius)
        if radius > grid_size / 2:
            # radius is too big for current grid, we cannot use 9 neighbors
            # to cover all possible points
            suggested_precision = 0
            for precision, max_size in GEO_HASH_GRID_SIZE.items():
                if radius > km_to_rad(max_size) / 2:
                    suggested_precision = precision - 1
                    break
            raise ValueError(
                'Too large radius, please rebuild GeoHashGrid with '
                'precision={0}'.format(suggested_precision)
            )
        me_and_neighbors = geohash.expand(self.get_point_hash(center_point))
        for key in me_and_neighbors:
            self.data[key] = list(map(as_geopoint, self.data.get(key, [])))
        return chain(*(self.data.get(key, []) for key in me_and_neighbors))

    def get_nearest_points(self, center_point, radius, converter=km_to_rad):
        """
        return list of geo points from circle with given center and radius
        :param center_point: GeoPoint with center of search circle
        :param radius: radius of search circle
        :param converter: function to convert the radius unit in radians
        :return: generator with tuple with GeoPoints and distance
        """
        if converter:
            radius = converter(radius)
        for point in self.get_nearest_points_dirty(center_point, radius,
                                                   converter=None):
            distance = point.distance_to(center_point, converter=None)
            if distance <= radius:
                distance = (distance if converter is None
                            else distance / converter(1.0))
                yield point, distance

    @staticmethod
    def json_filename(basename='.wmogrid.json'):
        _dir = os.path.join(os.path.dirname(__file__), 'data')
        return os.path.join(_dir, basename)

    def dumps(self):
        if PY2:
            return json.dumps(self.data, encoding='utf-8', cls=GeoPointEncoder)
        return json.dumps(self.data, cls=GeoPointEncoder)

    def save(self):  # pragma: no cover
        with open(self.json_filename(), 'w') as f:
            f.write(self.dumps())

    def load(self):
        with open(self.json_filename(), 'r') as f:
            self.data = json.load(f, encoding='utf-8')
