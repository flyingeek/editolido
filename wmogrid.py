# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from editolido.geoindex import GeoGridIndex, merge_importers
from editolido.geolite import LatLng
from editolido.geopoint import GeoPoint


def main():  # pragma: no cover
    wmo_grid = GeoGridIndex()
    for name, lon, lat in merge_importers():
        wmo_grid.add_point(GeoPoint(LatLng(lat, lon), name, normalizer=None))
    wmo_grid.save()


if __name__ == '__main__':
    main()
