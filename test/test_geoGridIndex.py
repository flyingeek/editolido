# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import pytest
import six
from unittest import TestCase
from editolido.geolite import LatLng, nm_to_rad, rad_to_nm, rad_to_km
from editolido.geopoint import GeoPoint
from editolido.geoindex import GeoGridIndex, wmo_importer

# noinspection PyUnresolvedReferences
online = pytest.mark.skipif(
    pytest.config.getoption("--offline"),
    reason="remove --offline option to run"
)


class TestGeoGridIndex(TestCase):
    def test_get_point_hash(self):
        grid = GeoGridIndex(4)
        self.assertEqual(grid.get_point_hash(LatLng(45, 10)), 'u0p0')
        self.assertEqual(grid.get_point_hash(GeoPoint((45, 10))), 'u0p0')
        grid = GeoGridIndex()
        self.assertEqual(grid.get_point_hash(LatLng(45, 10)), 'u0p')

    def test_add_point(self):
        grid = GeoGridIndex(4)
        p = ["", 45, 10]
        grid.add_point(p)
        self.assertEqual(grid.data['u0p0'], [p])

    def test_get_nearest_points_dirty(self):
        c = GeoPoint((45, 10.5))
        p = GeoPoint((45, 10))  # à 21,23NM
        grid = GeoGridIndex(4)
        print(grid.precision, rad_to_km(grid.grid_size))
        grid.add_point([p.name, float(p.latitude), float(p.longitude)])
        with self.assertRaises(ValueError):
            grid.get_nearest_points_dirty(c, 30, converter=nm_to_rad)
        grid = GeoGridIndex()
        grid.add_point([p.name, float(p.latitude), float(p.longitude)])
        nearby = grid.get_nearest_points_dirty(c, 20, converter=nm_to_rad)
        self.assertEqual(list(nearby), [p])

    def test_get_nearest_points(self):
        c = GeoPoint((45, 10.5))
        p = GeoPoint((45, 10))  # à 21,23NM
        grid = GeoGridIndex()
        grid.add_point([p.name, float(p.latitude), float(p.longitude)])
        nearby = grid.get_nearest_points(c, 20, converter=nm_to_rad)
        if six.PY2:
            self.assertEqual(list(nearby), [])
        else:
            pass  # TODO
        nearby = grid.get_nearest_points(c, 23, converter=nm_to_rad)
        if six.PY2:
            self.assertEqual(list(nearby),
                             [(p, c.distance_to(p, converter=rad_to_nm))])
        else:
            pass  # TODO

    def test_load(self):
        grid = GeoGridIndex()
        grid.load()
        self.assertGreater(len(grid.data), 4000)

    def test_dumps(self):
        p = GeoPoint((45, 10), name='P1', description='D2')
        grid = GeoGridIndex()
        self.assertEqual(grid.dumps(), '{}')
        grid.add_point([p.name, float(p.latitude), float(p.longitude)])
        grid.data['__test__'] = 'test'  # test default encoder is called
        jsondata = grid.dumps()
        self.assertDictEqual(
            grid.data,
            json.loads(jsondata, encoding='utf-8'))

    @online
    def test_wmo_importer(self):
        wmo_grid = GeoGridIndex()
        for name, _, lon, lat in wmo_importer():
            wmo_grid.add_point(
                GeoPoint(LatLng(lat, lon), name, normalizer=None))
        self.assertTrue(len(wmo_grid.data) > 5000)


class TestLoadedGrid(TestCase):
    def test_get_nearest_points_dirty(self):
        center_point = GeoPoint([49, 2])
        wmo_grid = GeoGridIndex()
        wmo_grid.load()
        # with self.assertRaises(ValueError):
        #     wmo_grid.get_nearest_points_dirty(center_point, 100)
        nearest = list(wmo_grid.get_nearest_points_dirty(center_point, 75))
        self.assertEqual(len(nearest), 42)

    def test_get_nearest_points(self):
        center_point = GeoPoint([49, 2])
        wmo_grid = GeoGridIndex()
        wmo_grid.load()
        nearest = list(wmo_grid.get_nearest_points(center_point, 27))
        self.assertEqual(len(nearest), 1)
        self.assertEqual(nearest[0][0].name, "07145")
