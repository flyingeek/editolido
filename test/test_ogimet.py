# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from unittest import TestCase
import os

from editolido.ofp import OFP
from editolido.ogimet import ogimet_route

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestOgimet(TestCase):
    def test_ogimet_existing_airports(self):
        with open(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z.txt', 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], 'KJFK')
        self.assertEqual(points[-1], 'LFPG')
        self.assertLess(len(points), 23)
        self.assertEqual(
            points,
            [u'KJFK', u'74483', u'KCON', u'KNHZ', u'KEPO', u'CYSJ', u'CYQM',
             u'CYSU', u'CWGR', u'CYJT', u'CWDO', u'03964', u'03965', u'03957',
             u'EGOP', u'03614', u'EGDL', u'03759', u'03880', u'07040', u'LFOP',
             u'LFPG']
        )
    def test_ogimet_to_FAOR(self):  # JNB
        with open(DATADIR + '/AF990_LFPG-FAOR_05Jun2016_21:25z_OFP_12_0_1.txt', 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], 'LFPG')
        self.assertEqual(points[-1], 'FAJS')  # FAOR => FAJS
        self.assertLess(len(points), 23)


    def test_ogimet_from_FAOR(self):  # JNB
        with open(DATADIR + '/AF995_FAOR-LFPG_09Jun2016_16:50z_OFP_9_0_1.txt', 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], 'FAJS')  # FAOR => FAJS
        self.assertEqual(points[-1], 'LFPG')
        self.assertLess(len(points), 23)

    def test_ogimet_to_VOBL(self):  # BLR
        with open(DATADIR + '/AF192_LFPG-VOBL_28Dec2016_10:25z_OFP_12_0_1.txt', 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], 'LFPG')
        self.assertEqual(points[-1], '43296')
        self.assertLess(len(points), 23)

    def test_ogimet_from_VOBL(self):  # BLR
        with open(DATADIR + '/AF191_VOBL-LFPG_30Dec2016_21:50z_OFP_20_0_1.txt', 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], '43296')
        self.assertEqual(points[-1], 'LFPG')
        self.assertLess(len(points), 23)
