# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from unittest import TestCase
import os
import pytest
import io

from editolido.ofp import OFP
from editolido.ogimet import ogimet_route, ogimet_url_and_route_and_tref, \
    get_gramet_image_url


DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

online = pytest.mark.skipif(
    pytest.config.getoption("--offline"),
    reason="remove --offline option to run"
)


class TestOgimet(TestCase):

    def test_ogimet_existing_airports(self):
        filepath = DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt'
        with open(filepath, 'r') as f:
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
        filepath = DATADIR + '/AF990_LFPG-FAOR_05Jun2016_21:25z_OFP_12_0_1.txt'
        with open(filepath, 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], 'LFPG')
        self.assertEqual(points[-1], 'FAJS')  # FAOR => FAJS
        self.assertLess(len(points), 23)

    def test_ogimet_from_FAOR(self):  # JNB
        filepath = DATADIR + '/AF995_FAOR-LFPG_09Jun2016_16:50z_OFP_9_0_1.txt'
        with open(filepath, 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], 'FAJS')  # FAOR => FAJS
        self.assertEqual(points[-1], 'LFPG')
        self.assertLess(len(points), 23)

    def test_ogimet_to_VOBL(self):  # BLR
        filepath = DATADIR + '/AF192_LFPG-VOBL_28Dec2016_10:25z_OFP_12_0_1.txt'
        with open(filepath, 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], 'LFPG')
        self.assertEqual(points[-1], '43296')
        self.assertLess(len(points), 23)

    def test_ogimet_from_VOBL(self):  # BLR
        filepath = DATADIR + '/AF191_VOBL-LFPG_30Dec2016_21:50z_OFP_20_0_1.txt'
        with open(filepath, 'r') as f:
            ofp = OFP(f.read())
        route = ogimet_route(ofp.route)
        points = [p.name for p in route if p.name]
        self.assertEqual(points[0], '43296')
        self.assertEqual(points[-1], 'LFPG')
        self.assertLess(len(points), 23)

    def test_ogimet_url(self):
        try:
            # noinspection PyUnresolvedReferences
            from urlparse import urlsplit, parse_qs
        except ImportError:
            # noinspection PyUnresolvedReferences
            from urllib.parse import urlsplit, parse_qs
        filepath = DATADIR + '/AF191_VOBL-LFPG_30Dec2016_21:50z_OFP_20_0_1.txt'
        with open(filepath, 'r') as f:
            ofp = OFP(f.read())
        url, _, tref = ogimet_url_and_route_and_tref(ofp)
        self.maxDiff = None
        self.assertEqual(
            url,
            'http://www.ogimet.com/display_gramet.php'
            '?lang=en&hini=0&tref={0}'
            '&hfin=10&fl=310&hl=3000&aero=yes'
            '&wmo=43296_VOBI_43109_OIZJ_40851_OITZ_OITK_LTCE_17030_15499_15324_'
            '12851_11659_10671_LFPG'
            '&submit=submit'.format(tref))

    def test_gramet_image_from_sample(self):
        filepath = DATADIR + '/ogimet_sample.html'
        with io.open(filepath, 'r', encoding="utf-8") as f:
            image_src, ogimet_serverid = get_gramet_image_url(f)
        self.maxDiff = None
        self.assertEqual(
            image_src,
            'http://www.ogimet.com'
            '/tmp/gramet_20170206122359_2017020600_43296_VOBI_'
            '43109_OIZJ_40851_OITZ_OITK_LTCE_17030_15499_'
            '15324_12851_11659_10671_LFPG_2017020612_2017020622.png')

    @online
    def test_gramet_image_from_ogimet(self):
        filepath = DATADIR + '/AF191_VOBL-LFPG_30Dec2016_21:50z_OFP_20_0_1.txt'
        with open(filepath, 'r') as f:
            ofp = OFP(f.read())
        url, _, _ = ogimet_url_and_route_and_tref(ofp)
        image_src, ogimet_serverid = get_gramet_image_url(url)
        self.assertTrue(image_src)
        self.assertEqual(image_src[-4:], '.png')
        self.assertEqual(image_src[0:22], 'http://www.ogimet.com/')
