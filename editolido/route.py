# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import itertools
from editolido.geolite import rad_to_nm, nm_to_rad


class Route(object):
    """
    A collection of GeoPoints
    """
    def __init__(self, points=None, name=None, description=None):
        self._route = points if points else []
        self.name = name
        self.description = description

    @property
    def segments(self):
        """
        Iterates the route in pairs of GeoPoints
        [p1, p2, p3] -> [(p1, p2), (p2, p3)]
        :return: generator of GeoPoints
        """
        a, b = itertools.tee(self.route)
        next(b, None)
        return itertools.izip(a, b)

    @property
    def route(self):
        """
        Access to an "evaluated" version of the route (a list of GeoPoints)
        :return: list of GeoPoint
        """
        if not isinstance(self._route, (list, tuple)):
            self._route = list(self._route)
        return self._route

    def distance(self, converter=rad_to_nm):
        """
        Sum the spherical distance of the route's segments
        :param converter: function definig the unit to use (default NM)
        :return: float
        """
        d = sum(itertools.imap(
            lambda s: s[0].distance_to(s[1]) if s else 0,
            self.segments))
        if converter:
            return converter(d)
        return d

    def __iter__(self):
        """
        Iterates over points of the route
        Note: the route will be evaluated
        """
        for p in self.route:
            yield p

    def __eq__(self, other):
        """
        Check if other route contains the same points (almost).
        """
        for p1, p2 in itertools.izip_longest(self, other):
            if p1 is None or p2 is None or p1 != p2:
                break
        else:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, item):
        return self.route[item]

    def split(self, max_length, converter=nm_to_rad, preserve=False):
        """
        Split a route in smaller segments.
        The new Route might be different from the original one as original
        start and end of inner segments are not preserved by default.
        :param max_length: max segment lenght in radians (or converter unit)
        :param converter: a unit converter function, convert unit into radians
        :param preserve: always emit the boundary of the original segments
        :return: Route
        """

        # noinspection PyShadowingNames
        def splitted_route_generator(max_radians, preserve):
            remaining = 0
            geopoint2 = None
            first = True
            for geopoint1, geopoint2 in self.segments:
                if first:
                    first = False
                    yield geopoint1  # first point
                segment_length = geopoint1.distance_to(geopoint2)
                d = remaining
                while d <= segment_length - max_radians:
                    d += max_radians
                    f = d / segment_length
                    yield geopoint1.at_fraction(
                        geopoint2, f, distance=segment_length)
                remaining = round(d - segment_length, 10)
                if preserve and remaining:
                    yield geopoint2
                    remaining = 0
            if remaining:
                yield geopoint2  # last if not yet emitted

        size = converter(max_length) if converter else max_length
        return self.__class__(splitted_route_generator(size, preserve))
