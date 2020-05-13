# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from editolido.geoindex import GeoGridIndex, merge_importers


def main():  # pragma: no cover
    wmo_grid = GeoGridIndex()
    counter = 0
    for name, lon, lat in merge_importers():
        wmo_grid.add_point([name, lat, lon])
        counter += 1
    wmo_grid.save()
    print("saved %d stations" % counter)


if __name__ == '__main__':
    main()
