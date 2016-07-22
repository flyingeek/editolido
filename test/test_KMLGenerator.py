# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from unittest import TestCase

from editolido.constants import PIN_ORANGE, PIN_RED
from editolido.kml import KMLGenerator

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestKMLGenerator(TestCase):
    def test_add_folder(self):
        kml = KMLGenerator()
        self.assertFalse(kml.folders)
        kml.add_folder('first')
        self.assertFalse(kml.folders['first'], [])
        kml.add_folder('second')
        self.assertEqual(kml.folders.keys(), ['first', 'second'])

    def test_add_folders(self):
        kml = KMLGenerator()
        kml.add_folders('first', 'second')
        self.assertEqual(kml.folders.keys(), ['first', 'second'])

    def test__update_kwargs(self):
        fn = KMLGenerator._update_kwargs
        args = {}
        fn('folder', args)
        self.assertEqual(args['style'], '#folder')
        args = {'style': 'test'}
        fn('folder', args)
        self.assertEqual(args['style'], 'test')
        args = {'style': 0}
        fn('folder', args)
        self.assertEqual(args['style'], '#placemark-none')
        args = {'style': 0}
        fn('folder', args)
        self.assertEqual(args['style'], '#placemark-none')

    def test_add_line(self):
        kml = KMLGenerator(line_template="{name} {color}")
        kml.add_folder('aFolder')
        from editolido.route import Route
        from editolido.geopoint import GeoPoint
        route = Route([GeoPoint((0, 0)), GeoPoint((0, 90))], name="route")
        kml.add_line('aFolder', route, color="blouge")
        self.assertEqual(kml.folders['aFolder'][0], 'route blouge')

    def test_add_points(self):
        kml = KMLGenerator(point_template="{name}{color}")
        kml.add_folder('aFolder')
        from editolido.route import Route
        from editolido.geopoint import GeoPoint
        route = Route([GeoPoint((0, 0)), GeoPoint((0, 90))], name="route")
        kml.add_points('aFolder', route, color="blouge")
        self.assertEqual(''.join(kml.folders['aFolder']), 'blouge' * 2)

    def test_add_point_no_pin_set_in_folder(self):
        kml = KMLGenerator(point_template="{name} {color}")
        kml.add_folder('aFolder')
        from editolido.geopoint import GeoPoint
        kml.add_point('aFolder', GeoPoint((0, 0), name="P1"))
        self.assertFalse(kml.folders['aFolder'])
        kml.add_point('aFolder', GeoPoint((0, 0), name="P1"),
                      color="blouge", style='#style')
        self.assertEqual(kml.folders['aFolder'][0], 'P1 blouge')

    def test_add_point_pin_set_in_folder(self):
        kml = KMLGenerator(point_template="{name} {color} {style}")
        kml.add_folder('aFolder', pin=PIN_ORANGE)
        from editolido.geopoint import GeoPoint
        kml.add_point('aFolder', GeoPoint((0, 0), name="P1"), color="blouge")
        self.assertEqual(kml.folders['aFolder'][0],
                         'P1 blouge #placemark-orange')
        kml.add_point('aFolder', GeoPoint((0, 0), name="P1"),
                      color="blouge", style=PIN_RED)
        self.assertEqual(kml.folders['aFolder'][1],
                         'P1 blouge #placemark-red')

    def test_render(self):
        kml = KMLGenerator(folder_template="{name} {open} {content}",
                           point_template="{name} {color} {style}",
                           template="{folders} {name} {extra}")
        kml.add_folder('aFolder')
        from editolido.geopoint import GeoPoint
        kml.add_point('aFolder', GeoPoint((0, 0), name="P1"),
                      color="blouge", style="#mystyle")
        self.assertEqual(kml.render(extra="what else ?",
                                    name='no name',
                                    aFolder_color="white"),
                         'aFolder 1 P1 blouge #mystyle no name what else ?')

    def test_render_folder(self):
        kml = KMLGenerator(folder_template="{name} {open} {content}",
                           point_template="{name} {color} {style}")
        kml.add_folder('aFolder')
        from editolido.geopoint import GeoPoint
        kml.add_point('aFolder', GeoPoint((0, 0), name="P1"),
                      color="blouge", style='#mystyle')
        self.assertEqual(kml.render_folder('aFolder'),
                         'aFolder 1 P1 blouge #mystyle')

    def test_render_folders(self):
        kml = KMLGenerator(folder_template="{name} {open} {content}",
                           point_template="{name} {color} {style}")
        kml.add_folders('aFolder', ('another', PIN_RED))
        from editolido.geopoint import GeoPoint
        kml.add_point('aFolder', GeoPoint((0, 0), name="P1"),
                      color="blouge", style='#mystyle')
        kml.add_point('another', GeoPoint((0, 0), name="P2"), color="red")
        self.assertEqual(kml.render_folders(),
                         'aFolder 1 P1 blouge #mystyle\n'
                         'another 1 P2 red #placemark-red')

    def test_as_kml_line(self):
        kml = KMLGenerator(
            line_template='{name}/{style}/{description}/{coordinates}',)
        from editolido.geopoint import GeoPoint
        from editolido.route import Route
        start = GeoPoint((0, 0))
        end = GeoPoint((0, 90))
        route = Route(
            [start, end], name="route_name", description="route_description")
        kml.add_folder('aFolder')
        kml.add_line('aFolder', route, style='route_style')
        self.assertEqual(
            ''.join(kml.folders['aFolder']),
            'route_name/route_style/route_description/'
            '0.000000,0.000000 90.000000,0.000000'
        )

    def test_as_kml_points(self):
        kml = KMLGenerator(
            point_template='{name}/{style}/{description}/{coordinates}',)
        from editolido.geopoint import GeoPoint
        from editolido.route import Route
        start = GeoPoint((0, 0), name="P1")
        end = GeoPoint((0, 90), name="P2", description="D2")
        route = Route(
            [start, end], name="route_name", description="route_description")
        kml.add_folder('aFolder')
        kml.add_points('aFolder', route, style='point_style')
        self.assertEqual(
            '\n'.join(kml.folders['aFolder']),
            'P1/point_style//0.000000,0.000000\n'
            'P2/point_style/D2/90.000000,0.000000'
        )

    def test_kml_ofp374_22Jul2016(self):
        """
        Ensure all waypoints and in the good order
        """
        from editolido.ofp import OFP
        with open(DATADIR + '/AF374_LFPG-CYVR_22Jul2016_08:45z_OFP_8_0_1.txt',
                  'r') as f:
            ofp = OFP(f.read())

        kml = KMLGenerator(point_template="{coordinates}")
        kml.add_folder('rmain')
        kml.add_points('rmain', ofp.route)
        coords = ["{1:.6f},{0:.6f}".format(p.latitude, p.longitude)
                  for p in ofp.route]
        self.assertEqual(coords, kml.folders['rmain'])
